#!/bin/bash
#
#SBATCH --job-name=grnt_prs
#SBATCH --output=parse_grants.out
#
#SBATCH --partition=hlwill
#SBATCH --time=7-00:00:00
#SBATCH --mem=0
#SBATCH --cpus-per-task=23
#
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gsmoore@stanford.edu

module load python/3.6.1

OAK="/oak/stanford/groups/hlwill"
TEMP="$SCRATCH/sponsorships_temp"
ZIP_DIR="$OAK/raw/USPTO_grants/data"
DTDS="$OAK/raw/USPTO_grants/python/patent_processor/config/grants/DTDs"
OUTPUT="output/grants"

rm -r $TEMP
rm -r $OUTPUT

mkdir $TEMP
mkdir $OUTPUT

# 2001-2005
for i in $ZIP_DIR/pg*.zip; do unzip "$i" -x *.sgm -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-grants.2002-2004.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

# 2005-2006
for i in $ZIP_DIR/ipg05*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-grants.2005.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2006-2013
for i in $ZIP_DIR/ipg0[6-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipg1[0-2]*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-grants.2006-20130108.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2013-present
for i in $ZIP_DIR/ipg1[3-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipg2*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-grants.20130115+.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

