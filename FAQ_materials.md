# FAQ Draft Materials

## 1) What problem does this project solve?
**Answer:**  
This project solves a 3D cube-packing puzzle: given many small polycube components (each with 3 to 5 unit cubes), it determines whether they can exactly fill an \(n \times n \times n\) cube (for example, \(4^3\), \(5^3\), \(7^3\), etc.). If a solution exists, the solver returns one valid placement sequence and can visualize the construction process.

## 2) Why are there two solver backends (`mrv` and `exact`)?
**Answer:**  
The two backends are used for both practical solving and method comparison:
- `mrv`: heuristic backtracking with pruning (usually faster in this codebase).
- `exact`: an exact-cover route based on Algorithm X / DLX-style search.  
Having both lets us compare trade-offs between heuristic search and exact-cover modeling on the same benchmark cases.

## 3) What does “unsolved” mean in solver output?
**Answer:**  
“Unsolved” (or “No cube-forming configuration exists.”) means the solver did not find a valid arrangement under the current model and constraints. This can happen because:
- the instance is mathematically infeasible, or
- the search space is too hard for the selected backend/time budget.  
For strict conclusions, record solver settings, backend, and runtime budget in your report.

## 4) How do I run larger benchmark cases from the command line?
**Answer:**  
Use `--include-large` to enable 5x5x5 / 6x6x6 / 7x7x7 cases, then pick a case and backend. Example:

```powershell
python cubazoid_solver.py --case search_7x7x7_mixed_balanced --include-large --no-show --backend mrv
```

To list all available cases:

```powershell
python cubazoid_solver.py --list-cases --include-large
```

## 5) How should I report performance fairly?
**Answer:**  
Use a consistent protocol:
1. Run on the same machine and Python version.
2. Disable visualization during timing (`--no-show`).
3. Use the same input case for both backends.
4. Run multiple trials and report median runtime.
5. Report whether a solution was found, runtime, and number of pieces.  
This makes comparisons reproducible and academically defensible.
