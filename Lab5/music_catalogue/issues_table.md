# Issue Table: music_catalog.py

| # | Issue | Tool / Code | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|---------|-------------|--------------|
| 1 | SQL injection | Bandit B608 (Medium) | Security | 10 | INSERT built with `%` string formatting; a title like `x'); DROP TABLE songs;--` alters the query | Parameterized query with `?` placeholders |
| 2 | Unsafe deserialization | Bandit B301 / B403 (Medium/Low) | Security | 1, 33 | `pickle.loads` can execute arbitrary code from untrusted data | Replaced pickle with `json.dumps` / `json.loads` |
| 3 | Weak PRNG | Bandit B311 (Low) | Security | 17 | `random.choice` is not cryptographically secure | Used `secrets.choice` |
| 4 | Mutable default argument | Pylint W0102 | Bug | 9 | `playlist=[]` is shared across calls, so unrelated playlists accumulate songs | Default to `None`, create a new list inside the function |
| 5 | Bare except | Flake8 E722 / Pylint W0702 | Bug / Style | 39 | Swallows every exception, including KeyboardInterrupt, hiding real errors | Catch `sqlite3.Error` only |
| 6 | Ambiguous variable name | Flake8 E741 | Style | 47 | `l` is easily confused with `1` or `I` | Renamed to `loaded` |
| 7 | Multiple statements on one line | Flake8 E701 / Pylint C0321 | Style | 48 | `if ...: print(...)` on one line | Put the body on its own line |
| 8 | Lines too long | Flake8 E501 / Pylint C0301 | Style | 6, 10, 21, 49 | Lines exceed 79 characters | Wrapped across multiple lines |
| 9 | Naming convention | Pylint C0103 | Style | 9, 15, 28, 32, 36 | camelCase function names | Renamed to snake_case |
| 10 | Missing docstrings | Pylint C0114 / C0116 | Documentation | 1, all functions | No module or function docstrings | Added docstrings |
| 11 | Unnecessary else after return | Pylint R1705 | Style | 22-25 | `else` after `return` is redundant | Removed `else`, de-indented |
| 12 | Module runs on import | (best practice) | Design | 52 | `main()` called unconditionally | Added `if __name__ == "__main__":` guard |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.57 / 10 | 10.00 / 10 |
| Bandit | 4 issues (2 Medium, 2 Low) | 0 issues |
| Flake8 | 7 issues | 0 issues |
