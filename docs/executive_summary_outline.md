# Two-Page Executive Summary Outline (No Jargon)

## 1) Problem (1-2 paragraphs)
- What is the real task?
  - We are given many small 3D block pieces.
  - Each piece has 3, 4, or 5 cubes.
  - Goal: decide whether all given pieces can exactly form one perfect cube.
- Why this matters:
  - It is a planning and search problem with many possibilities.
  - Fast and reliable solving is needed because hidden test cases are unknown.

## 2) Approach (3-5 short paragraphs)
- Big picture:
  - We built a solver that tries placements step by step.
  - It keeps only valid partial constructions and drops impossible branches early.
- Two solving modes:
  - `mrv`: practical search mode (default, fastest in our project).
  - `exact`: exact-cover baseline mode (good for method comparison).
- Reliability features:
  - Input checks (piece size range, connectivity, total volume).
  - Per-case timeout so one hard case does not block all runs.
- Visualization:
  - If a solution exists, we animate piece-by-piece cube construction.

## 3) Results (3-4 short paragraphs + 1 table)
- What was tested:
  - Small to large cases, including 5x5x5, 6x6x6, 7x7x7.
  - Both backends on the same machine and settings.
- What happened:
  - `mrv` solved more quickly on our benchmark set.
  - `exact` remained useful as a correctness/comparison baseline.
- Include a compact table:
  - Columns: case name, n, piece count, backend, solved?, runtime, timeout?.

## 4) What We Learned (1 short paragraph)
- Practical search with good pruning worked best for this assignment scale.
- Input validation and timeout handling were critical for stable batch grading.

## 5) Future Work (1-2 short paragraphs)
- Add richer test generation and stress tests.
- Add stronger lower-bound pruning and optional parallel search.
- Improve visualization and automated reporting outputs.

## 6) Writing Style Checklist (for A+ alignment)
- No equations, symbols, or specialist vocabulary.
- Prefer plain verbs: “try”, “check”, “reject”, “fill”, “verify”.
- Keep each paragraph focused on one message.
- End with a clear “what this means” sentence.

