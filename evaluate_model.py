#!/usr/bin/env python3
"""
CLI tool for evaluating AI models from OpenRouter URLs

This tool uses the Model Evaluator to analyze new models and determine
if they should be added to the Zen MCP Server model collection.

Usage:
    python evaluate_model.py <openrouter_url>
    
Example:
    python evaluate_model.py https://openrouter.ai/ai21/jamba-large-1.7
"""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools.custom.model_evaluator import ModelEvaluator

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Evaluate AI models from OpenRouter URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s https://openrouter.ai/ai21/jamba-large-1.7
    %(prog)s https://openrouter.ai/openai/gpt-5
    %(prog)s https://openrouter.ai/anthropic/claude-opus-4.1
        """
    )
    
    parser.add_argument(
        'url',
        help='OpenRouter model URL to evaluate'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--csv-only',
        action='store_true',
        help='Only output CSV entry if recommended for addition'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"🔍 Initializing Model Evaluator...")
        
        evaluator = ModelEvaluator()
        
        if args.verbose:
            print(f"📍 Evaluating model from: {args.url}")
        
        # Perform the evaluation
        model_metrics, recommendation = evaluator.evaluate_model_from_url(args.url)
        
        if args.csv_only:
            # Only output CSV if recommended
            if recommendation.should_replace:
                csv_entry = evaluator.generate_csv_entry(model_metrics)
                print(csv_entry)
            else:
                print("# Model not recommended for addition")
                sys.exit(1)
        else:
            # Full evaluation report
            evaluator.print_evaluation_report(model_metrics, recommendation)
        
    except KeyboardInterrupt:
        print("\n❌ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error evaluating model: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()