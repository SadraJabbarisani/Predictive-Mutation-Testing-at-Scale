#!/usr/bin/env bash
# One-time environment setup (Ubuntu / Google Colab). Java + Maven only needed to (re)collect PIT data.
set -e
pip install -q -r requirements.txt
if ! command -v java >/dev/null; then sudo apt-get -qq update && sudo apt-get -qq install -y openjdk-17-jdk-headless; fi
if ! command -v mvn  >/dev/null; then sudo apt-get -qq install -y maven; fi
java -version 2>&1 | head -1; mvn -v 2>&1 | head -1; python3 -c "import xgboost, lightgbm, sklearn; print('python deps ok')"
