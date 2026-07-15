# Contributing Guide

## Goals

Keep this repository useful and easy to maintain for A733 display work.

## Rules

- Make small, focused changes.
- Update the English document first, then the matching Chinese translation.
- Update current progress only in `docs/status.json`; README status blocks and
  `docs/status*.md` are generated files.
- Record important technical decisions in the decision log.
- Add or update sources whenever a hardware, BSP, or release claim changes.
- Prefer clear file names and predictable directory placement.
- Keep the workflow light. If you are the only maintainer, follow the same rules yourself without turning them into process theater.

## Workflow

1. Open or update the relevant document pair.
2. For a capability or milestone change, edit `docs/status.json` and run
   `python3 tools/render_status.py`.
3. Record the change in the decision log if it affects project direction.
4. Update the sources index if new references were used.
5. Run `python3 tools/render_status.py --check` and the test suite.
6. Validate links, wording, and consistency.
7. Commit the change with a descriptive message.

## Review expectations

- Keep terminology consistent across both languages.
- Avoid introducing duplicate definitions in multiple files.
- Reject direct edits inside `status-*:start` / `status-*:end` generated blocks.
- If a claim is uncertain, mark it as such instead of overstating it.
