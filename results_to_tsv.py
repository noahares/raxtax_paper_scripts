#!/usr/bin/env python

"""
Usage:
  results_to_tsv  -k <STR>

Options:
  -h, --help                show help.
  -k, --kingdom <STR>       Taxonomic Kingdom (e.g Fungi, Animalia etc)
"""


import re
from docopt import docopt

def raxtax_2_tsv(raxtax_out):
    """Parse raxtax output"""
    res = {}
    with open(raxtax_out, "r", encoding = "UTF-8") as f:
        for line in f:
            elems = line.rstrip().split("\t")
            if elems[0] not in res:
                res[elems[0]] = "\t".join(elems[1:15])
    return res

def sintax_2_tsv(sintax_out):
    """Parse sintax output"""
    res = {}
    with open(sintax_out, "r", encoding = "UTF-8") as f:
        for line in f:
            elems = line.rstrip().split("\t")
            tax_list = []
            if len(elems)>2:
                lineage = elems[1].split(",")
                for t in lineage:
                    t = t.replace(")","").replace("(","\t")
                    tax_list.append(t)
            else:
                tax_list = ["NA"] * 14
            res[elems[0]] = "\t".join(tax_list)
    return res

def rdp_2_tsv(rdp_out):
    """Parse rdp output"""
    res = {}
    with open(rdp_out, "r", encoding = "UTF-8") as f:
        for line in f:
            elems = line.rstrip().split("\t")
            i = 2
            tax_list = []
            while i<len(elems):
                tax_list.append(elems[i])
                tax_list.append(elems[i+2])
                i += 3
            res[elems[0]] = "\t".join(tax_list)
    return res

def bayesant_2_tsv(bayesant_out,kingdom):
    """Parse bayesant output"""
    f_res = {}
    res = {}
    with open(bayesant_out, "r", encoding = "UTF-8") as f:
        for line in f:
            elems = line.rstrip().split()
            if len(elems)>1:
                if elems[0] not in res:
                    res[elems[0]] = {}
                    res[elems[0]]["tax"] = []
                    res[elems[0]]["conf"] = []
                if re.search('[a-zA-Z]', elems[1]):
                    res[elems[0]]["tax"].append(elems[1])
                else:
                    elems[1] = str(round(float(elems[1]), 2))
                    res[elems[0]]["conf"].append(elems[1])

    for q in res:
        tax_list = [f"k:{kingdom}", "1.00"]
        for t,c in zip(res[q]["tax"],res[q]["conf"]):
            tax_list.append(t)
            tax_list.append(str(c))
        f_res[q] = "\t".join(tax_list)
    return f_res

def idtaxa_2_tsv(idtaxa_out):
    """Parse idtaxa output"""
    f_res = {}
    res = {}
    taxa = 0
    with open(idtaxa_out, "r", encoding = "UTF-8") as f:
        for line in f:
            l = line.rstrip()
            if l.endswith("taxon"):
                taxa = 1
                q = l
                q = l.replace("$`","").replace("`$taxon","")
                res[q] = {}
                res[q]["tax"] = []
                res[q]["conf"] = []
            if l.startswith("["):
                el = l.split()
                if taxa:
                    for e in el:
                        if "[" not in e:
                            res[q]["tax"].append(e.replace("\"",""))
                else:
                    for e in el:
                        if "[" not in e and "Taxa" not in e and "Test" not in e:
                            e = float(e)/100
                            e = str(round(e, 2))
                            res[q]["conf"].append(e)
            if l.endswith("confidence"):
                taxa = 0

    for q in res:
        tax_list = []
        if "unclassified_Root" in res[q]["tax"]:
            tax_list = ["NA"] * 14
        else:
            if len(res[q]["tax"]) < 8:
                k = len(res[q]["tax"])
                while k < 8:
                    res[q]["tax"].append("NA")
                    res[q]["conf"].append("NA")
                    k += 1
            for t,c in zip(res[q]["tax"],res[q]["conf"]):
                if t != "Root":
                    tax_list.append(t)
                    tax_list.append(str(c))
        f_res[q] = "\t".join(tax_list)
    return f_res

def write_res_tsv(fileo, res):
    """Write tsv results for each program used"""
    with open(fileo, "w", encoding = "UTF-8") as f:
        for a,b in res.items():
            f.write(f"{a}\t{b}\n")

def main():
    """ Parse program results and produce tsv files"""
    args = docopt(__doc__)
    kingdom = args['--kingdom']

    raxtax_out = "rx/raxtax.tsv"
    raxtax_res = "raxtax_res.tsv"

    sintax_out = "sintax.out"
    sintax_res = "sintax_res.tsv"

    rdp_out = "rdp.out"
    rdp_res = "rdp_res.tsv"

    bayesant_out = "bayesant.out"
    bayesant_res = "bayesant_res.tsv"

    idtaxa_out = "idtaxa.out"
    idtaxa_res = "idtaxa_res.tsv"

    # RaxTax to Tsv
    write_res_tsv(raxtax_res, raxtax_2_tsv(raxtax_out))

    # SinTax to Tsv
    write_res_tsv(sintax_res, sintax_2_tsv(sintax_out))

    # Rdp to TSV
    write_res_tsv(rdp_res, rdp_2_tsv(rdp_out))

    # BayesANT to tsv
    write_res_tsv(bayesant_res, bayesant_2_tsv(bayesant_out,kingdom))

    # IDTAXA to tsv
    write_res_tsv(idtaxa_res, idtaxa_2_tsv(idtaxa_out))


if __name__ == '__main__':
    main()
