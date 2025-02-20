"""Script to run tests with coverage report."""
import subprocess
import sys


def run_tests():
    """Run pytest with coverage report."""
    # Run tests with coverage
    result = subprocess.run([
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
        "tests/"
    ], capture_output=True, text=True)

    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
