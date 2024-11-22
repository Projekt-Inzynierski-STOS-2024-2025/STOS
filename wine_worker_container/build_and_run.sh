#!/bin/bash

SOURCE_FILE=project/source/main.cpp

INPUT_DIR=project/input

OUTPUT_DIR=project/output

OUTPUT_FILE=app.exe

TMP_LOG_FILE=tmp_output.log

LOG_FILTERS=(
    "X connection to :99 broken (explicit kill or server shutdown)."
    "0012:err:ole:"
    "000b:fixme:"
    "wine:"
    "Could not find Wine Gecko. HTML rendering will be disabled."
    "0014:err:ole"
)

x86_64-w64-mingw32-g++ $SOURCE_FILE -static-libstdc++ -static-libgcc -o $OUTPUT_FILE 

if [ $? -eq 0 ]; then
    echo "Kompilacja zakończona sukcesem. Uruchamianie programu dla każdego pliku wejściowego..."
    OUTPUT_LOG="${OUTPUT_DIR}/1.out"
    mkdir $OUTPUT_DIR
    grep -v -f <(printf "%s\\n" "${LOG_FILTERS[@]}") $TMP_LOG_FILE

    for INPUT_FILE in $INPUT_DIR/*.in; do
        FILE_BASENAME=$(basename "$INPUT_FILE" .in)
        OUTPUT_LOG="${OUTPUT_DIR}/${FILE_BASENAME}.out"
        touch $OUTPUT_LOG
        echo "Uruchamianie dla $INPUT_FILE, zapis wyjścia do $OUTPUT_LOG"
        start_time=$(date +%s)
        xvfb-run wine64 $OUTPUT_FILE < "$INPUT_FILE" > $TMP_LOG_FILE 2>&1
        end_time=$(date +%s)
        elapsed_time=$(($end_time - $start_time))
        echo "Czas wykonania: $elapsed_time"
        grep -v -f <(printf "%s\\n" "${LOG_FILTERS[@]}") $TMP_LOG_FILE > $OUTPUT_LOG
    done

    rm $TMP_LOG_FILE
    rm $OUTPUT_FILE
else
    echo "Błąd kompilacji."
    exit 1
fi