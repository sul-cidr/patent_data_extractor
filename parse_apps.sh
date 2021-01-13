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

module load python/3.9.0

module load libxml2
module load libxslt

# Ensure packages are up-to-date
pip3 install --upgrade -r requirements.txt

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

python3 patent_xml_to_csv.py --verbose \
        --xml-input $TEMP/*.{xml,XML} \
        --recurse \
        --config config/uspto-applications.2001-2004.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

# 2005-2006
for i in $ZIP_DIR/ipa05*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py  --verbose \
        --xml-input $TEMP/*.{xml,XML} \
        --recurse \
        --config config/uspto-applications.2005.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2006-2013
for i in $ZIP_DIR/ipa0[6-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipa1[0-3]*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py --verbose \
        --xml-input $TEMP/*.{xml,XML} \
        --recurse \
        --config config/uspto-applications.2006-2013.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
mkdir $TEMP

#2013-present
for i in $ZIP_DIR/ipa1[4-9]*.zip; do unzip "$i" -d $TEMP & done
for i in $ZIP_DIR/ipa2*.zip; do unzip "$i" -d $TEMP & done
wait

python3 patent_xml_to_csv.py --verbose \
        --xml-input $TEMP/*.{xml,XML} \
        --recurse \
        --config config/uspto-applications.2014+.yaml \
        --output-path $OUTPUT \
        --output-type sqlite \
        --dtd-path $DTDS \
        --continue-on-error

rm -r $TEMP
