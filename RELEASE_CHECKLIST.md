# Release checklist

- [ ] Confirm the README describes structural auditing, not biological validation.
- [ ] Review all dependencies in `uv.lock` and the GitHub Actions workflow.
- [ ] Run `make verify` on the maintainer's machine.
- [ ] Run both synthetic examples and inspect their reports.
- [ ] Confirm the clean example passes and the leaky example exits with code `2`.
- [ ] Inspect wheel contents and install the wheel in a clean environment.
- [ ] Confirm author, repository URL, license, and citation metadata.
- [ ] Review `PROJECT_REPORT.md`, especially the reason not to publish.
- [ ] Create the public repository only after all boxes above are checked.
