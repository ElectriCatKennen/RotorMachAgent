# Contributing to RotorAgent

Thank you for your interest in contributing to RotorAgent! This document provides guidelines and instructions for contributing.

## Quick Links

- [CLA (Contributor License Agreement)](CLA.md) — required for `src/` contributions
- [Development Roadmap](docs/04_开发规划.md) — see what's planned
- [Open Issues](../../issues) — find something to work on

## How to Contribute

### Report Bugs

1. Search [existing issues](../../issues) to avoid duplicates
2. Open a new issue with:
   - SW version and Python version
   - Minimal reproducible script
   - Expected vs actual behavior
   - Error messages (original text, not screenshots)

### Suggest Features

1. Open an issue with the `enhancement` label
2. Describe the use case (not just the solution)
3. Reference relevant standards (GB, ISO, API docs)

### Submit Code

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/your-feature`
3. Make your changes
4. **Test** your changes (at minimum, run your script against SW)
5. **Commit** with a clear message (see format below)
6. **Push** to your fork: `git push origin feature/your-feature`
7. Open a **Pull Request**

### Commit Message Format

```
<type>: <short description>

[optional longer description]
```

Types:
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation
- `refactor`: code restructuring
- `test`: test additions
- `chore`: maintenance

Examples:
```
feat: add shaft keyway generator with GB/T 1096 lookup
fix: FeatureRevolve parameter order (was causing 302.7° rotation)
docs: add SW API measurement method reference
```

## CLA Requirements

| Contribution Type | CLA Required | Why |
|------------------|-------------|-----|
| `src/` (core code) | **Yes** | Dual licensing (AGPL-3.0 + commercial) requires copyright assignment |
| `docs/` (documentation) | No | Documentation is not part of the dual-licensed core |
| `tests/` (test cases) | No | Tests are not part of the dual-licensed core |
| `examples/` (examples) | No | Examples are not part of the dual-licensed core |
| Bug reports / suggestions | No | Not copyrightable contributions |

If your PR touches `src/` files, you will be asked to confirm CLA acceptance. See [CLA.md](CLA.md) for full terms.

## Development Setup

### Prerequisites

- Windows 10/11
- Python 3.10+ (recommended: 3.11)
- SOLIDWORKS 2023+
- conda (recommended)

### Setup Steps

```bash
# Create conda environment
conda create -n rotoragent python=3.11
conda activate rotoragent

# Install dependencies
pip install -r requirements.txt

# Verify SW API connection
python tests/test_shaft_modeling.py
```

### Known Issues

- **comtypes encoding**: Chinese Windows may produce `mbcs` encoding errors. Set `PYTHONUTF8=1` before running.
- **COM registration**: If `Dispatch('SldWorks.Application')` fails, open SW GUI once to register COM components.

## Code Style

- Python 3.10+ syntax
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Use `ruff check .` and `ruff format .` before committing
- Add function-level docstrings and type annotations for public APIs

## Project Structure

```
src/
├── tools/          # Agent tool wrappers (measure, build, export)
├── adapters/       # Software adapters (solidworks, autocad, ansys)
└── agents/         # Agent workflow orchestration
```

When adding a new tool:
1. Create `src/tools/<tool_name>.py`
2. Follow the existing tool interface pattern
3. Add a test in `tests/`
4. Update docs

## Questions?

Open a [discussion](../../discussions) for general questions, or an [issue](../../issues) for bugs and feature requests.
