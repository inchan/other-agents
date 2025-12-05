#!/bin/bash

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to find Python 3.10+
find_python() {
  local python_paths=(
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "python3.14"
    "python3.13"
    "python3.12"
    "python3.11"
    "python3.10"
    "python3"
  )

  for cmd in "${python_paths[@]}"; do
    if command -v "$cmd" &> /dev/null; then
      version=$("$cmd" --version 2>&1 | awk '{print $2}')
      major=$(echo "$version" | cut -d. -f1)
      minor=$(echo "$version" | cut -d. -f2)
      if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

echo "🔍 Checking Python version..."
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
  echo "❌ Error: Python 3.10 or higher is required."
  echo "Please install Python 3.10+ using:"
  echo "  brew install python@3.11"
  exit 1
fi

PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION at $PYTHON_CMD"

# Setup virtual environment if not exists
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  "$PYTHON_CMD" -m venv venv
fi

# Check if pytest is installed
if ! ./venv/bin/python -m pytest --version &> /dev/null; then
  echo "📥 Installing development dependencies..."
  ./venv/bin/pip install --upgrade pip -q
  ./venv/bin/pip install -e ".[dev]" -q
  echo "✅ Dependencies installed"
fi

echo ""
echo "🧪 Running tests with coverage (parallel execution with pytest-xdist)..."
echo ""

# CPU 코어 수 감지
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  CPU_COUNT=$(sysctl -n hw.ncpu)
else
  # Linux
  CPU_COUNT=$(nproc)
fi

echo "🔧 Using $CPU_COUNT CPU cores for parallel execution"
echo ""

# Run tests with coverage and parallel execution
# -n auto: CPU 코어 수만큼 자동으로 워커 생성
./venv/bin/pytest -v --cov=src/other_agents_mcp --cov-report=term-missing -n auto

echo ""
echo "✅ Test execution completed"
