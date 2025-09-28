# Documentation Guidelines

## Scope
These instructions apply to every file within the `docs/` directory.

## Writing Standards
- Maintain a scholarly tone and support assertions with references to mission design literature where possible.
- Provide contextual introductions before diving into technical derivations or tables.
- Enumerate methodological stages using ordered lists, each prefaced by a concise summary sentence.
- When documenting analytical or simulation outputs, report the validation status against `tools/stk_export.py` and describe any
  limitations affecting Systems Tool Kit (STK 11.2) import compatibility.

## Formatting
- Include a concluding section titled `References` whenever sources are cited.
- Use tables for requirement matrices or trade-space summaries when they improve readability.
- Mathematical symbols should be typeset in inline LaTeX notation (e.g., `\(J_2\)`, `\(\delta a\)`).
