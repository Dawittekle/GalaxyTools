#!/bin/bash -ue
coordinate_system=$(grep coordinate_system random_name.tsv-meta.yaml | awk -F ":" '{print $2}' | tr -d "[:blank:]" )
if test -z "$coordinate_system"; then coordinate="1-based"; else coordinate=$coordinate_system; fi
from_build=$((grep genome_assembly random_name.tsv-meta.yaml | grep -Eo '[0-9][0-9]') || (echo $(basename random_name.tsv) | grep -Eo '[bB][a-zA-Z]*[0-9][0-9]' | grep -Eo '[0-9][0-9]'))
[[ -z "$from_build" ]] && { echo "Parameter from_build is empty" ; exit 1; }

map_to_build_nf.py     -f random_name.tsv     -from_build $from_build     -to_build 38     -vcf "/home/dawit/.nextflow/assets/EBISPOT/gwas-sumstats-harmoniser/test_data/homo_sapiens-chr*.parquet"     -chroms "[1, 22]"     -coordinate $coordinate
