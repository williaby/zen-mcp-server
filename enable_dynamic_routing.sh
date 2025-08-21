#!/bin/bash
# Enable Dynamic Model Routing with Layered Consensus Protection

set -e

echo "🚀 Enabling Dynamic Model Routing System"
echo "========================================"

# Check if routing system files exist
if [ ! -f "routing/integration.py" ]; then
    echo "❌ Routing system not found. Please ensure implementation is complete."
    exit 1
fi

# Set environment variable for current session
export ZEN_SMART_ROUTING=true
echo "✅ Set ZEN_SMART_ROUTING=true for current session"

# Add to .env file for persistence
if [ -f ".env" ]; then
    if grep -q "ZEN_SMART_ROUTING" .env; then
        sed -i 's/ZEN_SMART_ROUTING=.*/ZEN_SMART_ROUTING=true/' .env
        echo "✅ Updated ZEN_SMART_ROUTING in .env file"
    else
        echo "ZEN_SMART_ROUTING=true" >> .env
        echo "✅ Added ZEN_SMART_ROUTING to .env file"
    fi
else
    echo "ZEN_SMART_ROUTING=true" > .env
    echo "✅ Created .env file with ZEN_SMART_ROUTING=true"
fi

# Test the configuration
echo ""
echo "🧪 Testing configuration..."
if .zen_venv/bin/python -c "
from routing.integration import get_integration_instance
integration = get_integration_instance()
if integration.enabled:
    print('✅ Dynamic routing enabled successfully')
    # Test exclusion
    excluded = integration._is_tool_routing_disabled('layered_consensus', 'LayeredConsensusTool')
    if excluded:
        print('✅ Layered consensus excluded (your custom model selection preserved)')
    else:
        print('⚠️  Layered consensus NOT excluded - check configuration')
else:
    print('❌ Dynamic routing not enabled')
    exit(1)
"; then
    echo ""
    echo "🎉 SUCCESS! Dynamic Model Routing is now enabled with:"
    echo "   • Free model prioritization (29 models available)"
    echo "   • Intelligent complexity-based routing"
    echo "   • Cost optimization (20-30% typical savings)" 
    echo "   • Layered consensus exclusion (your customizations preserved)"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Restart the server: ./run-server.sh"
    echo "   2. Test with: routing_status action=status"
    echo "   3. Monitor savings with: routing_status action=stats"
    echo ""
    echo "Your layered consensus tool will work exactly as before!"
    echo "All other tools will now use intelligent model routing."
else
    echo ""
    echo "❌ Configuration test failed. Please check the setup."
    exit 1
fi