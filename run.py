"""
Root entrypoint for RazorRecover AI.
Allows judges on Windows, macOS, and Linux to run benchmarks, tests, and CLI directly.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so imports work regardless of working directory
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else None

    if action in ("benchmark", "eval", "--benchmark", "--eval"):
        from src.evaluation import EvaluationHarness
        harness = EvaluationHarness(seed=42)
        rep = harness.run_benchmark(count=200)
        harness.print_report(rep)

    elif action in ("test", "tests", "pytest", "--test"):
        try:
            import pytest
            sys.exit(pytest.main(["backend/tests", "-v"]))
        except ImportError:
            print("pytest not installed. Install with: pip install -r backend/requirements.txt")

    else:
        from src.cli import main
        main()
