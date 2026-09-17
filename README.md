# Multi-Agent Coding Assistant

A multi-agent AI pipeline that takes a plain-English coding specification and produces **working, tested Python code** through a collaborative loop of four agents backed by a secure Docker sandbox exposed via the **Model Context Protocol (MCP)**.

## Architecture

```
User Spec (str)
      │
      ▼
 ┌──────────┐  JSON plan
 │  Planner  │──────────────────────────────►┐
 └──────────┘                                │
                                             ▼
                                        ┌────────┐ ◄── feedback (structured)
                                        │  Coder  │◄──────────────────────┐
                                        └────────┘                        │
                                             │ code                       │
                                             ▼                            │
                                        ┌──────────┐  issues? ──── YES───┘
                                        │ Reviewer  │
                                        └──────────┘
                                             │ approved
                                             ▼
                                        ┌────────┐  run_code(code, tests)
                                        │ Tester  │────────────────────► MCP Sandbox (Docker)
                                        └────────┘ ◄──── stdout/stderr/pass-fail
                                             │ fail?
                                             └──── feedback ──► Coder (loop ≤ 4x)
                                             │ pass
                                             ▼
                                          ✅ Result
```

## Why MCP for the Sandbox?

The sandbox is wrapped as an **MCP Server** instead of a plain `subprocess.run()` call:

- **True Isolation**: Runs code in a disposable `code-sandbox:latest` Docker image (built on `python:3.12-slim`) with `--network none` — the generated code cannot make network requests, import unexpected system packages, or persist state between runs.
- **Resource Caps**: `--memory 128m --cpus 0.5` prevents runaway loops from locking up the host.
- **Reusability**: Any MCP-compatible client (Cursor, Claude Desktop, another agent) can connect to this same sandbox server without code changes.
- **Separation of Concerns**: The execution environment can be swapped (e.g., from Docker to Firecracker microVMs) without touching agent logic.

## Prerequisites

- Python 3.11+
- Docker Desktop (must be running)
- A [Google AI Studio](https://aistudio.google.com) API key (free tier works)

## Setup

**1. Clone and install dependencies:**
```powershell
git clone <repo-url>
cd "Multi-Agent Coding Assistant"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure your API key:**
```powershell
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY
```

**3. Build the Docker sandbox image** (one-time step):
```powershell
docker build -t code-sandbox:latest .\mcp_sandbox
```
This bakes `pytest` into the image so tests run with `--network none` (no internet).

## Usage

### Interactive Demo
```powershell
python -m demo.run_demo --spec "Write a function that checks if a string is a palindrome."
```

### Run the Full Evaluation Suite (20 tasks)
```powershell
python -m tasks.evaluator
# Results saved to metrics.json
```

## Evaluation Metrics

Tested against 20 coding tasks of increasing difficulty (Easy × 5, Medium × 8, Hard × 7):

| Metric | Result |
|---|---|
| **Success Rate** | **100% (20/20)** |
| **Avg Iterations (all tasks)** | **1.6** |
| **Total Evaluation Time** | 434 seconds (~7 min) |
| **Total Tasks** | 20 |

### Per-task Iteration Breakdown

| Task | Difficulty | Iterations | Notes |
|---|---|---|---|
| E1 add_numbers | Easy | 2 | Reviewer flagged missing type check |
| E2 is_even | Easy | 1 | First try |
| E3 reverse_string | Easy | 2 | Minor test assertion fix |
| E4 celsius_to_fahrenheit | Easy | 1 | First try |
| E5 count_vowels | Easy | 1 | First try |
| M1 find_max | Medium | 1 | First try |
| M2 is_palindrome | Medium | 1 | First try |
| M3 factorial | Medium | 4 | Recursion depth + int digit limit edge cases |
| M4 fibonacci | Medium | 1 | First try (iterative approach) |
| M5 merge_dicts | Medium | 1 | First try |
| M6 flatten_list | Medium | 1 | First try |
| M7 remove_duplicates | Medium | 1 | First try |
| M8 binary_search | Medium | 1 | First try |
| H1 lru_cache_impl | Hard | 2 | Interface check needed |
| H2 is_valid_parentheses | Hard | 2 | Edge case: non-bracket chars |
| H3 longest_substring | Hard | 2 | Off-by-one boundary |
| H4 word_frequency | Hard | 3 | Sort order + punctuation edge cases |
| H5 evaluate_postfix | Hard | 1 | First try |
| H6 topological_sort | Hard | 3 | Cycle detection + self-loop edge case |
| H7 roman_to_int | Hard | 1 | First try |

### Task Categories

| Difficulty | Count | Success | Avg Iterations |
|---|---|---|---|
| Easy | 5 | 5/5 (100%) | 1.4 |
| Medium | 8 | 8/8 (100%) | 1.4 |
| Hard | 7 | 7/7 (100%) | 2.0 |

## Project Structure

```
├── mcp_sandbox/
│   ├── Dockerfile        # Custom image: python:3.12-slim + pytest
│   ├── server.py         # MCP server exposing run_code() tool (MCP 2.x)
│   └── executor.py       # Runs code in Docker with --network none
│
├── agents/
│   ├── base.py           # Gemini LLM wrapper with retry/backoff
│   ├── planner.py        # Breaks spec into JSON plan
│   ├── coder.py          # Writes code from plan + feedback
│   ├── reviewer.py       # Reviews code against spec & plan
│   └── tester.py         # Writes tests, calls MCP sandbox
│
├── orchestrator/
│   └── pipeline.py       # Wires the loop (max 4 iterations)
│
├── tasks/
│   ├── task_definitions.py  # 20 evaluation specs
│   └── evaluator.py         # Batch runner + metrics
│
├── demo/
│   └── run_demo.py       # Colored CLI interface
│
├── requirements.txt
└── .env.example
```

## Configuration

| Env Var | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | *(required)* | Gemini API key |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Override the LLM model |
