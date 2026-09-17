import argparse
import sys
import io
from colorama import init, Fore, Style
from orchestrator.pipeline import run_pipeline

# Force UTF-8 output so emoji don't crash on Windows CP1252 terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Coding Assistant Demo")
    parser.add_argument("--spec", type=str, help="The coding specification to run")
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}{Style.BRIGHT}=========================================")
    print(f"{Fore.CYAN}{Style.BRIGHT} Multi-Agent Coding Assistant (Demo) ")
    print(f"{Fore.CYAN}{Style.BRIGHT}=========================================\n")
    
    spec = args.spec
    if not spec:
        spec = input(f"{Fore.YELLOW}Enter a coding specification:\n> ")
        print()
        
    print(f"{Fore.BLUE}Running Pipeline...")
    result = run_pipeline(spec)
    
    print("\n" + "="*40 + "\n")
    if result.success:
        print(f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] Solved in {result.iterations} iteration(s)!")
        print(f"\n{Fore.WHITE}Final Code:\n")
        print(result.final_code)
    else:
        print(f"{Fore.RED}{Style.BRIGHT}[FAILED] after {result.iterations} iteration(s).")
        print(f"\nFailure Reason: {result.failure_reason}")
        if result.final_code:
            print(f"\nLast Attempted Code:\n{result.final_code}")

if __name__ == "__main__":
    main()
