# Repository Guidelines

## Scope
These instructions apply to the entire repository unless a more specific `AGENTS.md` is introduced in a subdirectory.

## Style and Structure
- All documentation must use British English spelling and maintain an academic yet accessible tone.
- Structure Markdown documents with hierarchical headings (start at `#` and proceed sequentially).
- When listing ordered processes, use numbered lists with clear action verbs.
- Cite external references inline using bracketed reference tags (e.g., `[Ref1]`) and include a corresponding reference list where appropriate.

## Simulation Interoperability
- Ensure every new analytical or simulation script preserves compatibility with Systems Tool Kit (STK 11.2) data formats so outputs remain importable.
- Validate any new data products against the STK exporter (`tools/stk_export.py`) and document any limitations discovered during validation.

## Version Control
- Keep commits logically scoped and reference the main objective in the commit message.
- Do not include generated binaries or temporary files in the repository.

## Tests
- Place automated test assets under the `tests/` directory. Use a placeholder file (e.g., `.gitkeep`) if the directory would otherwise be empty.

## Documentation
- Place in-depth technical notes, derivations, and methodological details inside the `docs/` directory.
- The repository root `README.md` must provide a high-level overview and link to relevant documents inside `docs/`.

## Pull Requests
- Summaries must highlight mission design progress, analytical deliverables, and testing status.
