Team members: Ziang Yang (zy234), Xianghao Zheng (xz473), Yanhe Zhu (yz1054), Yuyao Tang (yt237)  
Contribution: Equal contribution from all team members.

# Cubazoid Solver

This repository solves a 3D packing problem:
given multiple small voxel pieces (each size 3 to 5), determine whether they can exactly fill a perfect cube.

The project includes:
- two solver backends (`mrv` and `exact`),
- reproducibility notebooks,
- GIF-based construction visualizations,
- structured result exports (`json` and `csv`).

## Project Layout

```text
final project/
├─ README.md                          # project overview and usage notes
├─ cubazoid_solver.py                 # CLI entrypoint
├─ environment.yml                    # Conda environment lock
├─ requirements.txt                   # Pinned Python package versions
├─ demo_cubazoid_repro.ipynb          # Repro + batch export + visualization notebook
├─ Executive_Summary.pdf              # submission PDF copied to repo root
├─ FAQ.pdf                            # submission PDF copied to repo root
├─ technical_appendix.pdf             # submission PDF copied to repo root
├─ docs/
│  ├─ executive_summary_outline.md
│  ├─ faq_outline.md
│  ├─ technical_appendix_outline.md
│  └─ technical_appendix/
│     ├─ technical_appendix.ipynb     # Full technical appendix notebook
│     └─ assets/
│        └─ problem_contract_piece_examples_3_4_5.png
├─ tex/
│  ├─ Executive_summary_main.tex
│  └─ faq_main.tex
├─ submit_pdf/
│  ├─ Executive_Summary.pdf
│  ├─ FAQ.pdf
│  └─ technical_appendix.pdf
├─ cubazoid/
│  ├─ __init__.py
│  ├─ types.py                         # Coord / Placement dataclasses
│  ├─ geometry.py                      # normalization + rotations + orientation generation
│  ├─ examples.py                      # built-in benchmark cases
│  ├─ solver.py                        # MRV backend + Exact Cover (DLX) backend
│  ├─ visualization.py                 # 3D voxel animation and GIF export
│  └─ api.py                           # unified solve_and_visualize interface
└─ outputs/                            # generated artifacts (results, gifs, figures)
```

## Solver Backends

### `mrv` (default)
- Backtracking with MRV (minimum remaining values) target-cell selection
- Placement precomputation
- Forward checking
- Hole/component pruning
- Failed-state memoization with piece-class compression
- Bitmask collision acceleration

### `exact`
- Exact Cover formulation
- Algorithm X with DLX-style linked-node cover/uncover
- Piece-class count symmetry handling

Both backends follow the same input contract and return `List[Placement]` or `None`.

## Environment Setup (Conda)

```powershell
conda env create -f environment.yml
conda activate cubazoid-repro
python --version
```

If `conda activate` is not available in your shell:

```powershell
conda init powershell
```

## CLI Usage

List available cases:

```powershell
python cubazoid_solver.py --list-cases --include-large
```

Run one case with MRV:

```powershell
python cubazoid_solver.py --case search_7x7x7_mixed_balanced --include-large --backend mrv --timeout-sec 120
```

Run one case with Exact backend:

```powershell
python cubazoid_solver.py --case search_7x7x7_mixed_balanced --include-large --backend exact --timeout-sec 120
```

Run all built-in cases without visualization:

```powershell
python cubazoid_solver.py --all --include-large --backend mrv --no-show --timeout-sec 120
```

CLI options:
- `--all`: run all predefined cases
- `--case <name>`: run one case
- `--list-cases`: print case names and exit
- `--include-large`: include 5x5x5, 6x6x6, 7x7x7 search cases
- `--backend {mrv,exact}`: choose backend
- `--timeout-sec <float>`: per-case timeout (`<=0` disables timeout)
- `--no-show`: disable matplotlib window
- `--interval <ms>`: animation frame interval

## Notebook Workflows

### `demo_cubazoid_repro.ipynb`
- runs batch evaluation,
- exports:
  - `outputs/all_case_results.json`
  - `outputs/all_case_results.csv`
- generates solved-case GIFs under `outputs/all_case_gifs/`,
- includes an external-case integration tutorial (for instructor-provided case formats).

### `docs/technical_appendix/technical_appendix.ipynb`
Complete technical report notebook with:
- problem contract,
- solver design details,
- complexity discussion,
- experiment protocol,
- results and correctness checks,
- reproducibility guide and reporting policy.

## Output Artifacts

Typical generated files:
- `outputs/all_case_results.json`
- `outputs/all_case_results.csv`
- `outputs/all_case_gifs/*.gif`
- `outputs/demo_visual/*.gif`
- `outputs/external_case_gifs/*.gif` (if external-case tutorial is used)

## Status Semantics

The project distinguishes these statuses:
- `solved`: valid placement list returned
- `unsolved`: no solution found within run, no timeout flag
- `invalid_input`: input rejected by contract checks (`infeasible_reason` set)
- `timeout`: search exceeded time budget (`timed_out = True`)

Do not merge `timeout` into `unsolved` in reporting.

## Reproducibility Tips

- Keep `--no-show` for fair timing runs.
- Report environment metadata (OS, CPU, Python, lock files).
- For runtime comparisons, run multiple trials and report median.
- Keep provenance logs under `outputs/env/` when possible.
