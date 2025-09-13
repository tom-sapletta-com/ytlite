#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
NC="\033[0m" # No Color

make generate
echo "${GREEN}✅ Content ready! Use 'make upload' to publish${NC}"
