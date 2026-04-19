# Technical Appendix Outline (Reproducible)

## 1) Repository Snapshot & Environment Lock
- Commit hash used for all reported results.
- File map (solver, api, examples, visualization, CLI entry).
- Python version and required packages.
- Dependency lock file(s) used (`requirements.txt` or `environment.yml`).
- Exact install command(s) and the date environment was validated.

## 2) Problem Contract
- Input format: list of 3D binary tensors.
- Output contract: valid placement list or `None`.
- Validation rules implemented:
  - piece size in `[3, 5]`
  - piece connectivity
  - total volume is a perfect cube
  - per-case timeout behavior

## 3) Solver Design
- `mrv` backend:
  - orientation generation
  - placement precomputation
  - MRV target selection
  - forward checks, hole pruning
  - memoization key design
  - bitmask acceleration
- `exact` backend:
  - exact cover formulation
  - DLX node structure
  - class-count symmetry breaking

## 4) Complexity Discussion
- Search-space growth intuition.
- Why pruning and ordering matter.
- Tradeoff between stronger branching vs branching-overhead.

## 5) Experimental Protocol
- Machine + OS + Python.
- Commands used.
- Timeout and visualization settings.
- Trial count and summary statistic (median recommended).

## 6) Results
- Table for all benchmark cases:
  - case name, cube size, piece count
  - backend
  - solved?
  - runtime
  - timeout hit?
- Include both successful and failed cases.

## 7) Correctness Checks
- Evidence that:
  - no overlaps
  - full cube coverage
  - each piece used once
  - invalid inputs rejected
- Include script/notebook outputs or logs.
- Independent verification script: command, input artifact, and expected pass/fail fields.

## 8) Ablation Notes
- Before/after bitmask optimization.
- MRV vs first-empty experiment note.
- Effect of timeout setting on batch stability.

## 9) Visualization Notes
- How the animation is generated.
- How to disable display for fair timing.
- Optional save-to-file workflow.

## 10) Reproduction Guide (Step-by-step)
1. Clone repo and install environment.
2. Run smoke tests.
3. Run benchmark commands.
4. Run notebook demo.
5. Compare outputs with reported tables.

## 10.5) One-Command Reproduction
- Provide one canonical command that reproduces the main reported batch.
- List expected output file paths (e.g., CSV/JSON/GIF folders).
- State expected status summary format (solved/unsolved/invalid/timeout).

## 11) Raw Data and Artifacts
- Link locations for raw runtime logs.
- Notebook path.
- Any exported CSV/JSON result files.

## 12) Limitations and Future Improvements
- Known hard cases.
- Potential algorithm upgrades.
- Engineering improvements for robustness.

## 13) Status Interpretation (Reporting Policy)
- Define `invalid_input`, `unsolved`, and `timed_out` exactly as used in code/output.
- Explain how each status should be reported in tables and narrative.
- Clarify what conclusions are valid (and not valid) under timeout-limited runs.
