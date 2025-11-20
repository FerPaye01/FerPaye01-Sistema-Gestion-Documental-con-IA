#!/bin/bash
# Test runner script for SGD UGEL Ilo
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SGD UGEL ILO - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-asyncio"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    "unit")
        echo -e "${YELLOW}Running unit tests only...${NC}"
        pytest -m "unit" tests/
        ;;
    
    "integration")
        echo -e "${YELLOW}Running integration tests (requires all services)...${NC}"
        echo -e "${YELLOW}Make sure Docker services are running: docker-compose up -d${NC}"
        echo ""
        pytest -m "integration" tests/
        ;;
    
    "fast")
        echo -e "${YELLOW}Running fast tests only (excluding slow tests)...${NC}"
        pytest -m "not slow" tests/
        ;;
    
    "smoke")
        echo -e "${YELLOW}Running smoke tests...${NC}"
        pytest -m "smoke" tests/
        ;;
    
    "all")
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/
        ;;
    
    "coverage")
        echo -e "${YELLOW}Running tests with coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term tests/
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    "verbose")
        echo -e "${YELLOW}Running all tests with verbose output...${NC}"
        pytest -vv tests/
        ;;
    
    "help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  unit         - Run only unit tests (fast, isolated)"
        echo "  integration  - Run only integration tests (requires services)"
        echo "  fast         - Run all tests except slow ones"
        echo "  smoke        - Run smoke tests only"
        echo "  all          - Run all tests (default)"
        echo "  coverage     - Run tests with coverage report"
        echo "  verbose      - Run tests with verbose output"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests"
        echo "  ./run_tests.sh fast               # Run fast tests only"
        echo "  ./run_tests.sh integration        # Run integration tests"
        echo "  ./run_tests.sh coverage           # Generate coverage report"
        exit 0
        ;;
    
    *)
        echo -e "${RED}Unknown option: $TEST_TYPE${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All tests passed! ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Some tests failed! ✗${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
