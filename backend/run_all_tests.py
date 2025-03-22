#!/usr/bin/env python3
import os
import sys
import subprocess
import unittest
import pytest
import argparse
import asyncio
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

def print_header(message):
    """Print a formatted header message"""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{message.center(80)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")

def print_result(test_name, success=True, message=None):
    """Print test result with coloring"""
    if success:
        print(f"{Fore.GREEN}✓ {test_name} - PASSED{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ {test_name} - FAILED{Style.RESET_ALL}")
        if message:
            print(f"{Fore.RED}  {message}{Style.RESET_ALL}")

def run_pytest(test_files=None):
    """Run pytest tests with proper reporting"""
    args = ["-xvs"]
    
    if test_files:
        args.extend(test_files)
    else:
        # Exclude test_custom_llm.py as it's a CLI tool, not a pytest file
        args.append("tests/")
        args.append("--ignore=tests/test_custom_llm.py")
    
    print_header("Running pytest tests")
    
    try:
        pytest.main(args)
        return True
    except Exception as e:
        print_result("pytest", False, str(e))
        return False

def run_api_tests():
    """Run API integration tests"""
    print_header("Running API integration tests")
    
    try:
        # Run the API tests with pytest
        result = subprocess.run(
            ["python", "-m", "pytest", "-xvs", "tests/test_api_integration.py"],
            capture_output=True,
            text=True,
            check=False
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print_result("API Integration Tests", True)
            return True
        else:
            print_result("API Integration Tests", False)
            print(result.stderr)
            return False
    except Exception as e:
        print_result("API Integration Tests", False, str(e))
        return False

def run_api_config_test():
    """Run API configuration test"""
    print_header("Running API configuration tests")
    
    try:
        # Run the config API test script
        result = subprocess.run(
            ["python", "-m", "test_api_config"],
            capture_output=True,
            text=True,
            check=False
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print_result("API Configuration Tests", True)
            return True
        else:
            print_result("API Configuration Tests", False)
            print(result.stderr)
            return False
    except Exception as e:
        print_result("API Configuration Tests", False, str(e))
        return False

async def run_pdf_datasource_test():
    """Run PDF datasource test"""
    print_header("Running PDF datasource test")
    
    try:
        # Import and run the test directly
        from tests.test_pdf_datasource import test_pdf_datasource
        
        # Capture stdout to get test output
        import io
        import sys
        
        original_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        await test_pdf_datasource()
        
        sys.stdout = original_stdout
        print(captured_output.getvalue())
        
        print_result("PDF Datasource Test", True)
        return True
    except Exception as e:
        print_result("PDF Datasource Test", False, str(e))
        return False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run all tests for the backend")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--api-only", action="store_true", help="Run only API tests")
    parser.add_argument("--pdf-only", action="store_true", help="Run only PDF datasource test")
    parser.add_argument("--config-only", action="store_true", help="Run only API config tests")
    return parser.parse_args()

async def main():
    """Main function to run all tests"""
    args = parse_args()
    all_passed = True
    
    # Create sample_pdfs directory if it doesn't exist
    os.makedirs("sample_pdfs", exist_ok=True)
    
    # Determine which tests to run based on args
    run_unit = not any([args.api_only, args.pdf_only, args.config_only])
    run_api = not any([args.unit_only, args.pdf_only, args.config_only])
    run_pdf = not any([args.unit_only, args.api_only, args.config_only])
    run_config = not any([args.unit_only, args.api_only, args.pdf_only])
    
    # Run specific tests based on command line arguments
    if args.unit_only:
        run_unit = True
        run_api = run_pdf = run_config = False
    elif args.api_only:
        run_api = True
        run_unit = run_pdf = run_config = False
    elif args.pdf_only:
        run_pdf = True
        run_unit = run_api = run_config = False
    elif args.config_only:
        run_config = True
        run_unit = run_api = run_pdf = False
    
    # Run the tests
    if run_unit:
        unit_success = run_pytest()
        all_passed = all_passed and unit_success
    
    if run_api:
        api_success = run_api_tests()
        all_passed = all_passed and api_success
    
    if run_pdf:
        pdf_success = await run_pdf_datasource_test()
        all_passed = all_passed and pdf_success
    
    if run_config:
        config_success = run_api_config_test()
        all_passed = all_passed and config_success
    
    # Print summary
    print_header("Test Summary")
    if all_passed:
        print(f"{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"{Fore.RED}Some tests failed. Check the output above for details.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 