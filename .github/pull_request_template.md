## Summary

<!-- What changed and why? -->

## Verification

- [ ] `python -m pytest`
- [ ] `ruff check src tests`
- [ ] `mypy src`
- [ ] `python -m build`

## Safety review

- [ ] No credentials, runtime state, or personal paths are included.
- [ ] New effects have explicit policy/risk handling and STOP checks.
- [ ] Provider-specific behavior is isolated and tested.
