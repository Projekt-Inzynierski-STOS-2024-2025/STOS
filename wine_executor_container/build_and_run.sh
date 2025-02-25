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
    "0010:fixme:kernelbase:AppPolicyGetProcessTerminationMethod FFFFFFFA, 0032FEAC"
)

mkdir $OUTPUT_DIR
touch $TMP_LOG_FILE

for INPUT_FILE in $INPUT_DIR/*.in; do
    FILE_BASENAME=$(basename "$INPUT_FILE" .in)
    OUTPUT="${OUTPUT_DIR}/${FILE_BASENAME}.out"
    touch $OUTPUT
    echo "Running $INPUT_FILE -> $OUTPUT"
    START_TIME=$(date +%s)
    xvfb-run wine64 $SOURCE_FILE < "$INPUT_FILE" > $TMP_LOG_FILE 2>&1
    END_TIME=$(date +%s)
    ELAPSED_TIME=$(($END_TIME - $START_TIME))
    echo "$ELAPSED_TIME" >> $TMP_LOG_FILE
    grep -v -f <(printf "%s\\n" "${LOG_FILTERS[@]}") $TMP_LOG_FILE > $OUTPUT
done

rm $TMP_LOG_FILE