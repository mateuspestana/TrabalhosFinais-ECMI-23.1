#!/bin/bash

# Checa se o python esta instalado
command -v python >/dev/null 2>&1 || { echo >&2 "Python is é necessario porém não esta instalado. Abortando."; exit 1; }

# Checa se o pip esta instalado
command -v pip >/dev/null 2>&1 || { echo >&2 "pip é necessario porém não esta instalado. Abortando."; exit 1; }

# Checa se o Firefox esta installado
command -v firefox >/dev/null 2>&1 || {
  echo >&2 "Firefox não esta instalado. Instalando Firefox..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install --cask firefox
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install firefox
  else
    echo >&2 "Operating system não é supportado. Por favor instale firefox manualmente."
    exit 1
  fi
}

# Install dependencies
pip install -r requirements.txt || { echo >&2 "Failed to install dependencies. Aborting."; exit 1; }

# Start the Streamlit app
streamlit run main.py