#!/bin/bash

SOURCE_FILE=project/source/app.exe

INPUT_DIR=project/input
OUTPUT_DIR=project/output

TMP_LOG_FILE=tmp_output.log

LOG_FILTERS=(
    "X connection to :99 broken (explicit kill or server shutdown)."
    "0012:err:ole:"
    "000b:fixme:"
    "wine:"
    "Could not find Wine Gecko. HTML rendering will be disabled."
    "0014:err:ole"
)

mkdir $OUTPUT_DIR
touch $TMP_LOG_FILE
grep -v -f <(printf "%s\\n" "${LOG_FILTERS[@]}") $TMP_LOG_FILE

for INPUT_FILE in $INPUT_DIR/*.in; do
    FILE_BASENAME=$(basename "$INPUT_FILE" .in)
    OUTPUT="${OUTPUT_DIR}/${FILE_BASENAME}.out"
    touch $OUTPUT
    echo "Uruchamianie dla $INPUT_FILE, zapis wyjścia do $OUTPUT"
    start_time=$(date +%s)
    xvfb-run wine64 $SOURCE_FILE < "$INPUT_FILE" > $OUTPUT 2>&1
    end_time=$(date +%s)
    elapsed_time=$(($end_time - $start_time))
    echo "Czas wykonania: $elapsed_time" >> $OUTPUT
done

rm $TMP_LOG_FILE
