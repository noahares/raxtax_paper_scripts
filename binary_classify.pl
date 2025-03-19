#!/usr/bin/env perl

sub print_bin_classification {
	my ($r, $l, $t_l, $c, $u) = @_;

	print "$r\t$l\t$t_l\t$c\t";
	
	if ($l eq $t_l) {
		print "TP\n";
	}
	else {
		if ($t_l eq "NA") {
			if ($u>0) {
				print "FN\n";
			}
			else {
				print "TN\n";
			}
		}
		else {
			if ($u>0) {
				print "MC\n";
			}
			else {
				print "FP\n";
			}			
		}
	}
}


use warnings;
use strict;



my %pr;
open I, $ARGV[0];
while (my $line = <I> ) {
	chomp($line);
	my @p = split(/\t/,$line);
	$pr{$p[0]}=$p[1];
}

close I;

open F, $ARGV[1];
my %c;
my $i = 0;
while (my $line = <F> ) {
	chomp($line);
	my @p = split(/\t/,$line);
	my $orig = $p[0];
	my @ori = split(/=/,$orig);
	my @o = split(/,/,$ori[1]);

	my $ki = $o[0];
	my $ph = $o[1];
	my $cl = $o[2];
	my $or = $o[3];
	my $fa = $o[4];
	my $ge = $o[5];
	my $sp = $o[6];
	$sp =~ s/\;//;

	my $t_ki = $p[1];
	my $t_ki_c = $p[2];

	my $t_ph = $p[3];
	my $t_ph_c = $p[4];
	
	my $t_cl = $p[5];
	my $t_cl_c = $p[6];
	
	my $t_or = $p[7];
	my $t_or_c = $p[8];
	
	my $t_fa = $p[9];
	my $t_fa_c = $p[10];
	
	my $t_ge = $p[11];
	my $t_ge_c = $p[12];
	
	my $t_sp = $p[13];
	my $t_sp_c = $p[14];

	print_bin_classification("k", $ki, $t_ki, $t_ki_c, $pr{$ki});
	print_bin_classification("p", $ph, $t_ph, $t_ph_c, $pr{$ph});
	print_bin_classification("c", $cl, $t_cl, $t_cl_c, $pr{$cl});
	print_bin_classification("o", $or, $t_or, $t_or_c, $pr{$or});
	print_bin_classification("f", $fa, $t_fa, $t_fa_c, $pr{$fa});
	print_bin_classification("g", $ge, $t_ge, $t_ge_c, $pr{$ge});
	print_bin_classification("s", $sp, $t_sp, $t_sp_c, $pr{$sp});	

}

