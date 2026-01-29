#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Color definitions for better visibility
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting automated refactoring workflow...${NC}"

# --- Step 1: Code Formatting ---
echo -e "${BLUE}[1/4] Running clang-format for indentation and layout...${NC}"
find src \( -name "*.cpp" -o -name "*.hpp" -o -name "*.h" \) -print0 | xargs -0 clang-format -i
echo -e "${GREEN}Formatting completed.${NC}"

# --- Step 2: Regenerate CMake Configuration ---
echo -e "${BLUE}[2/4] Configuring CMake and generating compile_commands.json...${NC}"
mkdir -p build
cmake -S . -B build \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
      -DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON
echo -e "${GREEN}CMake configuration completed.${NC}"

# --- Step 3: Compilation Check (The Guard) ---
echo -e "${BLUE}[3/4] Verifying build integrity before refactoring...${NC}"
if ! cmake --build build --parallel $(nproc); then
    echo -e "${RED}Error: Compilation failed. Clang-tidy will not run on broken code.${NC}"
    echo -e "${RED}Please fix the compiler errors (e.g., missing includes) and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Compilation check passed.${NC}"

# --- Step 4: Clang-Tidy Fixes ---
echo -e "${BLUE}[4/4] Running clang-tidy for static analysis and auto-fixes...${NC}"
# We use -p build to locate the compilation database
find src -name "*.cpp" -print0 | xargs -0 clang-tidy -p build --fix --quiet

echo -e "${GREEN}Success! All refactoring steps completed.${NC}"
echo -e "${BLUE}Tip: Run 'git diff' to review changes before committing.${NC}"