#!/bin/bash

# test a few basic test cases for the stockfish container

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

START_FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# Position where White can deliver mate in 1 with Qxf7
MATE_FEN="r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5Q2/PPPP1PPP/RNB1K2R w KQkq - 4 4"

echo "Starting Chess-Analyzer Integration Tests..."

# Test 1: Standard Position Analysis
echo -n "Test 1: Validating Standard Opening... "
OUTPUT=$(docker run --rm stockfish-analyzer "$START_FEN" "e4, e5" 10)
if echo "$OUTPUT" | grep -q "\"final_rating\""; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Output: $OUTPUT"
    exit 1
fi

# Test 2: Checkmate Detection (M1)
echo -n "Test 2: Validating Checkmate Detection... "
MATE_OUTPUT=$(docker run --rm stockfish-analyzer "$MATE_FEN" "Qxf7" 10)
if echo "$MATE_OUTPUT" | grep -q "\"rating\": \"M0\""; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED (Expected M1 rating)${NC}"
    echo "Output: $MATE_OUTPUT"
    exit 1
fi

# Test 3: Invalid Move Handling
echo -n "Test 3: Validating Error Handling... "
ERROR_OUTPUT=$(docker run --rm stockfish-analyzer "$START_FEN" "NotAMove" 5)
if echo "$ERROR_OUTPUT" | grep -q "Invalid move"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Output: $ERROR_OUTPUT"
    exit 1
fi

echo -e "\n${GREEN}All tests passed successfully!${NC}"