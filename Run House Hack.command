#!/bin/bash

cd "$(dirname "$0")"
mkdir -p reports data/raw data/processed

echo "======================================"
echo " Whitestown House-Hack Radar"
echo "======================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Please install Python 3 first, then run this file again."
  echo
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "First run: creating the Python environment..."
  python3 -m venv .venv || exit 1
fi

source .venv/bin/activate

echo "Checking required packages..."
python -m pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Could not install the required packages. Check your internet connection."
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

if [ ! -f ".env" ] || ! grep -qE '^RENTCAST_API_KEY=.+$' .env; then
  echo
  echo "First-time setup: paste your RentCast API key below."
  echo "It will be saved only in the local .env file and is ignored by GitHub."
  read -s -p "RentCast API key: " RENTCAST_KEY
  echo
  printf 'RENTCAST_API_KEY=%s\n' "$RENTCAST_KEY" > .env
fi

echo
echo "Searching Whitestown listings and calculating deals..."
python -m src.main
STATUS=$?

echo
if [ $STATUS -eq 0 ]; then
  echo "Done. Opening the reports folder..."
  open reports
else
  echo "The run did not finish successfully. Leave this window open and send me a screenshot of the error."
fi

echo
read -n 1 -s -r -p "Press any key to close this window..."
