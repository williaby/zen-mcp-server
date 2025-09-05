#!/bin/bash

# Preserve Dynamic Routing - Upstream Pull Protection Script
# ===========================================================
# This script ensures dynamic routing survives upstream pulls by:
# 1. Backing up current routing integration
# 2. Applying plugin-based architecture 
# 3. Verifying routing functionality after pulls

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"  
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to backup current routing state
backup_routing() {
    print_info "Creating routing backup..."
    
    # Create backup directory
    mkdir -p backups/routing-$(date +%Y%m%d-%H%M%S)
    local backup_dir="backups/routing-$(date +%Y%m%d-%H%M%S)"
    
    # Backup routing files
    if [[ -d "routing/" ]]; then
        cp -r routing/ "$backup_dir/"
        print_success "Routing directory backed up"
    fi
    
    if [[ -d "tools/routing_status.py" ]]; then
        cp tools/routing_status.py "$backup_dir/"
        print_success "Routing status tool backed up"
    fi
    
    if [[ -d "plugins/" ]]; then
        cp -r plugins/ "$backup_dir/"
        print_success "Plugins directory backed up"
    fi
    
    echo "$backup_dir" > .last_routing_backup
    print_success "Backup created at: $backup_dir"
}

# Function to verify routing is working
verify_routing() {
    print_info "Verifying dynamic routing functionality..."
    
    # Check if routing files exist
    if [[ ! -d "routing/" ]]; then
        print_error "Routing directory missing"
        return 1
    fi
    
    if [[ ! -f "plugins/dynamic_routing_plugin.py" ]]; then
        print_error "Dynamic routing plugin missing"
        return 1
    fi
    
    # Test routing system
    if ZEN_SMART_ROUTING=true python -c "
import sys
sys.path.append('.')
try:
    from plugins.dynamic_routing_plugin import DynamicRoutingPlugin
    plugin = DynamicRoutingPlugin()
    success = plugin.initialize()
    print('✅ Dynamic routing plugin test:', 'PASSED' if success else 'FAILED')
    exit(0 if success else 1)
except Exception as e:
    print(f'❌ Dynamic routing test FAILED: {e}')
    exit(1)
"; then
        print_success "Dynamic routing verification PASSED"
        return 0
    else
        print_error "Dynamic routing verification FAILED"
        return 1
    fi
}

# Function to restore from backup if needed
restore_routing() {
    if [[ -f ".last_routing_backup" ]]; then
        local backup_dir=$(cat .last_routing_backup)
        if [[ -d "$backup_dir" ]]; then
            print_info "Restoring routing from backup: $backup_dir"
            
            # Restore routing files
            if [[ -d "$backup_dir/routing" ]]; then
                cp -r "$backup_dir/routing" ./
                print_success "Routing directory restored"
            fi
            
            if [[ -f "$backup_dir/routing_status.py" ]]; then
                cp "$backup_dir/routing_status.py" tools/
                print_success "Routing status tool restored"
            fi
            
            if [[ -d "$backup_dir/plugins" ]]; then
                cp -r "$backup_dir/plugins" ./
                print_success "Plugins directory restored"
            fi
            
            return 0
        fi
    fi
    
    print_error "No backup found to restore from"
    return 1
}

# Main execution
case "${1:-verify}" in
    "backup")
        backup_routing
        ;;
    "verify")
        if ! verify_routing; then
            print_error "Routing verification failed"
            exit 1
        fi
        ;;
    "restore")
        if ! restore_routing; then
            print_error "Routing restoration failed"
            exit 1
        fi
        verify_routing
        ;;
    "full-check")
        backup_routing
        if ! verify_routing; then
            print_error "Attempting restoration..."
            restore_routing
            verify_routing
        fi
        ;;
    *)
        echo "Usage: $0 {backup|verify|restore|full-check}"
        echo "  backup     - Create backup of current routing setup"
        echo "  verify     - Verify routing is working correctly"
        echo "  restore    - Restore routing from last backup"
        echo "  full-check - Backup, verify, and restore if needed"
        exit 1
        ;;
esac

print_success "Dynamic routing protection complete!"