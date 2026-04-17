# FAQ Outline (2-5 pages)

Use this as a question bank. Pick ~12-18 questions depending on target length.

## A. Problem Definition
1. What exactly is the input and output?
2. What does “returns null otherwise” mean in your implementation?
3. Do you always use all pieces, or can some be left unused?
4. What counts as a valid piece in this project?

## B. Correctness and Trust
5. How do you know the solution really fills the full cube and not only a shell?
6. How do you prevent overlapping pieces?
7. How do you verify each piece is used exactly once?
8. What happens when the total piece volume is not a perfect cube?
9. What happens if a piece is disconnected?

## C. Algorithm Choices
10. Why include both `mrv` and `exact` backends?
11. Why is `mrv` the default?
12. What pruning ideas were most important?
13. Did you test alternative branching strategies (for example first-empty cell)?

## D. Performance and Limits
14. How do you measure runtime fairly?
15. Why add per-case timeout, and what timeout did you choose?
16. Which cases are hardest and why?
17. What are known failure modes or limits?

## E. Reproducibility
18. How can someone reproduce your reported numbers exactly?
19. Which command lines should a grader run first?
20. What environment assumptions matter (Python version, machine, visualization on/off)?

## F. Deliverable Quality
21. What does the visualization show, and how should it be interpreted?
22. What did you change after debugging/merge conflicts, and how did you re-validate?
23. If results vary run-to-run, how do you report them responsibly?

## Suggested Answer Template (reuse per question)
- **Short answer (1-2 sentences)**
- **Evidence (command, log line, or code location)**
- **Implication (why this matters to grading or correctness)**

