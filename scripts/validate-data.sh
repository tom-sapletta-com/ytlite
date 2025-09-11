#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${YELLOW}📦 Validating generated data in output/projects/...${NC}"
python3 -u src/data_validator.py --projects-root output/projects --report output/validate_data.json --write-per-project
RC=$?
if [ $RC -eq 0 ]; then
  echo -e "${GREEN}✓ Data integrity OK${NC}"
else
  echo -e "${RED}✗ Data integrity issues found. See output/validate_data.json${NC}"
fi
exit $RC
