#!/bin/bash

$STOS_HOME=/home/stos/STOS

echo Starting stos daemon
cd $STOS_HOME/deployment
nix-shell --run "../main.py"
