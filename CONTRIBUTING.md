# Contributing

Thanks for contributing to MCP Directory Local.

1. Use Python 3.10+ and create a virtual environment.
2. Install with `python -m pip install -e .`.
3. Keep the core dependency-free unless a dependency clearly improves safety or correctness.
4. Add or update tests for behavior changes.
5. Run `python -m compileall -q src tests` and `python -m unittest discover -s tests -v`.
6. Keep examples synthetic and never commit tokens, credentials, private URLs, or personal data.
7. Submit focused changes with clear commit messages.

Bug reports should include platform, Python version, a minimal sanitized registry, expected behavior, and actual behavior.
