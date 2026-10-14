# Lab 5: Static Code Analysis Report

## Objective

Static code analysis is the process of examining source code without executing it to detect bugs, security vulnerabilities, and style violations. This lab applies three Python static analysis tools — Pylint, Bandit, and Flake8 — to a warehouse stock management program, documents the findings, applies fixes, and verifies improvements.

## Tools Used

| Tool | Purpose |
|------|---------|
| Pylint | Code quality: naming conventions, missing docstrings, unused imports, logic issues. Scores code 0–10. |
| Bandit | Security: detects hardcoded passwords, use of eval, weak hashing, bare except blocks. |
| Flake8 | Style: PEP 8 compliance, line length, whitespace, import order, unused variables. |

## Findings Table

| # | Issue | Tool | Orig. Line | Description | Fix Applied | Verified |
|---|-------|------|-----------|-------------|-------------|----------|
| 1 | Hardcoded password (B105) | Bandit | 10 | `SUPERVISOR_PASSWORD = "wh-admin-1234"` stored in source code. CWE-259. | Replaced with `os.environ.get("WAREHOUSE_SUPERVISOR_PASSWORD")`. Refuses login if env var unset. | Bandit reports 0 issues after fix. |
| 2 | Use of `eval()` (B307) | Bandit | 62, 80 | Two calls to `eval()` — one for stock formula, one for a print statement. Allows arbitrary code execution. CWE-78. | Removed both. Implemented `safe_calculate()` using `ast.parse()` + AST walk allowing only numeric constants and +,-,*,/. | Bandit reports 0 issues after fix. |
| 3 | MD5 weak hash (B324) | Bandit | 31 | `hashlib.md5()` used for SKU checksum. MD5 is cryptographically broken. CWE-327. | Replaced with `hashlib.sha256()`. | Bandit reports 0 issues after fix. |
| 4 | Bare `except` (B110/E722) | Bandit/Flake8 | 23 | `except: pass` swallows all exceptions silently, hiding bugs. | Replaced with specific exception handling; removed silent pass. | No bare-except warnings in any tool after fix. |
| 5 | Missing docstrings (C0116) | Pylint | multiple | Eight functions had no docstrings, making the code unmaintainable. | Added docstrings to all functions and a module-level docstring. | Pylint C0116 warnings eliminated. |
| 6 | Non-snake_case names (C0103) | Pylint | multiple | Functions named `addStock`, `removeStock`, `getStock`, etc. violate PEP 8. | Renamed all functions to snake_case; updated all call sites. | Pylint C0103 warnings eliminated; NameErrors resolved. |
| 7 | Mutable default argument (W0102) | Pylint | 12 | `def addStock(sku, qty, history=[])` — mutable default is shared across calls. | Changed to `history=None`; assign `history = []` inside function. | Pylint W0102 warning eliminated. |
| 8 | File opened without context manager (R1732) | Pylint/Flake8 | 34, 40, 63 | `open()` without `with` risks resource leaks. | All file operations converted to `with open(...) as f:` with `encoding='utf-8'`. | Pylint R1732 and Flake8 context-manager warnings eliminated. |
| 9 | Unconditional `main()` call at module level | Logic / Best practice | bottom | `main()` called unconditionally at import time. Importing the module in tests or other scripts runs the demo, writes files, and pollutes the environment. | Wrapped in `if __name__ == "__main__": main()`. | Program runs correctly when executed directly; does not execute on import. |

## Pylint Scores

| | Score |
|-|-------|
| Before | 4.93/10 |
| After | 10.00/10 |

## Bandit Summary

| Severity | Before | After |
|----------|--------|-------|
| High | 1 | 0 |
| Medium | 2 | 0 |
| Low | 2 | 0 |

## Flake8 Summary

| | Violations |
|-|-----------|
| Before | 19 |
| After | 0 |

## Reflection

See `reflection.md` for full answers to the lab reflection questions.

The lab README states the four reflection questions are in the physical handout (not in the repository). The reflection file covers the key themes: what tools found vs. manual review, fixing vs. suppressing warnings, priority of findings, and static analysis limitations.

## Conclusion

The warehouse stock manager was improved from a Pylint score of 4.93/10 to 10.00/10. All five Bandit security findings and all 19 Flake8 style violations were resolved. The fixes addressed real security risks (hardcoded credentials, arbitrary code execution via `eval`, weak MD5 hashing) and code quality issues (missing documentation, non-standard naming, resource leaks). The program's functionality was preserved and a silent logic bug in `add_stock` was also corrected.
