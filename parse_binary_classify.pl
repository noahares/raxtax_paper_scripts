#!/usr/bin/env perl

use warnings;
use strict;

my $in_file = $ARGV[0];
my $rank = $ARGV[1]; # (p,c,o,f,g,s)

my %tp;
my %fp;
my %fn;
my %tn;
my %mc;
my $i=1;

while ($i < 101) {
	$tp{$i} = 0;
	$fp{$i} = 0;
	$fn{$i} = 0;
	$tn{$i} = 0;
	$mc{$i} = 0;
	$i++;
}

open F, $in_file;
while (my $line = <F> ) {
	chomp($line);
	my @p = split(/\t/,$line);
	if ($p[0] eq $rank) {
		my $c = 100;
		if ($p[3] ne "NA") {
			$c = $p[3]*100;
		}
		

		if ($p[4] eq "TP") {
			$i = 1;
			while ($i<$c+1) {
				$tp{$i}++;
				$i++;
			}
			while ($i<101) {
				$fn{$i}++;
				$i++;
			}			
		}

		if ($p[4] eq "MC") {
			$i = 1;
			while ($i<$c+1) {
				$mc{$i}++;
				$i++;
			}
			while ($i<101) {
				$fn{$i}++;
				$i++;
			}			
		}

		if ($p[4] eq "FP") {
			$i = 1;
			while ($i<$c+1) {
				$fp{$i}++;
				$i++;
			}
			while ($i<101) {
				$tn{$i}++;
				$i++;
			}
			
		}
		if ($p[4] eq "FN") {
			$i = 1;
			while ($i<101) {
				$fn{$i}++;
				$i++;
			}
		}
		if ($p[4] eq "TN") {
			$i = 1;
			while ($i<101) {
				$tn{$i}++;
				$i++;
			}
		}				
	}
}

close F;

$i = 1;
while ($i < 101) {
	my $recall = $tp{$i}/($tp{$i} + $mc{$i} + $fn{$i});
	my $precision = $tp{$i}/($tp{$i} + $fp{$i});
	my $f1 = (2 * $recall * $precision)/($recall + $precision);
	if ($in_file =~ /raxtax/) {
		print "raxtax";
	}
	elsif ($in_file =~ /sintax/) {
		print "sintax";
	}
	elsif ($in_file =~ /rdp/) {
		print "rdp";
	}
	elsif ($in_file =~ /bayesant/) {
		print "bayeasnt";
	}
	elsif ($in_file =~ /idtaxa/) {
		print "idtaxa";
	}	
	print "\t$i";
	print "\t$f1";
	print "\n";
	$i++;
}

