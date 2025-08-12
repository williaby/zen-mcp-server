#!/usr/bin/env python3
"""
Test script for the Model Evaluator tool
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools.custom.model_evaluator import ModelEvaluator

def test_model_evaluation():
    """Test the model evaluator with the example URL"""
    
    print("🚀 Testing Model Evaluator with AI21 Jamba Large 1.7")
    print("=" * 60)
    
    try:
        # Initialize the evaluator
        evaluator = ModelEvaluator()
        print("✅ Model evaluator initialized successfully")
        
        # Test URL
        test_url = "https://openrouter.ai/ai21/jamba-large-1.7"
        print(f"📍 Evaluating URL: {test_url}")
        
        # Perform evaluation
        model_metrics, recommendation = evaluator.evaluate_model_from_url(test_url)
        
        # Print the comprehensive report
        evaluator.print_evaluation_report(model_metrics, recommendation)
        
        print("\n✅ Model evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_model_evaluation()
    sys.exit(0 if success else 1)