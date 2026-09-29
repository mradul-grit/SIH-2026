# Contributing to SIH-26227

Thank you for working on this project. Follow these guidelines to keep the codebase maintainable and ready for review.

---

## Development Setup

```bash
git clone https://github.com/mradul-grit/SIH-2026.git
cd SIH-2026
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install pytest httpx ruff       # dev extras
```

---

## Branching Strategy

| Branch | Purpose |
| :--- | :--- |
| `main` | Protected. All reviewed, passing code. |
| `feature/<name>` | New features or modules. |
| `fix/<name>` | Bug fixes. |
| `exp/<name>` | ML experiments (may not merge to main). |

- **Never push directly to `main`.** Open a Pull Request.
- **One PR per logical change.** Keep PRs small (< 400 lines) for faster review.
- Delete your feature branch after merge.

---

## Commit Message Format

```
<type>(<scope>): <short description>

[optional body]
[optional footer: Closes #issue]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `exp`

**Examples:**
```
feat(models): add CBAM attention to siamese encoder
fix(api): handle missing file_t2 in change-detect endpoint
docs(readme): add quickstart instructions
test(endpoints): add audit log endpoint coverage
exp(training): unified 5-dataset training run EXP-002
```

---

## Code Standards

- **Python style**: `ruff` with `line-length=100`. Run `ruff check . --fix` before committing.
- **Type hints**: Add type hints to all public function signatures.
- **Docstrings**: All public classes and functions need at minimum a one-line summary docstring.
- **No hardcoded paths**: Always use `from project_code.config import PROJECT_ROOT` for file I/O.

---

## Testing

Every non-trivial code change must include or update tests in `tests/`.

```bash
# Run full test suite
pytest tests/ -v

# Run only smoke tests (fast)
pytest tests/test_smoke.py -v

# Run only API integration tests
pytest tests/test_endpoints.py -v
```

All tests must pass before a PR is merged.

---

## Pull Request Checklist

- [ ] Branch is up to date with `main`
- [ ] All tests pass locally
- [ ] `ruff check .` returns no errors
- [ ] New modules include docstrings
- [ ] No hardcoded paths or credentials
- [ ] Documentation updated if API/architecture changed
- [ ] Experiment log updated if a new ML experiment was run (`docs/experiments/experiment-log.md`)
- [ ] `docs/architecture/decisions.md` updated if a new ADR was made

---

## Experiment Protocol

Before starting a new ML experiment:
1. Copy the experiment template from `docs/experiments/experiment-log.md`.
2. Assign a new ID: `EXP-NNN`.
3. Record the experiment at the start (hypothesis, dataset, config).
4. Update with results and conclusion after the run.
5. Commit the log update to a `exp/<name>` branch.
