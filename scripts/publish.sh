#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
NC="\033[0m" # No Color

make generate shorts
echo "${GREEN}✅ Content ready! Use 'make upload' to publish${NC}"
