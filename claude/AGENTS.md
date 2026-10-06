# Purpose of the explanation-utility experiment

This experiment aims to isolate, as far as possible, the effect of Queen's natural-language explanations on inference-time search, separate from the effect of its numeric outputs, its model capacity and the search procedure itself. When a design choice could let numeric outputs or anything other than the explanations stand in for their contribution, choose the version that keeps the explanations' contribution separable.

## Budgets

- Pilot: at most $2k.
- Whole experiment: at most $25k.

## Example

In the rungs that use prose, the search selects which nodes to expand using the natural-language analyses at each node, not numeric evaluations. If selection ran on numbers, Queen's numeric heads would decide which positions get analysed, and any gain on those rungs could not be credited to the explanations.
