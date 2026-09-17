import argparse
import sys
import io

from colorama import init, Fore, Style
from orchestrator.pipeline import run_pipeline

# Force UTF-8 output so special characters don't crash on Windows CP1252 terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

init(autoreset=True)


def _print_files(files: dict, color: str = Fore.WHITE) -> None:
    """Print all generated files with filename headers."""
    for filename, code in files.items():
        print(f"\n{color}{'─' * 40}")
        print(f"{Style.BRIGHT}{filename}")
        print(f"{'─' * 40}{Style.RESET_ALL}")
        print(code)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Single-file: python -m demo.run_demo --spec 'Write a fibonacci function'\n"
            "  Multi-file:  python -m demo.run_demo --spec "
            "'Create a calculator package with add, subtract, multiply, divide "
            "in separate modules and a validation utility.'"
        ),
    )
    parser.add_argument("--spec", required=True, help="Plain-English coding specification.")
    args = parser.parse_args()

    spec: str = args.spec

    print(f"\n{Fore.CYAN}{'=' * 41}")
    print(f" Multi-Agent Coding Assistant (Demo)")
    print(f"{'=' * 41}{Style.RESET_ALL}\n")
    print("Running Pipeline...")

    result = run_pipeline(spec)

    print(f"\n{'=' * 40}\n")

    if result.success:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] Solved in "
            f"{result.iterations} iteration(s)!"
        )
        print(f"\n{Fore.WHITE}Generated Files:\n")
        _print_files(result.final_files or {}, color=Fore.CYAN)
    else:
        print(
            f"{Fore.RED}{Style.BRIGHT}[FAILED] after "
            f"{result.iterations} iteration(s)."
        )
        print(f"\nFailure Reason: {result.failure_reason}")
        if result.final_files:
            print(f"\n{Fore.YELLOW}Last Attempted Files:\n")
            _print_files(result.final_files, color=Fore.YELLOW)


if __name__ == "__main__":
    main()
