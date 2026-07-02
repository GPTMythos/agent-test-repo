# GitHub Issue Resolution Agent

An autonomous, **free/open-source** AI agent that reads a GitHub issue, understands the
relevant parts of the repository, diagnoses the root cause, writes a fix, validates it
(tests/lint/build), self-corrects on failure, and opens a documented Pull Request.

This is a **proof of concept**, built to demonstrate a realistic agentic workflow rather
than a production system — see [Future Roadmap](#future-roadmap) for what a real version
would add.

## How it works (pipeline)

```
Repo URL + Issue ──▶ [1] Analyze issue & index repo (no full-repo dump)
                        │
                        ▼
                 [2] Explore + diagnose root cause
                     (agent decides which extra files it needs)
                        │
                        ▼
                 [3] Generate code changes
                        │
                        ▼
                 [4] Validate (tests / lint / build)
                        │      ▲
                        │      │  feed failures back, retry (bounded)
                        ▼      │
                     pass? ────┘ no
                        │ yes
                        ▼
                 [5] Branch, commit, push, open PR
                        │
                        ▼
                 [6] Print/save execution report
```

The key design choice for scaling to real repositories is the **retrieval layer**
(`repo_indexer.py` + `context_builder.py`): the LLM never sees the whole repo. It gets a
small set of files ranked by relevance to the issue text, expanded one hop via imports,
and — if it decides it needs more — it can explicitly request specific files (a small
tool-use loop) before committing to a root-cause analysis.

## Project layout

```
github-issue-agent/
├── main.py                     # CLI entry point
├── pyproject.toml
├── .env.example
└── src/agent/
    ├── config.py                # Configuration Manager (pydantic-settings)
    ├── models.py                 # Typed data contracts between phases
    ├── logger.py                 # Logging System
    ├── github_client.py          # GitHub Client (PyGithub) — issues, PRs
    ├── repo_manager.py           # Repository Manager (clone/update via GitPython)
    ├── repo_indexer.py           # Repository Indexer (symbols/imports/keywords)
    ├── context_builder.py        # Context Builder (relevance search + budget)
    ├── llm_interface.py          # LLM Interface (Ollama / OpenAI-compatible / Anthropic)
    ├── prompts.py                 # Prompt Templates
    ├── code_generator.py         # Exploration loop, root cause, code generation
    ├── validator.py               # Validator (pytest/ruff/npm test/build, best-effort)
    ├── self_correction.py        # Self-Correction Agent (bounded retry loop)
    ├── git_manager.py             # Git Manager (branch/commit/push)
    ├── pr_manager.py              # Pull Request Manager (PR body + creation)
    └── orchestrator.py           # Wires phases 1-6 together + CLI
```

Every component is independently replaceable — e.g. swap `llm_interface.py`'s provider,
or replace `repo_indexer.search()` with an embedding-based vector search, without
touching anything else.

## Setup

**Requirements:** Python 3.10+, git, and a GitHub Personal Access Token.

```bash
# 1. Install uv (fast, free Python package manager) if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
cd github-issue-agent
uv venv
uv pip install -e .

# 3. Configure
cp .env.example .env
# edit .env: set GITHUB_TOKEN, and your LLM provider settings
```

### Choosing a free LLM

- **Recommended (fully local, no API key, no cost):** install [Ollama](https://ollama.com),
  then `ollama pull qwen2.5-coder:7b` (or any coding-capable model you can run). Leave
  `LLM_PROVIDER=ollama` in `.env`.
- **Free hosted alternative:** any OpenAI-compatible free tier (e.g. Groq). Set
  `LLM_PROVIDER=openai_compatible`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`.

### GitHub token

Create a classic PAT with `repo` scope (or a fine-grained token with Contents +
Issues + Pull requests read/write) at
`https://github.com/settings/tokens`. Put it in `.env` as `GITHUB_TOKEN`.

## Usage

```bash
uv run python main.py --repo owner/name --issue 42

# or a full URL for either argument
uv run python main.py --repo https://github.com/owner/name --issue https://github.com/owner/name/issues/42

# Analyze, fix, and validate WITHOUT pushing/opening a PR:
uv run python main.py --repo owner/name --issue 42 --dry-run

# Save the final report to a file
uv run python main.py --repo owner/name --issue 42 --report-out report.md
```

The agent will:
1. Clone the repo into `.agent_workspace/` (configurable via `WORKDIR`).
2. Print progress for each phase.
3. Print a final execution report (issue, root cause, files touched, validation
   results, retry attempts, PR URL, duration, confidence).

## Error handling

The agent is built to fail gracefully rather than crash: invalid repos/issues,
missing tokens, clone failures, unreachable LLM endpoints, unparsable model output,
and validation failures are all caught and surfaced in the execution report. Code
generation retries are capped by `MAX_SELF_CORRECTION_RETRIES` to prevent infinite loops.

## Limitations (POC scope)

- Relevance search is keyword-overlap based, not embeddings — good enough for
  small/medium repos, but a large monorepo would benefit from a real vector index.
- Code generation asks the LLM for full file contents rather than diffs, which is
  more reliable to parse/apply for a POC but uses more tokens on large files.
- No sandboxing: validation runs tests/build tools directly in the cloned repo.
  Don't point this at a repo you don't trust, or run it in a container/VM.
- Single-issue, single-run tool — no persistent queue or scheduling.

## Future Roadmap

- Embedding-based repository index (e.g. Chroma + a free local embedding model)
  as a drop-in replacement for `RepoIndexer.search()`.
- Sandboxed validation (Docker) so untrusted repos can be handled safely.
- Diff-based code edits instead of whole-file regeneration, for large files.
- Multi-issue batch mode with a persistent work queue.
- Human-in-the-loop approval step before push (currently opt out via `--dry-run`).
- Structured tool-calling (function calling) once using a model/provider that
  supports it natively, instead of JSON-in-prompt parsing.
