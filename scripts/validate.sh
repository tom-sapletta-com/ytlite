#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# Set Python command to use virtual environment
PYTHON_CMD="/home/tom/github/tom-sapletta-com/ytlite/venv/bin/python3"

# Function to validate data
validate_data() {
  echo "$(tput setaf 3)Validating data...$(tput sgr0)"
  $PYTHON_CMD /home/tom/github/tom-sapletta-com/ytlite/src/validator.py validate_data --detailed
  if [ $? -eq 0 ]; then
    echo "$(tput setaf 2) Data validation completed$(tput sgr0)"
  else
    echo "$(tput setaf 1) Data validation failed. Check logs for details.$(tput sgr0)"
    if [ -f output/validation_report.json ]; then
      cat output/validation_report.json | jq '.'
    else
      echo "No validation report found."
    fi
    exit 1
  fi
}

# Function to validate app
validate_app() {
  echo "$(tput setaf 3)Validating app...$(tput sgr0)"
  $PYTHON_CMD /home/tom/github/tom-sapletta-com/ytlite/src/validator.py validate_app --detailed
  if [ $? -eq 0 ]; then
    echo "$(tput setaf 2) App validation completed$(tput sgr0)"
  else
    echo "$(tput setaf 1) App validation failed. Check logs for details.$(tput sgr0)"
    if [ -f output/validation_report.json ]; then
      cat output/validation_report.json | jq '.'
    else
      echo "No validation report found."
    fi
    exit 1
  fi
}

echo "${YELLOW} Validating generated videos...${NC}"
$PYTHON_CMD -c "
from src.validator import validate_all_videos
validate_all_videos()
"
echo "${GREEN} Validation complete${NC}"
validate_data
validate_app
