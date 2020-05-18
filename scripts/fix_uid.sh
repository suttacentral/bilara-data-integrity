#!/usr/bin/env bash
# Replace wrong CS UIDs with the corrected one.
# Input: Csv, two column: bad_uid, good_uid
# Usage: Copy script and the 'fixed_uid.csv' files to 'bilary-data', run it & commit.

CSV_FILENAME='fixed_uid.csv'
FILE_PATTERN="*.json"
# Fix CRLF
sed -i "s/\r//g" "${CSV_FILENAME}"

while IFS=, read -r in_uid out_uid; do
    FILES=$(grep "${in_uid}" -Rl --include="${FILE_PATTERN}" *)
    [[ -z "${FILES}" ]] && echo "No uid matched for ${in_uid}" >&2
    for f in ${FILES}; do
        echo "** Replacing ${in_uid} in $f"
        sed -i "s/${in_uid}\"/${out_uid}\"/g" "${f}"
    done
done < "${CSV_FILENAME}"
