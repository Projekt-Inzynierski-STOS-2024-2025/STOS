#!/bin/bash
echo ------ Checking network 
if ! ping -c 1 -W 5 google.com &> /dev/null; then
    echo "[error] issue with your network/dns"
    exit 1
fi
echo ------ Checking for docker installation 
if ! command -v docker &> /dev/null; then
    echo "[error] docker not present in path"
    exit 1
fi
echo ------ Checking for nix shell installation 
if ! command -v nix-shell &> /dev/null; then
    echo "[error] nix-shell not present in path"
    exit 1
fi
echo ------ Healthcheck was successful 
