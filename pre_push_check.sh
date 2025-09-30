#!/bin/bash

# Pre-Push Verification Script for Knowledge Assistant
# This script checks everything is ready before pushing to production

set -e

echo "🚀 Knowledge Assistant Pre-Push Checklist"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Environment Configuration
echo
echo "🔧 Checking Environment Configuration..."

if [ -f ".env" ]; then
    check_pass "Environment file (.env) exists"
    
    # Check if it contains real values
    if grep -q "your_.*_here" .env; then
        check_fail "Environment file contains placeholder values - update .env with real credentials"
    else
        check_pass "Environment file appears to have real values"
    fi
    
    # Check required variables
    required_vars=("GEMINI_API_KEY" "DATABASE_URL" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env; then
            check_pass "$var is configured"
        else
            check_fail "$var is missing from .env"
        fi
    done
else
    check_fail "Environment file (.env) missing - copy from .env.example"
fi

# 2. Security Checks
echo
echo "🔐 Security Checks..."

if [ -f ".gitignore" ]; then
    check_pass ".gitignore file exists"
    
    if grep -q "\.env" .gitignore; then
        check_pass ".env is in .gitignore"
    else
        check_fail ".env should be in .gitignore"
    fi
    
    if grep -q "uploads/" .gitignore; then
        check_pass "uploads/ directory is in .gitignore"
    else
        check_warn "uploads/ directory should be in .gitignore"
    fi
else
    check_fail ".gitignore file missing"
fi

# Check for sensitive data in tracked files
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git ls-files | xargs grep -l "password\|secret\|key" | grep -v ".py\|.md\|.example" > /dev/null 2>&1; then
        check_warn "Potential sensitive data found in tracked files"
    else
        check_pass "No obvious sensitive data in tracked files"
    fi
fi

# 3. Dependencies
echo
echo "📦 Checking Dependencies..."

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt missing"
fi

if [ -f "requirements-prod.txt" ]; then
    check_pass "requirements-prod.txt exists"
else
    check_warn "requirements-prod.txt missing (recommended for production)"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [ "$(echo "$python_version >= 3.11" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
    check_pass "Python version $python_version is supported"
else
    check_warn "Python version $python_version - recommend 3.11+"
fi

# 4. Docker Configuration
echo
echo "🐳 Docker Configuration..."

if [ -f "Dockerfile" ]; then
    check_pass "Dockerfile exists"
else
    check_warn "Dockerfile missing (recommended for deployment)"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml missing"
fi

if [ -f "docker-compose.prod.yml" ]; then
    check_pass "Production docker-compose file exists"
else
    check_warn "docker-compose.prod.yml missing (recommended for production)"
fi

# 5. Documentation
echo
echo "📚 Documentation Checks..."

if [ -f "README.md" ]; then
    check_pass "README.md exists"
    
    # Check if README has basic sections
    if grep -q "## Features\|## Installation\|## Usage" README.md; then
        check_pass "README.md has basic sections"
    else
        check_warn "README.md could be more comprehensive"
    fi
else
    check_fail "README.md missing"
fi

if [ -f "DEPLOYMENT.md" ]; then
    check_pass "DEPLOYMENT.md exists"
else
    check_warn "DEPLOYMENT.md missing (helpful for production deployment)"
fi

# 6. Code Quality
echo
echo "🧹 Code Quality Checks..."

# Check for common Python issues
if command -v flake8 >/dev/null 2>&1; then
    if flake8 --count --select=E9,F63,F7,F82 --show-source --statistics . >/dev/null 2>&1; then
        check_pass "No critical Python syntax errors"
    else
        check_fail "Python syntax errors found - run 'flake8 .' to see details"
    fi
else
    check_warn "flake8 not installed - cannot check code quality"
fi

# Check for TODO/FIXME comments
if grep -r "TODO\|FIXME\|XXX" --include="*.py" . >/dev/null 2>&1; then
    check_warn "TODO/FIXME comments found - review before production"
else
    check_pass "No TODO/FIXME comments in Python files"
fi

# 7. File Structure
echo
echo "📁 File Structure Checks..."

required_dirs=("app" "routes" "services")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory $dir/ exists"
    else
        check_fail "Directory $dir/ missing"
    fi
done

required_files=(
    "main.py"
    "app/models.py"
    "app/database.py"
    "app/config.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "File $file exists"
    else
        check_fail "File $file missing"
    fi
done

# 8. Testing
echo
echo "🧪 Testing Checks..."

if [ -f "test_system.py" ]; then
    check_pass "System test script exists"
else
    check_warn "test_system.py missing - recommend testing before deployment"
fi

if [ -d "tests/" ]; then
    check_pass "Tests directory exists"
else
    check_warn "tests/ directory missing - recommend unit tests"
fi

# 9. Production Readiness
echo
echo "🚀 Production Readiness..."

if [ -f "generate_secrets.py" ]; then
    check_pass "Secret generation script available"
else
    check_warn "generate_secrets.py missing - create secure secrets manually"
fi

# Check for development-only settings
if grep -r "debug.*=.*True\|DEBUG.*=.*True" --include="*.py" . >/dev/null 2>&1; then
    check_warn "Debug mode enabled - disable for production"
else
    check_pass "No debug mode found in code"
fi

# Final Summary
echo
echo "📊 Pre-Push Summary"
echo "==================="
echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
echo -e "❌ Failed: ${RED}$FAILED${NC}"
echo -e "⚠️  Warnings: ${YELLOW}$WARNINGS${NC}"
echo

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed! Ready for deployment.${NC}"
    else
        echo -e "${YELLOW}✅ Core checks passed with $WARNINGS warnings. Review warnings before production deployment.${NC}"
    fi
    echo
    echo "Next steps:"
    echo "1. Review any warnings above"
    echo "2. Test with: python test_system.py"
    echo "3. Deploy with: docker-compose up -d"
    echo "4. Monitor logs: docker-compose logs -f"
else
    echo -e "${RED}❌ $FAILED critical issues found. Fix these before pushing:${NC}"
    echo
    echo "Common fixes:"
    echo "1. Create .env file: cp .env.example .env"
    echo "2. Add your API keys to .env file"
    echo "3. Generate secrets: python generate_secrets.py"
    echo "4. Add secrets to .env file"
    echo "5. Fix any missing files or directories"
    exit 1
fi