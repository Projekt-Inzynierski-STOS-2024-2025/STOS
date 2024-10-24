#!/bin/bash

cpu=$(nproc)

ram=$(free -h | awk '/^Mem:/ {print $2}')

sed -i "/^TOTAL_CPU=/c\TOTAL_CPU=$cpu" .env
sed -i "/^TOTAL_RAM=/c\TOTAL_RAM=$ram" .env