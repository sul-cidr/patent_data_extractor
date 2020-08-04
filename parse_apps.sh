#!/bin/bash
#
#SBATCH --job-name=app_prs
#SBATCH --output=parse_apps.out
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
TEMP="$SCRATCH/app_parse_temp"
ZIP_DIR="$OAK/raw/USPTO_applications/data"
DTDS="$OAK/raw/USPTO_applications/python/patent_processor/config/applications/DTDs"
OUTPUT="output/applications"

rm -r $TEMP
rm -r $OUTPUT

mkdir $TEMP
mkdir $OUTPUT

# 2001-2005
for i in $ZIP_DIR/pa0[1-4]*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-applications-0105.yaml \
        --output-path $OUTPUT \
        --output-type csv \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

# 2005-2006
for i in $ZIP_DIR/ipa05*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-applications-0506.yaml \
        --output-path $OUTPUT \
        --output-type csv \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2006-2013
for i in $ZIP_DIR/ipa0[6-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipa1[0-2]*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config config/uspto-applications-0613.yaml \
        --output-path $OUTPUT \
        --output-type csv \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2013-present
for i in $ZIP_DIR/ipa1[3-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipa2*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py \
        --xml-input $TEMP \
        --recurse \
        --config "config/uspto-applications-13+.yaml" \
        --output-path $OUTPUT \
        --output-type csv \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

