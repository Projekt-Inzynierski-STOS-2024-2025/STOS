#!/bin/bash

SOURCE_FILE=project/main.cpp

OUTPUT_FILE=app.exe

OUTPUT_LOG=project/output.txt

TMP_LOG_FILE=tmp_output.log

LOG_FILTERS=(
    "X connection to :99 broken (explicit kill or server shutdown)."
    "0012:err:ole:"
    "000b:fixme:"
    "wine:"
    "Could not find Wine Gecko. HTML rendering will be disabled."
)

x86_64-w64-mingw32-g++ $SOURCE_FILE -static-libstdc++ -static-libgcc -o $OUTPUT_FILE 

if [ $? -eq 0 ]; then
    echo "Kompilacja zakończona sukcesem. Uruchamianie programu i zapis wyjścia do pliku $OUTPUT_LOG ..."

    xvfb-run wine64 $OUTPUT_FILE > $TMP_LOG_FILE 2>&1

    grep -v -f <(printf "%s\n" "${LOG_FILTERS[@]}") $TMP_LOG_FILE > $OUTPUT_LOG

    rm $TMP_LOG_FILE
    rm $OUTPUT_FILE
else
    echo "Błąd kompilacji."
    exit 1
fi