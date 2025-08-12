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

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools.custom.model_evaluator import ModelEvaluator, ModelMetrics


def test_basic_evaluation():
    """Test the model evaluator with AI21 Jamba Large 1.7"""

    print("🚀 Testing Model Evaluator with AI21 Jamba Large 1.7")
    print("=" * 60)

    try:
        evaluator = ModelEvaluator()
        print("✅ Model evaluator initialized successfully")

        test_url = "https://openrouter.ai/ai21/jamba-large-1.7"
        print(f"📍 Evaluating URL: {test_url}")

        model_metrics, recommendation = evaluator.evaluate_model_from_url(test_url)
        evaluator.print_evaluation_report(model_metrics, recommendation)

        print("\n✅ Model evaluation completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_premium_evaluation():
    """Test the model evaluator with a simulated premium model"""

    print("🚀 Testing Model Evaluator with Simulated Premium Model")
    print("=" * 60)

    try:
        evaluator = ModelEvaluator()
        print("✅ Model evaluator initialized successfully")

        # Create simulated premium model
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

        meets_requirements = evaluator._meets_basic_qualification(simulated_model)
        print(f"✅ Meets basic requirements: {meets_requirements}")

        if meets_requirements:
            recommendation = evaluator._calculate_replacement_recommendation(simulated_model)
            evaluator.print_evaluation_report(simulated_model, recommendation)

            if recommendation.should_replace:
                print("\n📄 GENERATED CSV ENTRY:")
                csv_entry = evaluator.generate_csv_entry(simulated_model, rank=1)
                print(csv_entry)

        print("\n✅ Model evaluation completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Evaluate AI models from OpenRouter URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s https://openrouter.ai/ai21/jamba-large-1.7
    %(prog)s https://openrouter.ai/openai/gpt-5
    %(prog)s --test basic
    %(prog)s --test premium
        """
    )

    parser.add_argument(
        'url',
        nargs='?',
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

    parser.add_argument(
        '--test',
        choices=['basic', 'premium'],
        help='Run internal tests instead of URL evaluation'
    )

    args = parser.parse_args()

    try:
        # Handle test mode
        if args.test:
            if args.test == 'basic':
                success = test_basic_evaluation()
            elif args.test == 'premium':
                success = test_premium_evaluation()
            sys.exit(0 if success else 1)

        # Validate URL is provided for non-test mode
        if not args.url:
            parser.error("URL is required when not using --test mode")

        if args.verbose:
            print("🔍 Initializing Model Evaluator...")

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
