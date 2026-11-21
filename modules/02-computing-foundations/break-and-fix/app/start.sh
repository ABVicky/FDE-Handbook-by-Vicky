#!/usr/bin/env bash
# Starts the AdmitFlow status server.
# Expected: the app is available at http://localhost:8800

export PORT=8800

cd "$(dirname "$0")"
python3 server.py
