# Lab 5: Reflection

## Note on reflection questions

The lab README (step 6) states: "Answer the four reflection questions from the handout
in `reflection.md`." The questions themselves are in the physical lab handout, which is
not included in this repository. The four reflection answers below address the themes
that static-analysis labs at this level typically cover — tool findings, fixing vs.
suppressing, security vs. style, and limitations — based on the actual work done in
this assignment. If the handout questions differ, these answers should be updated to
match the exact wording provided.

---

## Q1. What issues did the static analysis tools find that you might have missed in a
manual code review?

Running Pylint, Bandit, and Flake8 surfaced several problems that are easy to overlook
when reading code by eye:

- **All eight function names violated snake_case** (e.g. `addStock`, `removeStock`).
  In a quick manual scan the logic can look correct even though the naming breaks PEP 8
  throughout.
- **Two `eval()` calls** — one on a user-supplied formula, one on a hard-coded string
  — were flagged by Bandit as Medium severity. The second one (`eval("print('stock
  audit complete')")`) is obviously unnecessary, but it is the kind of line that blends
  into the background during review.
- **MD5 usage** (High severity in Bandit, B324) is easy to miss because `hashlib.md5`
  looks like any other hash call; only a tool with a known-weak-algorithm list catches
  it reliably.
- **Mutable default argument** (`history=[]`) is a classic Python footgun. Manual review
  can overlook it, but Pylint flags it immediately as W0102.

Pylint's numeric score (4.93 / 10 before fixes) also provided an objective baseline
that made the overall state of the code impossible to ignore.

---

## Q2. Which issues were most important to fix, and why?

Priority was given to Bandit findings, in order of severity:

1. **MD5 weak hash (High)** — The SKU checksum used `hashlib.md5`, which is
   cryptographically broken. Even though the checksum here is only a short label printed
   on bin cards, using a weak hash normalises bad practice. Replaced with SHA-256.

2. **`eval()` on user input (Medium × 2)** — Passing a user-supplied string to `eval()`
   is a remote code execution risk. The formula `"current + 25"` is benign, but
   `"__import__('os').system('rm -rf /')"` is also a valid `eval()` input. Replaced with
   a whitelist-based AST evaluator that permits only numeric constants and the four
   arithmetic operators.

3. **Hardcoded password (Low)** — Storing `"wh-admin-1234"` in source code means the
   credential is visible in Git history forever, even after it is removed. Moved to an
   environment variable.

Style and quality issues (docstrings, naming, blank lines) were fixed last because they
carry no security risk, but they matter for maintainability and for achieving the
Pylint > 9.5 target.

---

## Q3. What is the difference between suppressing a warning and fixing it? Give an
example from this assignment.

Suppressing a warning hides the symptom without addressing the cause. Examples of
suppression that were deliberately avoided in this assignment:

- Adding `# nosec B307` to the line with `eval()` would silence Bandit but leave the
  arbitrary code execution risk in place.
- Adding `# pylint: disable=invalid-name` would remove the C0103 score penalty but
  leave all call sites using camelCase names, making the code harder to read and
  inconsistent with Python conventions.
- Adding `# noqa: E501` to a long line would satisfy Flake8 without improving
  readability.

The correct approach is to fix the underlying issue. For the `eval()` calls, that meant
writing `safe_calculate()` — approximately 30 lines of AST-walking code. It is more
work than a comment, but it actually makes the program safer. Every suppression
directive also degrades the signal-to-noise ratio for future tool runs, making it
harder to notice new genuine issues.

---

## Q4. What can static analysis tools NOT detect? What did you have to find by reading
and running the code yourself?

Static analysis tools work on code structure; they cannot reason about runtime
behaviour or program intent. Issues found only by reading and running the code:

- **Logic bug in `remove_stock`**: the original `bare except: pass` meant that removing
  stock from a SKU that did not exist (e.g. `remove_stock("GHOST-9", 1)`) silently did
  nothing instead of returning cleanly. Pylint flagged the bare `except`, but not the
  fact that the correct fix is a pre-condition check (`if sku not in warehouse_stock:
  return`), not just a more specific exception type.

- **Over-removal without error**: `remove_stock("WID-001", 500)` on a SKU with only 28
  units drove the stock to a large negative number in the original code. The tool
  reports showed nothing wrong with this. Reading the code and running the demo revealed
  it. The fix (delete the entry when stock reaches zero or below) was a semantic
  decision, not a tool recommendation.

- **`__name__ == "__main__"` guard missing**: the original code called `main()` at
  module level unconditionally, meaning importing the file in a test or another script
  would immediately run the demo, create a `warehouse.json`, and write to the audit log.
  No tool flagged this in the initial reports; it was identified by reading the code
  structure and was fixed by adding `if __name__ == "__main__": main()`.

These examples show that static analysis is a valuable first pass, but it is not a
substitute for code reading, running the program, and thinking about intended behaviour.
