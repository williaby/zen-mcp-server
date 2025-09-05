#!/bin/bash

# Upgrade Zen MCP Server with Routing Protection
# ===============================================
# Safe upstream pull with automatic routing preservation

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

print_info "🚀 Starting protected upstream upgrade..."

# 1. Backup current routing state
print_info "Creating routing backup..."
./preserve-dynamic-routing.sh backup

# 2. Verify current routing works
print_info "Verifying current routing..."
if ! ./preserve-dynamic-routing.sh verify >/dev/null 2>&1; then
    print_error "Current routing verification failed - aborting upgrade"
    exit 1
fi
print_success "Current routing verified"

# 3. Pull upstream changes
print_info "Pulling upstream changes..."
if git pull upstream main; then
    print_success "Upstream pull successful"
else
    print_error "Upstream pull failed"
    exit 1
fi

# 4. Verify routing still works after pull
print_info "Verifying routing after upgrade..."
if ./preserve-dynamic-routing.sh verify >/dev/null 2>&1; then
    print_success "Routing survived upstream pull!"
else
    print_error "Routing broken after pull - attempting restoration..."
    if ./preserve-dynamic-routing.sh restore; then
        print_success "Routing restored from backup"
        if ./preserve-dynamic-routing.sh verify >/dev/null 2>&1; then
            print_success "Routing verification passed after restore"
        else
            print_error "Routing still broken after restore - manual intervention needed"
            exit 1
        fi
    else
        print_error "Failed to restore routing - manual intervention needed"
        exit 1
    fi
fi

# 5. Test server startup
print_info "Testing server startup..."
if timeout 10 bash -c '
    source .zen_venv/bin/activate
    ZEN_SMART_ROUTING=true python -c "
    import server
    print(\"✅ Server imports successfully with routing\")
    "
' >/dev/null 2>&1; then
    print_success "Server startup test passed"
else
    print_error "Server startup test failed"
    exit 1
fi

# 6. Success summary
print_success "🎉 Upstream upgrade completed successfully!"
print_success "✅ Routing protection: ACTIVE"
print_success "✅ Dynamic routing: PRESERVED" 
print_success "✅ Server functionality: VERIFIED"

echo
print_info "To start the server with dynamic routing:"
echo "  ZEN_SMART_ROUTING=true ./run-server.sh"