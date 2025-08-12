#!/usr/bin/env python3
"""
Test script for the Model Evaluator tool with a premium model
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools.custom.model_evaluator import ModelEvaluator, ModelMetrics

def test_premium_model_evaluation():
    """Test the model evaluator with a simulated premium model"""
    
    print("🚀 Testing Model Evaluator with Simulated Premium Model")
    print("=" * 60)
    
    try:
        # Initialize the evaluator
        evaluator = ModelEvaluator()
        print("✅ Model evaluator initialized successfully")
        
        # Create a simulated premium model that should qualify for replacement
        simulated_model = ModelMetrics(
            name="test/premium-model-v2",
            provider="test",
            humaneval_score=92.0,
            swe_bench_score=85.0,
            mmlu_score=89.0,
            input_cost=3.0,
            output_cost=12.0,
            context_window=500000,
            has_multimodal=True,
            has_vision=True,
            has_coding=True,
            description="Advanced reasoning and coding model with multimodal capabilities",
            openrouter_url="https://openrouter.ai/test/premium-model-v2"
        )
        
        print(f"📍 Evaluating simulated model: {simulated_model.name}")
        
        # Check basic qualification
        meets_requirements = evaluator._meets_basic_qualification(simulated_model)
        print(f"✅ Meets basic requirements: {meets_requirements}")
        
        if meets_requirements:
            # Calculate replacement recommendation
            recommendation = evaluator._calculate_replacement_recommendation(simulated_model)
            
            # Print the comprehensive report
            evaluator.print_evaluation_report(simulated_model, recommendation)
            
            # Show CSV entry that would be generated
            if recommendation.should_replace:
                print(f"\n📄 GENERATED CSV ENTRY:")
                csv_entry = evaluator.generate_csv_entry(simulated_model, rank=1)
                print(csv_entry)
        
        print("\n✅ Model evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_premium_model_evaluation()
    sys.exit(0 if success else 1)