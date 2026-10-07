# Pilot report

Positions: 100. API spend: $409.76. Regret is Stockfish win-rate regret in percentage points (lower is better).

## Substituting cheaper models for opus

Positive difference = worse than the reference model.

| role | model | cell | n | regret diff | 95% CI | same move |
|---|---|---|---|---|---|---|
| reader/chooser | flash | ('chooser', 'R0', None, True, 'high') | 100 | +1.51 | [-0.98, +4.25] | 46% |
| reader/chooser | flash | ('chooser', 'R0', None, True, 'low') | 100 | -3.18 | [-5.89, -0.45] | 40% |
| reader/chooser | flash | ('chooser', 'R0', None, True, None) | 100 | -2.01 | [-4.31, +0.32] | 48% |
| reader/chooser | flash | ('chooser', 'R1', 'q/d0', False, None) | 100 | -1.10 | [-2.91, +0.52] | 81% |
| reader/chooser | flash | ('chooser', 'R1', 'q/d0', True, None) | 100 | -2.00 | [-3.63, -0.42] | 59% |
| reader/chooser | flash | ('chooser', 'R1', 'q/d1/qwen/prose', True, None) | 98 | -2.59 | [-4.34, -1.02] | 63% |
| reader/chooser | flash | ('chooser', 'R2', 'q/d0', False, None) | 100 | -0.85 | [-1.81, -0.03] | 91% |
| reader/chooser | flash | ('chooser', 'R2', 'q/d0', True, None) | 100 | -0.02 | [-1.53, +1.60] | 76% |
| reader/chooser | flash | ('chooser', 'R2', 'q/d1/qwen/prose', True, None) | 98 | -0.84 | [-3.01, +1.28] | 76% |
| reader/chooser | flash | ('chooser', 'R3', 'q/d0', False, None) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| reader/chooser | flash | ('chooser', 'R3', 'q/d0', True, None) | 100 | -0.36 | [-1.94, +0.45] | 89% |
| reader/chooser | flash | ('chooser', 'R3', 'q/d1/minimax', True, None) | 100 | +0.04 | [-0.95, +1.10] | 86% |
| reader/chooser | flash | ('chooser', 'R4', 'q/d0', False, None) | 100 | +0.01 | [-0.31, +0.35] | 98% |
| reader/chooser | flash | ('chooser', 'R4', 'q/d0', True, 'high') | 100 | +0.86 | [-0.61, +2.51] | 81% |
| reader/chooser | flash | ('chooser', 'R4', 'q/d0', True, 'low') | 100 | +0.65 | [-0.27, +1.80] | 83% |
| reader/chooser | flash | ('chooser', 'R4', 'q/d0', True, None) | 100 | +1.46 | [-0.15, +3.31] | 83% |
| reader/chooser | flash | ('chooser', 'R4', 'q/d1/qwen/full', True, None) | 93 | -0.60 | [-2.23, +0.91] | 83% |
| reader/chooser | flash | ('depth', 'R2', 'q/d0', False, None) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| reader/chooser | flash | ('depth', 'R2', 'q/d0', True, None) | 100 | -0.39 | [-1.01, -0.02] | 93% |
| reader/chooser | flash | ('depth', 'R2', 'q/d1/qwen/full', True, None) | 94 | -2.00 | [-3.91, -0.34] | 93% |
| reader/chooser | flash | ('depth', 'R2', 'q/d1/qwen/prose', True, None) | 98 | -0.78 | [-1.98, +0.03] | 96% |
| reader/chooser | flash | ('depth', 'R4', 'q/d0', False, None) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| reader/chooser | flash | ('depth', 'R4', 'q/d0', True, None) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| reader/chooser | flash | ('depth', 'R4', 'q/d1/qwen/full', True, None) | 93 | -0.39 | [-1.36, +0.12] | 97% |
| reader/chooser | flash | ('depth', 'ctrl', None, True, None) | 100 | -2.39 | [-4.92, +0.07] | 45% |
| reader/chooser | flash | ('oneply', 'R2', 'q', False, None) | 100 | -0.28 | [-1.08, +0.46] | 77% |
| reader/chooser | flash | ('oneply', 'R2', 'q', True, None) | 100 | -1.40 | [-3.04, -0.00] | 61% |
| reader/chooser | flash | ('oneply', 'R4', 'q', False, None) | 100 | -0.13 | [-0.42, +0.14] | 90% |
| reader/chooser | flash | ('oneply', 'R4', 'q', True, None) | 100 | -0.31 | [-0.92, +0.17] | 81% |
| reader/chooser | flash | ('oneply', 'ctrl', None, True, None) | 100 | +2.63 | [+0.56, +4.96] | 50% |
| reader/chooser | sonnet | ('chooser', 'R0', None, True, 'high') | 100 | +4.47 | [+1.59, +7.38] | 39% |
| reader/chooser | sonnet | ('chooser', 'R0', None, True, 'low') | 100 | +2.10 | [-0.83, +4.83] | 46% |
| reader/chooser | sonnet | ('chooser', 'R0', None, True, None) | 100 | +1.82 | [-0.64, +4.28] | 48% |
| reader/chooser | sonnet | ('chooser', 'R1', 'q/d0', False, None) | 100 | +6.24 | [+3.03, +9.56] | 65% |
| reader/chooser | sonnet | ('chooser', 'R1', 'q/d0', True, None) | 100 | +4.11 | [+1.97, +6.68] | 55% |
| reader/chooser | sonnet | ('chooser', 'R1', 'q/d1/qwen/prose', True, None) | 98 | +2.28 | [+0.37, +4.48] | 56% |
| reader/chooser | sonnet | ('chooser', 'R2', 'q/d0', False, None) | 100 | +6.32 | [+3.47, +9.26] | 67% |
| reader/chooser | sonnet | ('chooser', 'R2', 'q/d0', True, None) | 100 | +4.22 | [+1.66, +6.94] | 57% |
| reader/chooser | sonnet | ('chooser', 'R2', 'q/d1/qwen/prose', True, None) | 98 | +4.15 | [+1.53, +6.94] | 59% |
| reader/chooser | sonnet | ('chooser', 'R3', 'q/d0', False, None) | 100 | +0.43 | [+0.00, +1.11] | 98% |
| reader/chooser | sonnet | ('chooser', 'R3', 'q/d0', True, None) | 100 | +2.28 | [-0.00, +4.50] | 73% |
| reader/chooser | sonnet | ('chooser', 'R3', 'q/d1/minimax', True, None) | 100 | +3.03 | [+1.14, +5.30] | 78% |
| reader/chooser | sonnet | ('chooser', 'R4', 'q/d0', False, None) | 100 | +1.49 | [+0.20, +3.04] | 92% |
| reader/chooser | sonnet | ('chooser', 'R4', 'q/d0', True, 'high') | 100 | +0.62 | [-1.02, +2.37] | 79% |
| reader/chooser | sonnet | ('chooser', 'R4', 'q/d0', True, 'low') | 100 | +2.29 | [+1.00, +3.75] | 70% |
| reader/chooser | sonnet | ('chooser', 'R4', 'q/d0', True, None) | 100 | +2.35 | [+0.78, +4.11] | 76% |
| reader/chooser | sonnet | ('chooser', 'R4', 'q/d1/qwen/full', True, None) | 93 | +2.99 | [+0.51, +5.61] | 68% |
| reader/chooser | sonnet | ('depth', 'R2', 'q/d0', False, None) | 100 | +0.25 | [+0.00, +0.75] | 99% |
| reader/chooser | sonnet | ('depth', 'R2', 'q/d0', True, None) | 100 | +1.54 | [+0.34, +3.14] | 84% |
| reader/chooser | sonnet | ('depth', 'R2', 'q/d1/qwen/full', True, None) | 94 | -0.21 | [-2.62, +2.29] | 81% |
| reader/chooser | sonnet | ('depth', 'R2', 'q/d1/qwen/prose', True, None) | 98 | -0.18 | [-1.74, +1.33] | 93% |
| reader/chooser | sonnet | ('depth', 'R4', 'q/d0', False, None) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| reader/chooser | sonnet | ('depth', 'R4', 'q/d0', True, None) | 100 | +0.37 | [+0.00, +0.99] | 98% |
| reader/chooser | sonnet | ('depth', 'R4', 'q/d1/qwen/full', True, None) | 93 | +0.12 | [-1.01, +1.15] | 96% |
| reader/chooser | sonnet | ('depth', 'ctrl', None, True, None) | 100 | +2.24 | [-0.48, +4.92] | 42% |
| reader/chooser | sonnet | ('oneply', 'R2', 'q', False, None) | 100 | +0.42 | [-0.30, +1.27] | 79% |
| reader/chooser | sonnet | ('oneply', 'R2', 'q', True, None) | 100 | -0.47 | [-2.04, +1.25] | 66% |
| reader/chooser | sonnet | ('oneply', 'R4', 'q', False, None) | 100 | -0.10 | [-0.24, +0.02] | 88% |
| reader/chooser | sonnet | ('oneply', 'R4', 'q', True, None) | 100 | +1.86 | [+0.21, +3.72] | 70% |
| reader/chooser | sonnet | ('oneply', 'ctrl', None, True, None) | 100 | +1.54 | [-0.23, +3.62] | 54% |
| reader/chooser | flash | ALL CELLS (per-position mean) | 100 | -0.48 | [-0.97, +0.02] |  |
| reader/chooser | sonnet | ALL CELLS (per-position mean) | 100 | +1.95 | [+1.50, +2.44] |  |
| hybrid writer | flash | ('chooser', 'R2', 'd0', 'opus', True) | 98 | +0.03 | [-2.19, +2.19] | 79% |
| hybrid writer | flash | ('chooser', 'R2', 'd1/qwen/full', 'opus', True) | 87 | -0.63 | [-2.01, +0.74] | 82% |
| hybrid writer | flash | ('chooser', 'R2', 'd1/qwen/prose', 'opus', True) | 91 | +0.12 | [-1.75, +2.13] | 63% |
| hybrid writer | flash | ('chooser', 'R4', 'd0', 'opus', True) | 98 | +0.62 | [-0.75, +2.10] | 84% |
| hybrid writer | flash | ('chooser', 'R4', 'd1/qwen/full', 'opus', True) | 87 | -0.04 | [-1.08, +0.99] | 83% |
| hybrid writer | flash | ('depth', 'R1', 'd0', 'mech', True) | 98 | +1.24 | [+0.10, +2.58] | 88% |
| hybrid writer | flash | ('depth', 'R1', 'd1/qwen/full', 'mech', True) | 87 | -2.61 | [-4.97, -0.59] | 83% |
| hybrid writer | flash | ('depth', 'R1', 'd1/qwen/prose', 'mech', True) | 91 | +1.24 | [-1.37, +4.04] | 66% |
| hybrid writer | flash | ('depth', 'R2', 'd0', 'opus', True) | 98 | +0.05 | [+0.00, +0.15] | 99% |
| hybrid writer | flash | ('depth', 'R2', 'd0', 'queen', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | flash | ('depth', 'R2', 'd1/qwen/full', 'opus', True) | 87 | -0.27 | [-1.32, +0.50] | 97% |
| hybrid writer | flash | ('depth', 'R2', 'd1/qwen/full', 'queen', True) | 87 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | flash | ('depth', 'R2', 'd1/qwen/prose', 'opus', True) | 91 | +0.90 | [-0.61, +2.64] | 77% |
| hybrid writer | flash | ('depth', 'R2', 'd1/qwen/prose', 'queen', True) | 91 | +0.41 | [-0.53, +1.40] | 77% |
| hybrid writer | flash | ('depth', 'R3', 'd0', 'mech', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | flash | ('depth', 'R3', 'd1/qwen/full', 'mech', True) | 87 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | flash | ('depth', 'R4', 'd0', 'opus', True) | 98 | +0.02 | [+0.00, +0.05] | 99% |
| hybrid writer | flash | ('depth', 'R4', 'd1/qwen/full', 'opus', True) | 87 | -0.98 | [-2.51, -0.00] | 95% |
| hybrid writer | flash | ('oneply', 'R2', '', 'opus', True) | 98 | -0.18 | [-1.46, +1.02] | 74% |
| hybrid writer | flash | ('oneply', 'R2', '', 'queen', True) | 98 | -0.19 | [-0.52, +0.11] | 84% |
| hybrid writer | flash | ('oneply', 'R4', '', 'opus', True) | 98 | +0.11 | [-0.60, +0.62] | 85% |
| hybrid writer | sonnet | ('chooser', 'R2', 'd0', 'opus', True) | 98 | -0.97 | [-2.74, +0.81] | 79% |
| hybrid writer | sonnet | ('chooser', 'R2', 'd1/qwen/full', 'opus', True) | 85 | +1.51 | [+0.24, +3.11] | 86% |
| hybrid writer | sonnet | ('chooser', 'R2', 'd1/qwen/prose', 'opus', True) | 84 | -0.66 | [-2.62, +1.14] | 75% |
| hybrid writer | sonnet | ('chooser', 'R4', 'd0', 'opus', True) | 98 | +1.16 | [-0.19, +2.89] | 84% |
| hybrid writer | sonnet | ('chooser', 'R4', 'd1/qwen/full', 'opus', True) | 85 | +1.42 | [-0.43, +3.51] | 76% |
| hybrid writer | sonnet | ('depth', 'R1', 'd0', 'mech', True) | 98 | -0.02 | [-0.57, +0.50] | 98% |
| hybrid writer | sonnet | ('depth', 'R1', 'd1/qwen/full', 'mech', True) | 85 | -1.53 | [-3.60, +0.36] | 84% |
| hybrid writer | sonnet | ('depth', 'R1', 'd1/qwen/prose', 'mech', True) | 84 | -2.10 | [-4.99, +0.71] | 77% |
| hybrid writer | sonnet | ('depth', 'R2', 'd0', 'opus', True) | 98 | +0.43 | [+0.00, +1.23] | 98% |
| hybrid writer | sonnet | ('depth', 'R2', 'd0', 'queen', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | sonnet | ('depth', 'R2', 'd1/qwen/full', 'opus', True) | 85 | -0.05 | [-1.37, +1.28] | 93% |
| hybrid writer | sonnet | ('depth', 'R2', 'd1/qwen/full', 'queen', True) | 85 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | sonnet | ('depth', 'R2', 'd1/qwen/prose', 'opus', True) | 84 | +0.07 | [-0.53, +0.91] | 93% |
| hybrid writer | sonnet | ('depth', 'R2', 'd1/qwen/prose', 'queen', True) | 84 | -0.06 | [-0.14, +0.00] | 96% |
| hybrid writer | sonnet | ('depth', 'R3', 'd0', 'mech', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | sonnet | ('depth', 'R3', 'd1/qwen/full', 'mech', True) | 85 | +0.00 | [+0.00, +0.00] | 100% |
| hybrid writer | sonnet | ('depth', 'R4', 'd0', 'opus', True) | 98 | +1.00 | [+0.15, +2.27] | 93% |
| hybrid writer | sonnet | ('depth', 'R4', 'd1/qwen/full', 'opus', True) | 85 | -0.13 | [-1.66, +1.23] | 93% |
| hybrid writer | sonnet | ('oneply', 'R2', '', 'opus', True) | 94 | +0.86 | [-0.56, +2.23] | 68% |
| hybrid writer | sonnet | ('oneply', 'R2', '', 'queen', True) | 94 | +0.20 | [-0.22, +0.74] | 82% |
| hybrid writer | sonnet | ('oneply', 'R4', '', 'opus', True) | 94 | +1.24 | [+0.33, +2.44] | 78% |
| hybrid writer | flash | ALL CELLS (per-position mean) | 100 | +0.02 | [-0.36, +0.37] |  |
| hybrid writer | sonnet | ALL CELLS (per-position mean) | 100 | +0.11 | [-0.16, +0.38] |  |
| consolidator | flash | ('chooser', 'R2', 'd1', 'full', 'opus', True) | 99 | -0.18 | [-1.21, +0.84] | 89% |
| consolidator | flash | ('chooser', 'R2', 'd1', 'prose', 'opus', True) | 99 | -0.65 | [-1.90, +0.70] | 83% |
| consolidator | flash | ('chooser', 'R2', 'rw', 'full', 'opus', True) | 100 | -0.28 | [-2.03, +1.54] | 72% |
| consolidator | flash | ('chooser', 'R2', 'rw', 'prose', 'opus', True) | 100 | -0.34 | [-2.02, +1.25] | 82% |
| consolidator | flash | ('chooser', 'R4', 'd1', 'full', 'opus', True) | 99 | +0.34 | [-0.27, +1.25] | 93% |
| consolidator | flash | ('chooser', 'R4', 'rw', 'full', 'opus', True) | 100 | -0.92 | [-2.15, +0.09] | 85% |
| consolidator | flash | ('depth', 'R1', 'd1', 'full', 'mech', True) | 99 | -0.69 | [-2.02, +0.63] | 89% |
| consolidator | flash | ('depth', 'R1', 'd1', 'prose', 'mech', True) | 99 | +0.66 | [-0.98, +2.59] | 80% |
| consolidator | flash | ('depth', 'R1', 'rw', 'full', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R1', 'rw', 'prose', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R2', 'd1', 'full', 'opus', True) | 99 | +0.06 | [+0.00, +0.18] | 99% |
| consolidator | flash | ('depth', 'R2', 'd1', 'full', 'queen', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R2', 'd1', 'prose', 'opus', True) | 99 | -0.35 | [-0.84, +0.01] | 91% |
| consolidator | flash | ('depth', 'R2', 'd1', 'prose', 'queen', True) | 99 | -0.32 | [-0.80, +0.06] | 90% |
| consolidator | flash | ('depth', 'R2', 'rw', 'full', 'opus', True) | 100 | -0.56 | [-1.34, -0.03] | 95% |
| consolidator | flash | ('depth', 'R2', 'rw', 'full', 'queen', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R2', 'rw', 'prose', 'opus', True) | 100 | +0.02 | [-0.06, +0.13] | 98% |
| consolidator | flash | ('depth', 'R2', 'rw', 'prose', 'queen', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R3', 'd1', 'full', 'mech', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R3', 'rw', 'full', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R4', 'd1', 'full', 'opus', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | flash | ('depth', 'R4', 'rw', 'full', 'opus', True) | 100 | -0.18 | [-0.56, +0.01] | 98% |
| consolidator | qwen | ('chooser', 'R2', 'd1', 'prose', 'opus', True) | 97 | +1.43 | [-0.35, +3.60] | 70% |
| consolidator | qwen | ('chooser', 'R2', 'rw', 'full', 'opus', True) | 100 | +0.05 | [-1.07, +0.98] | 83% |
| consolidator | qwen | ('chooser', 'R2', 'rw', 'prose', 'opus', True) | 98 | +0.75 | [-0.98, +2.64] | 77% |
| consolidator | qwen | ('chooser', 'R4', 'd1', 'full', 'opus', True) | 92 | +0.85 | [-0.38, +2.52] | 88% |
| consolidator | qwen | ('chooser', 'R4', 'rw', 'full', 'opus', True) | 99 | -0.77 | [-1.88, +0.18] | 84% |
| consolidator | qwen | ('depth', 'R1', 'd1', 'full', 'mech', True) | 93 | -0.99 | [-2.25, -0.08] | 95% |
| consolidator | qwen | ('depth', 'R1', 'd1', 'prose', 'mech', True) | 97 | +0.32 | [-1.04, +1.65] | 69% |
| consolidator | qwen | ('depth', 'R1', 'rw', 'full', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R1', 'rw', 'prose', 'mech', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R2', 'd1', 'full', 'opus', True) | 93 | +2.02 | [+0.37, +3.95] | 92% |
| consolidator | qwen | ('depth', 'R2', 'd1', 'full', 'queen', True) | 93 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R2', 'd1', 'prose', 'opus', True) | 97 | +1.29 | [+0.23, +2.58] | 77% |
| consolidator | qwen | ('depth', 'R2', 'd1', 'prose', 'queen', True) | 97 | +0.52 | [-0.08, +1.25] | 78% |
| consolidator | qwen | ('depth', 'R2', 'rw', 'full', 'opus', True) | 100 | -0.26 | [-0.66, +0.00] | 95% |
| consolidator | qwen | ('depth', 'R2', 'rw', 'full', 'queen', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R2', 'rw', 'prose', 'opus', True) | 98 | +0.66 | [+0.05, +1.46] | 94% |
| consolidator | qwen | ('depth', 'R2', 'rw', 'prose', 'queen', True) | 98 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R3', 'd1', 'full', 'mech', True) | 92 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R3', 'rw', 'full', 'mech', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | qwen | ('depth', 'R4', 'd1', 'full', 'opus', True) | 92 | +0.39 | [-0.12, +1.23] | 97% |
| consolidator | qwen | ('depth', 'R4', 'rw', 'full', 'opus', True) | 99 | -0.19 | [-0.56, +0.01] | 98% |
| consolidator | sonnet | ('chooser', 'R2', 'd1', 'full', 'opus', True) | 99 | +0.65 | [-0.77, +2.18] | 89% |
| consolidator | sonnet | ('chooser', 'R2', 'd1', 'prose', 'opus', True) | 99 | +0.53 | [-0.77, +2.03] | 69% |
| consolidator | sonnet | ('chooser', 'R2', 'rw', 'full', 'opus', True) | 100 | -0.20 | [-1.75, +1.27] | 77% |
| consolidator | sonnet | ('chooser', 'R2', 'rw', 'prose', 'opus', True) | 100 | +0.32 | [-1.60, +2.49] | 77% |
| consolidator | sonnet | ('chooser', 'R4', 'd1', 'full', 'opus', True) | 99 | +0.87 | [+0.07, +2.15] | 86% |
| consolidator | sonnet | ('chooser', 'R4', 'rw', 'full', 'opus', True) | 100 | -0.34 | [-1.83, +1.45] | 84% |
| consolidator | sonnet | ('depth', 'R1', 'd1', 'full', 'mech', True) | 99 | +5.31 | [+2.57, +8.12] | 54% |
| consolidator | sonnet | ('depth', 'R1', 'd1', 'prose', 'mech', True) | 99 | +2.92 | [+0.54, +5.73] | 53% |
| consolidator | sonnet | ('depth', 'R1', 'rw', 'full', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R1', 'rw', 'prose', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R2', 'd1', 'full', 'opus', True) | 99 | +0.02 | [+0.00, +0.05] | 99% |
| consolidator | sonnet | ('depth', 'R2', 'd1', 'full', 'queen', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R2', 'd1', 'prose', 'opus', True) | 99 | +1.22 | [+0.52, +2.08] | 75% |
| consolidator | sonnet | ('depth', 'R2', 'd1', 'prose', 'queen', True) | 99 | +1.48 | [+0.59, +2.65] | 74% |
| consolidator | sonnet | ('depth', 'R2', 'rw', 'full', 'opus', True) | 100 | +0.23 | [-0.53, +1.29] | 95% |
| consolidator | sonnet | ('depth', 'R2', 'rw', 'full', 'queen', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R2', 'rw', 'prose', 'opus', True) | 100 | +0.03 | [-0.06, +0.15] | 98% |
| consolidator | sonnet | ('depth', 'R2', 'rw', 'prose', 'queen', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R3', 'd1', 'full', 'mech', True) | 99 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R3', 'rw', 'full', 'mech', True) | 100 | +0.00 | [+0.00, +0.00] | 100% |
| consolidator | sonnet | ('depth', 'R4', 'd1', 'full', 'opus', True) | 99 | +0.14 | [+0.00, +0.40] | 98% |
| consolidator | sonnet | ('depth', 'R4', 'rw', 'full', 'opus', True) | 100 | +0.12 | [-0.56, +0.91] | 97% |
| consolidator | flash | ALL CELLS (per-position mean) | 100 | -0.16 | [-0.37, +0.05] |  |
| consolidator | qwen | ALL CELLS (per-position mean) | 100 | +0.28 | [+0.05, +0.53] |  |
| consolidator | sonnet | ALL CELLS (per-position mean) | 100 | +0.59 | [+0.26, +0.94] |  |

## Failure, child-failure and truncation rates

| agent | failed decisions (scored as random) | one-ply children failed | Queen reads truncated |
|---|---|---|---|
| flash | 0.4% (11/2974) | 0.0% (0/1500) | – |
| hce | 0.0% (0/200) | – | – |
| mech | 0.3% (13/4209) | – | – |
| opus | 0.1% (10/10606) | 0.0% (1/3252) | – |
| queen | 0.0% (0/2935) | 0.0% (0/1176) | 0.0% (1/3719) |
| sonnet | 0.4% (11/2974) | 0.2% (3/1500) | – |

## Where the shared tree's children come from

Positions: 100. Children supplied by Queen (rest topped up by move_priority), count of positions by number: 0: 0, 1: 0, 2: 0, 3: 100.
BEST_MOVE legal: 100%. PROMISING_MOVES written per position: 3.00, legal: 2.99 (0% illegal). Distinct legal root moves in ANALYSIS: 4.70.

## Health (debugging counts)

### API calls

| model/role | calls | errors by kind | refusals | cut off at token limit | empty | p50 s | p95 s |
|---|---|---|---|---|---|---|---|
| flash/chooser | 1933 | – | 0 | 11 | 1 | 9.47 | 92.28 |
| flash/consolidator | 246 | – | 0 | 0 | 0 | 22.11 | 42.33 |
| flash/reader | 2584 | – | 0 | 0 | 0 | 3.85 | 15.12 |
| flash/rewrite | 200 | – | 0 | 0 | 0 | 18.87 | 38.68 |
| flash/writer | 500 | – | 0 | 0 | 0 | 15.77 | 27.21 |
| opus/chooser | 6412 | – | 7 | 0 | 7 | 7.44 | 16.35 |
| opus/consolidator | 246 | – | 0 | 0 | 0 | 31.64 | 41.63 |
| opus/reader | 9243 | – | 0 | 0 | 0 | 4.78 | 12.22 |
| opus/rewrite | 200 | – | 0 | 0 | 0 | 16.85 | 23.42 |
| opus/writer | 500 | – | 0 | 0 | 0 | 26.34 | 38.68 |
| sonnet/chooser | 1933 | – | 0 | 1 | 0 | 6.68 | 13.12 |
| sonnet/consolidator | 246 | – | 0 | 0 | 0 | 13.25 | 17.01 |
| sonnet/reader | 2584 | – | 0 | 0 | 0 | 2.63 | 9.60 |
| sonnet/rewrite | 200 | – | 0 | 0 | 0 | 10.98 | 16.07 |
| sonnet/writer | 500 | – | 0 | 0 | 0 | 12.27 | 17.03 |

### Queen generations (roots and children)

n=400; cut off at 2048 tokens: 0.0% (0/400); median tokens: 701
No ANALYSIS: 0.0% (0/400); BEST_MOVE missing or illegal: 0.2% (1/400); CRITICAL_LINE hits an illegal move: 5.5% (22/400); CRITICAL_LINE empty: 0.2% (1/400)
EVALUATION unparsed: 0.0% (0/400); how its sign was read: {'player_up_down': 344, 'explicit_perspective': 41, 'named_favored_side': 14, 'white_pov_fallback': 1} (white_pov_fallback means no side was named, so the sign may be wrong)
Root evaluations whose sign agrees with Stockfish, by method (positions not near equal): {'explicit_perspective': '4/5', 'player_up_down': '58/61', 'named_favored_side': '1/1'}

Queen reads: n=4457, cut off: 0.0% (0/4457). Qwen: n=1294, cut off: 0.0% (0/1294), output tokens p50/p95: 3118/13777.

### Writers

| writer | outputs | unusable (by reason) | length / target p10, p50, p90 | full: BEST_MOVE = minimax |
|---|---|---|---|---|
| flash | 800 | {'vocabulary': 3} | 0.91, 1.03, 1.21 | 100/100 |
| opus | 800 | {'vocabulary': 3} | 1.00, 1.11, 1.26 | 99/99 |
| qwen | 400 | {'vocabulary': 6, 'no ANALYSIS field': 4} | 0.85, 1.00, 1.10 | 93/93 |
| sonnet | 800 | {'vocabulary': 7} | 0.96, 1.04, 1.13 | 100/100 |

### Decision statuses

| agent | statuses |
|---|---|
| flash | {'ok': 2963, 'unparseable': 11} |
| hce | {'ok': 200} |
| mech | {'ok': 4196, 'empty': 13} |
| opus | {'ok': 10596, 'unparseable': 4, 'illegal': 6} |
| queen | {'ok': 2935} |
| sonnet | {'ok': 2963, 'unparseable': 10, 'illegal': 1} |

## Writer output Queen can read

| writer | readable |
|---|---|
| flash | 797/800 (100%) |
| opus | 797/800 (100%) |
| qwen | 948/984 (96%) |
| sonnet | 793/800 (99%) |

## API cost by model and role

| model/role | calls | errors | refusals | $ | $/call | mean in | mean out |
|---|---|---|---|---|---|---|---|
| flash/chooser | 1933 | 0 | 0 | 16.15 | 0.0084 | 648 | 2099 |
| flash/consolidator | 246 | 0 | 0 | 4.34 | 0.0176 | 5058 | 3691 |
| flash/reader | 2584 | 0 | 0 | 5.45 | 0.0021 | 982 | 366 |
| flash/rewrite | 200 | 0 | 0 | 2.56 | 0.0128 | 1820 | 3053 |
| flash/writer | 500 | 0 | 0 | 3.87 | 0.0077 | 743 | 1915 |
| opus/chooser | 6412 | 0 | 7 | 116.27 | 0.0181 | 1331 | 640 |
| opus/consolidator | 246 | 0 | 0 | 27.64 | 0.1123 | 8256 | 3966 |
| opus/reader | 9243 | 0 | 0 | 135.13 | 0.0146 | 1513 | 428 |
| opus/rewrite | 200 | 0 | 0 | 11.39 | 0.0569 | 2986 | 2250 |
| opus/writer | 500 | 0 | 0 | 28.50 | 0.0570 | 1206 | 2609 |
| sonnet/chooser | 1933 | 0 | 0 | 17.63 | 0.0091 | 915 | 729 |
| sonnet/consolidator | 246 | 0 | 0 | 9.36 | 0.0380 | 8256 | 2152 |
| sonnet/reader | 2584 | 0 | 0 | 17.07 | 0.0066 | 1367 | 387 |
| sonnet/rewrite | 200 | 0 | 0 | 5.43 | 0.0272 | 2986 | 2120 |
| sonnet/writer | 500 | 0 | 0 | 8.97 | 0.0179 | 1206 | 1553 |

## GPU

Queen: {'requests': 4857, 'mean_output_tokens': 143.7465513691579, 'p90_output_tokens': 117, 'generation_seconds': 690.2794292476028, 'requests_per_gpu_hour': 25330.61142943037}

Qwen: {'requests': 1294, 'mean_output_tokens': 4646.968315301391, 'p90_output_tokens': 10472, 'generation_seconds': 6880.528842135798, 'requests_per_gpu_hour': 677.0409814246163}

## All cells

| cell | n | regret | 95% CI | regret (successes) | fail% | child fail% | trunc% | top-1% |
|---|---|---|---|---|---|---|---|---|
| chooser | R0 | - | flash | 100 | 5.87 | [+3.89, +8.08] | 5.87 | 0 | – | – | 46 |
| chooser | R0 | - | flash | effort=high | 100 | 8.03 | [+5.60, +10.82] | 7.17 | 4 | – | – | 42 |
| chooser | R0 | - | flash | effort=low | 100 | 6.17 | [+4.21, +8.55] | 6.17 | 0 | – | – | 51 |
| chooser | R0 | - | opus | 100 | 7.88 | [+5.51, +10.28] | 7.62 | 1 | – | – | 39 |
| chooser | R0 | - | opus | effort=high | 100 | 6.52 | [+4.73, +8.46] | 6.52 | 0 | – | – | 37 |
| chooser | R0 | - | opus | effort=low | 100 | 9.35 | [+6.81, +12.16] | 9.35 | 0 | – | – | 31 |
| chooser | R0 | - | sonnet | 100 | 9.70 | [+7.34, +12.14] | 9.61 | 1 | – | – | 30 |
| chooser | R0 | - | sonnet | effort=high | 100 | 11.00 | [+8.49, +13.55] | 10.74 | 4 | – | – | 23 |
| chooser | R0 | - | sonnet | effort=low | 100 | 11.45 | [+8.66, +14.32] | 11.38 | 1 | – | – | 27 |
| chooser | R1 | q/d0 | flash | 100 | 3.05 | [+1.74, +4.53] | 3.05 | 0 | – | – | 58 |
| chooser | R1 | q/d0 | flash | noFEN | 100 | 3.34 | [+2.13, +4.79] | 3.18 | 1 | – | – | 51 |
| chooser | R1 | q/d0 | opus | 100 | 5.05 | [+3.49, +6.80] | 5.05 | 0 | – | – | 44 |
| chooser | R1 | q/d0 | opus | noFEN | 100 | 4.44 | [+2.75, +6.33] | 4.44 | 0 | – | – | 49 |
| chooser | R1 | q/d0 | sonnet | 100 | 9.16 | [+6.65, +12.03] | 9.16 | 0 | – | – | 33 |
| chooser | R1 | q/d0 | sonnet | noFEN | 100 | 10.67 | [+7.35, +14.38] | 10.67 | 0 | – | – | 40 |
| chooser | R1 | q/d1/qwen/prose | flash | 98 | 2.66 | [+1.62, +3.82] | 2.66 | 0 | – | – | 58 |
| chooser | R1 | q/d1/qwen/prose | opus | 98 | 5.24 | [+3.45, +7.22] | 5.24 | 0 | – | – | 48 |
| chooser | R1 | q/d1/qwen/prose | sonnet | 98 | 7.53 | [+5.35, +9.92] | 7.43 | 1 | – | – | 35 |
| chooser | R2 | h-flash/d0 | opus | 99 | 4.16 | [+2.63, +5.95] | 4.16 | 0 | – | – | 46 |
| chooser | R2 | h-flash/d1/qwen/full | opus | 93 | 1.67 | [+0.80, +2.76] | 1.67 | 0 | – | – | 65 |
| chooser | R2 | h-flash/d1/qwen/prose | opus | 96 | 3.08 | [+1.85, +4.61] | 3.08 | 0 | – | – | 52 |
| chooser | R2 | h-opus/d0 | opus | 99 | 4.12 | [+2.50, +6.07] | 3.72 | 1 | – | – | 54 |
| chooser | R2 | h-opus/d1/qwen/full | opus | 93 | 2.35 | [+1.29, +3.62] | 2.35 | 0 | – | – | 60 |
| chooser | R2 | h-opus/d1/qwen/prose | opus | 95 | 3.11 | [+1.79, +4.62] | 2.82 | 1 | – | – | 54 |
| chooser | R2 | h-sonnet/d0 | opus | 99 | 3.18 | [+2.03, +4.52] | 3.18 | 0 | – | – | 55 |
| chooser | R2 | h-sonnet/d1/qwen/full | opus | 92 | 3.49 | [+1.94, +5.45] | 3.49 | 0 | – | – | 58 |
| chooser | R2 | h-sonnet/d1/qwen/prose | opus | 89 | 2.28 | [+1.19, +3.76] | 2.28 | 0 | – | – | 57 |
| chooser | R2 | q/d0 | flash | 100 | 3.67 | [+2.15, +5.46] | 3.67 | 0 | – | – | 57 |
| chooser | R2 | q/d0 | flash | noFEN | 100 | 2.05 | [+1.23, +3.16] | 2.05 | 0 | – | – | 55 |
| chooser | R2 | q/d0 | opus | 100 | 3.68 | [+2.01, +5.57] | 3.38 | 1 | – | – | 55 |
| chooser | R2 | q/d0 | opus | noFEN | 100 | 2.90 | [+1.70, +4.30] | 2.90 | 0 | – | – | 53 |
| chooser | R2 | q/d0 | sonnet | 100 | 7.90 | [+5.58, +10.31] | 7.64 | 1 | – | – | 40 |
| chooser | R2 | q/d0 | sonnet | noFEN | 100 | 9.22 | [+6.25, +12.36] | 9.22 | 0 | – | – | 43 |
| chooser | R2 | q/d1/flash/full | opus | 100 | 1.52 | [+0.79, +2.47] | 1.52 | 0 | – | – | 63 |
| chooser | R2 | q/d1/flash/prose | opus | 100 | 2.23 | [+1.12, +3.47] | 2.23 | 0 | – | – | 60 |
| chooser | R2 | q/d1/opus/full | opus | 99 | 1.66 | [+0.97, +2.61] | 1.66 | 0 | – | – | 58 |
| chooser | R2 | q/d1/opus/prose | opus | 99 | 2.90 | [+1.73, +4.19] | 2.90 | 0 | – | – | 53 |
| chooser | R2 | q/d1/qwen/prose | flash | 98 | 3.50 | [+2.10, +5.33] | 3.50 | 0 | – | – | 56 |
| chooser | R2 | q/d1/qwen/prose | opus | 98 | 4.34 | [+2.58, +6.58] | 4.34 | 0 | – | – | 54 |
| chooser | R2 | q/d1/qwen/prose | sonnet | 98 | 8.50 | [+6.05, +11.33] | 8.50 | 0 | – | – | 39 |
| chooser | R2 | q/d1/sonnet/full | opus | 100 | 2.50 | [+1.28, +4.08] | 2.50 | 0 | – | – | 58 |
| chooser | R2 | q/d1/sonnet/prose | opus | 100 | 3.40 | [+2.16, +4.93] | 3.40 | 0 | – | – | 50 |
| chooser | R2 | q/rw/flash/full | opus | 100 | 3.40 | [+2.04, +5.01] | 3.40 | 0 | – | – | 54 |
| chooser | R2 | q/rw/flash/prose | opus | 100 | 3.61 | [+2.12, +5.22] | 3.61 | 0 | – | – | 53 |
| chooser | R2 | q/rw/opus/full | opus | 100 | 3.68 | [+2.24, +5.36] | 3.68 | 0 | – | – | 51 |
| chooser | R2 | q/rw/opus/prose | opus | 100 | 3.95 | [+2.46, +5.64] | 3.68 | 1 | – | – | 51 |
| chooser | R2 | q/rw/qwen/full | opus | 100 | 3.73 | [+2.38, +5.24] | 3.73 | 0 | – | – | 52 |
| chooser | R2 | q/rw/qwen/prose | opus | 98 | 4.77 | [+3.11, +6.71] | 4.77 | 0 | – | – | 49 |
| chooser | R2 | q/rw/sonnet/full | opus | 100 | 3.48 | [+2.08, +5.06] | 3.48 | 0 | – | – | 54 |
| chooser | R2 | q/rw/sonnet/prose | opus | 100 | 4.27 | [+2.49, +6.40] | 3.96 | 1 | – | – | 54 |
| chooser | R3 | q/d0 | flash | 100 | 2.22 | [+1.33, +3.36] | 2.22 | 0 | – | – | 55 |
| chooser | R3 | q/d0 | flash | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| chooser | R3 | q/d0 | opus | 100 | 2.57 | [+1.35, +4.34] | 2.57 | 0 | – | – | 55 |
| chooser | R3 | q/d0 | opus | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| chooser | R3 | q/d0 | sonnet | 100 | 4.86 | [+2.83, +7.12] | 4.86 | 0 | – | – | 47 |
| chooser | R3 | q/d0 | sonnet | noFEN | 100 | 2.33 | [+1.36, +3.52] | 2.33 | 0 | – | – | 54 |
| chooser | R3 | q/d1/minimax | flash | 100 | 1.56 | [+0.78, +2.60] | 1.56 | 0 | – | – | 64 |
| chooser | R3 | q/d1/minimax | opus | 100 | 1.52 | [+0.85, +2.39] | 1.52 | 0 | – | – | 60 |
| chooser | R3 | q/d1/minimax | sonnet | 100 | 4.55 | [+2.71, +6.83] | 4.55 | 0 | – | – | 52 |
| chooser | R4 | h-flash/d0 | opus | 99 | 3.29 | [+2.02, +4.89] | 3.29 | 0 | – | – | 54 |
| chooser | R4 | h-flash/d1/qwen/full | opus | 93 | 1.73 | [+1.03, +2.56] | 1.73 | 0 | – | – | 62 |
| chooser | R4 | h-opus/d0 | opus | 99 | 2.67 | [+1.55, +3.92] | 2.67 | 0 | – | – | 55 |
| chooser | R4 | h-opus/d1/qwen/full | opus | 93 | 2.12 | [+1.32, +3.10] | 2.12 | 0 | – | – | 60 |
| chooser | R4 | h-sonnet/d0 | opus | 99 | 3.84 | [+2.27, +5.73] | 3.84 | 0 | – | – | 56 |
| chooser | R4 | h-sonnet/d1/qwen/full | opus | 92 | 3.31 | [+1.74, +5.10] | 3.31 | 0 | – | – | 59 |
| chooser | R4 | q/d0 | flash | 100 | 3.82 | [+2.23, +5.74] | 3.82 | 0 | – | – | 56 |
| chooser | R4 | q/d0 | flash | effort=high | 100 | 3.62 | [+2.19, +5.41] | 2.37 | 6 | – | – | 55 |
| chooser | R4 | q/d0 | flash | effort=low | 100 | 2.78 | [+1.55, +4.20] | 2.78 | 0 | – | – | 59 |
| chooser | R4 | q/d0 | flash | noFEN | 100 | 2.01 | [+1.18, +3.13] | 2.01 | 0 | – | – | 56 |
| chooser | R4 | q/d0 | opus | 100 | 2.35 | [+1.38, +3.53] | 2.35 | 0 | – | – | 54 |
| chooser | R4 | q/d0 | opus | effort=high | 100 | 2.77 | [+1.57, +4.12] | 2.77 | 0 | – | – | 55 |
| chooser | R4 | q/d0 | opus | effort=low | 100 | 2.12 | [+1.27, +3.22] | 2.12 | 0 | – | – | 56 |
| chooser | R4 | q/d0 | opus | noFEN | 100 | 2.00 | [+1.19, +3.09] | 2.00 | 0 | – | – | 56 |
| chooser | R4 | q/d0 | sonnet | 100 | 4.70 | [+3.02, +6.76] | 4.38 | 1 | – | – | 47 |
| chooser | R4 | q/d0 | sonnet | effort=high | 100 | 3.38 | [+1.99, +5.06] | 3.38 | 0 | – | – | 53 |
| chooser | R4 | q/d0 | sonnet | effort=low | 100 | 4.41 | [+2.90, +6.10] | 4.29 | 1 | – | – | 46 |
| chooser | R4 | q/d0 | sonnet | noFEN | 100 | 3.49 | [+1.95, +5.24] | 3.49 | 0 | – | – | 52 |
| chooser | R4 | q/d1/flash/full | opus | 100 | 1.83 | [+0.84, +3.08] | 1.83 | 0 | – | – | 62 |
| chooser | R4 | q/d1/opus/full | opus | 99 | 1.45 | [+0.79, +2.31] | 1.45 | 0 | – | – | 61 |
| chooser | R4 | q/d1/qwen/full | flash | 93 | 1.85 | [+1.04, +2.77] | 1.85 | 0 | – | – | 61 |
| chooser | R4 | q/d1/qwen/full | opus | 93 | 2.45 | [+1.23, +3.98] | 2.45 | 0 | – | – | 61 |
| chooser | R4 | q/d1/qwen/full | sonnet | 93 | 5.44 | [+3.30, +7.76] | 5.44 | 0 | – | – | 45 |
| chooser | R4 | q/d1/sonnet/full | opus | 100 | 2.35 | [+1.15, +4.03] | 2.35 | 0 | – | – | 58 |
| chooser | R4 | q/rw/flash/full | opus | 100 | 1.93 | [+1.11, +3.01] | 1.93 | 0 | – | – | 58 |
| chooser | R4 | q/rw/opus/full | opus | 100 | 2.85 | [+1.64, +4.28] | 2.85 | 0 | – | – | 53 |
| chooser | R4 | q/rw/qwen/full | opus | 99 | 2.11 | [+1.26, +3.29] | 2.11 | 0 | – | – | 58 |
| chooser | R4 | q/rw/sonnet/full | opus | 100 | 2.51 | [+1.30, +4.30] | 2.51 | 0 | – | – | 55 |
| depth | R0 | - | hce | 100 | 5.01 | [+3.54, +6.59] | 5.01 | 0 | – | – | 40 |
| depth | R1 | h-flash/d0 | mech | 99 | 3.33 | [+1.94, +5.10] | 3.33 | 0 | – | – | 53 |
| depth | R1 | h-flash/d1/qwen/full | mech | 93 | 2.18 | [+1.17, +3.47] | 1.95 | 1 | – | – | 59 |
| depth | R1 | h-flash/d1/qwen/prose | mech | 96 | 7.37 | [+4.81, +10.37] | 6.95 | 2 | – | – | 48 |
| depth | R1 | h-opus/d0 | mech | 99 | 2.09 | [+1.22, +3.17] | 2.09 | 0 | – | – | 56 |
| depth | R1 | h-opus/d1/qwen/full | mech | 93 | 4.64 | [+2.59, +6.88] | 3.13 | 5 | – | – | 55 |
| depth | R1 | h-opus/d1/qwen/prose | mech | 95 | 5.44 | [+3.20, +7.98] | 5.44 | 0 | – | – | 51 |
| depth | R1 | h-sonnet/d0 | mech | 99 | 2.08 | [+1.21, +3.12] | 2.08 | 0 | – | – | 56 |
| depth | R1 | h-sonnet/d1/qwen/full | mech | 92 | 2.99 | [+1.60, +4.79] | 2.35 | 3 | – | – | 55 |
| depth | R1 | h-sonnet/d1/qwen/prose | mech | 89 | 3.58 | [+1.73, +5.90] | 3.58 | 0 | – | – | 60 |
| depth | R1 | q/d0 | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/d1/flash/full | mech | 100 | 1.82 | [+0.91, +2.96] | 1.82 | 0 | – | – | 61 |
| depth | R1 | q/d1/flash/prose | mech | 100 | 3.48 | [+1.98, +5.33] | 3.48 | 0 | – | – | 52 |
| depth | R1 | q/d1/opus/full | mech | 99 | 2.47 | [+1.36, +3.82] | 2.47 | 0 | – | – | 58 |
| depth | R1 | q/d1/opus/prose | mech | 99 | 2.86 | [+1.83, +4.15] | 2.86 | 0 | – | – | 53 |
| depth | R1 | q/d1/qwen/full | mech | 94 | 1.38 | [+0.72, +2.26] | 1.38 | 0 | – | – | 63 |
| depth | R1 | q/d1/qwen/prose | mech | 98 | 3.21 | [+1.98, +4.61] | 2.88 | 1 | – | – | 53 |
| depth | R1 | q/d1/sonnet/full | mech | 100 | 7.75 | [+5.17, +10.68] | 7.50 | 1 | – | – | 41 |
| depth | R1 | q/d1/sonnet/prose | mech | 100 | 5.72 | [+3.72, +8.02] | 5.72 | 0 | – | – | 43 |
| depth | R1 | q/rw/flash/full | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/flash/prose | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/opus/full | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/opus/prose | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/qwen/full | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/qwen/prose | mech | 98 | 2.11 | [+1.20, +3.21] | 2.11 | 0 | – | – | 55 |
| depth | R1 | q/rw/sonnet/full | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R1 | q/rw/sonnet/prose | mech | 100 | 2.08 | [+1.22, +3.20] | 2.08 | 0 | – | – | 55 |
| depth | R2 | h-flash/d0 | opus | 99 | 1.96 | [+1.18, +3.08] | 1.96 | 0 | – | – | 56 |
| depth | R2 | h-flash/d0 | queen | 99 | 1.91 | [+1.13, +3.02] | 1.91 | 0 | – | 0 | 57 |
| depth | R2 | h-flash/d1/qwen/full | opus | 93 | 1.39 | [+0.88, +1.95] | 1.39 | 0 | – | – | 59 |
| depth | R2 | h-flash/d1/qwen/full | queen | 93 | 1.44 | [+0.76, +2.31] | 1.44 | 0 | – | 0 | 61 |
| depth | R2 | h-flash/d1/qwen/prose | opus | 96 | 2.65 | [+1.49, +4.14] | 2.65 | 0 | – | – | 56 |
| depth | R2 | h-flash/d1/qwen/prose | queen | 96 | 2.00 | [+1.23, +2.90] | 2.00 | 0 | – | 0 | 58 |
| depth | R2 | h-opus/d0 | opus | 99 | 1.90 | [+1.11, +2.92] | 1.90 | 0 | – | – | 57 |
| depth | R2 | h-opus/d0 | queen | 99 | 1.90 | [+1.11, +2.92] | 1.90 | 0 | – | 0 | 57 |
| depth | R2 | h-opus/d1/qwen/full | opus | 93 | 1.61 | [+0.79, +2.74] | 1.61 | 0 | – | – | 60 |
| depth | R2 | h-opus/d1/qwen/full | queen | 93 | 1.41 | [+0.73, +2.27] | 1.41 | 0 | – | 0 | 61 |
| depth | R2 | h-opus/d1/qwen/prose | opus | 95 | 1.68 | [+0.85, +2.81] | 1.68 | 0 | – | – | 58 |
| depth | R2 | h-opus/d1/qwen/prose | queen | 95 | 1.50 | [+0.82, +2.40] | 1.50 | 0 | – | 0 | 59 |
| depth | R2 | h-sonnet/d0 | opus | 99 | 2.34 | [+1.32, +3.55] | 2.34 | 0 | – | – | 55 |
| depth | R2 | h-sonnet/d0 | queen | 99 | 1.92 | [+1.12, +2.89] | 1.92 | 0 | – | 0 | 56 |
| depth | R2 | h-sonnet/d1/qwen/full | opus | 92 | 1.50 | [+0.78, +2.56] | 1.50 | 0 | – | – | 62 |
| depth | R2 | h-sonnet/d1/qwen/full | queen | 92 | 1.40 | [+0.71, +2.34] | 1.40 | 0 | – | 0 | 62 |
| depth | R2 | h-sonnet/d1/qwen/prose | opus | 89 | 1.71 | [+0.84, +2.88] | 1.71 | 0 | – | – | 63 |
| depth | R2 | h-sonnet/d1/qwen/prose | queen | 89 | 1.40 | [+0.70, +2.35] | 1.40 | 0 | – | 0 | 64 |
| depth | R2 | q/d0 | flash | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R2 | q/d0 | flash | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R2 | q/d0 | opus | 100 | 2.29 | [+1.27, +3.54] | 2.29 | 0 | – | – | 55 |
| depth | R2 | q/d0 | opus | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R2 | q/d0 | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/d0 | sonnet | 100 | 3.82 | [+2.14, +5.78] | 3.82 | 0 | – | – | 50 |
| depth | R2 | q/d0 | sonnet | noFEN | 100 | 2.15 | [+1.24, +3.34] | 1.89 | 1 | – | – | 56 |
| depth | R2 | q/d1/flash/full | opus | 100 | 1.45 | [+0.79, +2.33] | 1.45 | 0 | – | – | 61 |
| depth | R2 | q/d1/flash/full | queen | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | 0 | 61 |
| depth | R2 | q/d1/flash/prose | opus | 100 | 1.76 | [+0.97, +2.74] | 1.76 | 0 | – | – | 59 |
| depth | R2 | q/d1/flash/prose | queen | 100 | 1.80 | [+1.00, +2.78] | 1.80 | 0 | – | 0 | 58 |
| depth | R2 | q/d1/opus/full | opus | 99 | 1.35 | [+0.70, +2.18] | 1.35 | 0 | – | – | 62 |
| depth | R2 | q/d1/opus/full | queen | 99 | 1.35 | [+0.70, +2.18] | 1.35 | 0 | – | 0 | 62 |
| depth | R2 | q/d1/opus/prose | opus | 99 | 2.13 | [+1.30, +3.19] | 2.13 | 0 | – | – | 55 |
| depth | R2 | q/d1/opus/prose | queen | 99 | 2.13 | [+1.30, +3.19] | 2.13 | 0 | – | 0 | 55 |
| depth | R2 | q/d1/qwen/full | flash | 94 | 1.38 | [+0.72, +2.26] | 1.38 | 0 | – | – | 63 |
| depth | R2 | q/d1/qwen/full | opus | 94 | 3.38 | [+1.61, +5.38] | 2.71 | 2 | – | – | 61 |
| depth | R2 | q/d1/qwen/full | queen | 94 | 1.38 | [+0.72, +2.26] | 1.38 | 0 | – | 1 | 63 |
| depth | R2 | q/d1/qwen/full | sonnet | 94 | 3.17 | [+1.72, +4.97] | 3.17 | 0 | – | – | 56 |
| depth | R2 | q/d1/qwen/prose | flash | 98 | 2.65 | [+1.62, +3.83] | 2.65 | 0 | – | – | 56 |
| depth | R2 | q/d1/qwen/prose | opus | 98 | 3.43 | [+2.10, +5.11] | 3.43 | 0 | – | – | 54 |
| depth | R2 | q/d1/qwen/prose | queen | 98 | 2.67 | [+1.63, +3.84] | 2.67 | 0 | – | 0 | 55 |
| depth | R2 | q/d1/qwen/prose | sonnet | 98 | 3.25 | [+1.89, +4.93] | 3.25 | 0 | – | – | 55 |
| depth | R2 | q/d1/sonnet/full | opus | 100 | 1.41 | [+0.78, +2.27] | 1.41 | 0 | – | – | 60 |
| depth | R2 | q/d1/sonnet/full | queen | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | 0 | 61 |
| depth | R2 | q/d1/sonnet/prose | opus | 100 | 3.32 | [+2.21, +4.65] | 3.32 | 0 | – | – | 50 |
| depth | R2 | q/d1/sonnet/prose | queen | 100 | 3.57 | [+2.32, +5.05] | 3.57 | 0 | – | 0 | 51 |
| depth | R2 | q/rw/flash/full | opus | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R2 | q/rw/flash/full | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/flash/prose | opus | 100 | 1.94 | [+1.13, +3.04] | 1.94 | 0 | – | – | 56 |
| depth | R2 | q/rw/flash/prose | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/opus/full | opus | 100 | 2.45 | [+1.42, +3.74] | 2.45 | 0 | – | – | 54 |
| depth | R2 | q/rw/opus/full | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/opus/prose | opus | 100 | 1.92 | [+1.12, +3.01] | 1.92 | 0 | – | – | 55 |
| depth | R2 | q/rw/opus/prose | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/qwen/full | opus | 100 | 2.20 | [+1.25, +3.45] | 2.20 | 0 | – | – | 56 |
| depth | R2 | q/rw/qwen/full | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/qwen/prose | opus | 98 | 2.60 | [+1.55, +3.84] | 2.60 | 0 | – | – | 52 |
| depth | R2 | q/rw/qwen/prose | queen | 98 | 1.92 | [+1.11, +3.02] | 1.92 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/sonnet/full | opus | 100 | 2.68 | [+1.52, +4.21] | 2.28 | 1 | – | – | 52 |
| depth | R2 | q/rw/sonnet/full | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R2 | q/rw/sonnet/prose | opus | 100 | 1.95 | [+1.15, +3.05] | 1.95 | 0 | – | – | 55 |
| depth | R2 | q/rw/sonnet/prose | queen | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | 0 | 56 |
| depth | R3 | h-flash/d0 | mech | 99 | 1.91 | [+1.13, +3.02] | 1.91 | 0 | – | – | 57 |
| depth | R3 | h-flash/d1/qwen/full | mech | 93 | 1.44 | [+0.76, +2.31] | 1.44 | 0 | – | – | 61 |
| depth | R3 | h-opus/d0 | mech | 99 | 1.90 | [+1.11, +2.92] | 1.90 | 0 | – | – | 57 |
| depth | R3 | h-opus/d1/qwen/full | mech | 93 | 1.41 | [+0.73, +2.27] | 1.41 | 0 | – | – | 61 |
| depth | R3 | h-sonnet/d0 | mech | 99 | 1.92 | [+1.12, +2.89] | 1.92 | 0 | – | – | 56 |
| depth | R3 | h-sonnet/d1/qwen/full | mech | 92 | 1.40 | [+0.71, +2.34] | 1.40 | 0 | – | – | 62 |
| depth | R3 | q/d0 | mech | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R3 | q/d1/flash/full | mech | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | – | 61 |
| depth | R3 | q/d1/minimax | mech | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | – | 61 |
| depth | R3 | q/d1/opus/full | mech | 99 | 1.35 | [+0.70, +2.18] | 1.35 | 0 | – | – | 62 |
| depth | R3 | q/d1/qwen/full | mech | 93 | 1.39 | [+0.68, +2.25] | 1.39 | 0 | – | – | 63 |
| depth | R3 | q/d1/sonnet/full | mech | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | – | 61 |
| depth | R3 | q/rw/flash/full | mech | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R3 | q/rw/opus/full | mech | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R3 | q/rw/qwen/full | mech | 99 | 1.92 | [+1.14, +3.01] | 1.92 | 0 | – | – | 56 |
| depth | R3 | q/rw/sonnet/full | mech | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | h-flash/d0 | opus | 99 | 1.93 | [+1.15, +3.04] | 1.93 | 0 | – | – | 56 |
| depth | R4 | h-flash/d1/qwen/full | opus | 93 | 1.16 | [+0.72, +1.61] | 1.16 | 0 | – | – | 61 |
| depth | R4 | h-opus/d0 | opus | 99 | 1.90 | [+1.11, +2.92] | 1.90 | 0 | – | – | 57 |
| depth | R4 | h-opus/d1/qwen/full | opus | 93 | 2.04 | [+0.91, +3.48] | 2.04 | 0 | – | – | 60 |
| depth | R4 | h-sonnet/d0 | opus | 99 | 2.90 | [+1.65, +4.45] | 2.90 | 0 | – | – | 53 |
| depth | R4 | h-sonnet/d1/qwen/full | opus | 92 | 1.92 | [+0.83, +3.45] | 1.92 | 0 | – | – | 62 |
| depth | R4 | q/d0 | flash | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/d0 | flash | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/d0 | opus | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/d0 | opus | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/d0 | sonnet | 100 | 2.27 | [+1.25, +3.53] | 2.27 | 0 | – | – | 56 |
| depth | R4 | q/d0 | sonnet | noFEN | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/d1/flash/full | opus | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | – | 61 |
| depth | R4 | q/d1/opus/full | opus | 99 | 1.35 | [+0.70, +2.18] | 1.35 | 0 | – | – | 62 |
| depth | R4 | q/d1/qwen/full | flash | 93 | 1.39 | [+0.68, +2.25] | 1.39 | 0 | – | – | 63 |
| depth | R4 | q/d1/qwen/full | opus | 93 | 1.78 | [+0.83, +3.01] | 1.78 | 0 | – | – | 63 |
| depth | R4 | q/d1/qwen/full | sonnet | 93 | 1.90 | [+0.87, +3.11] | 1.90 | 0 | – | – | 61 |
| depth | R4 | q/d1/sonnet/full | opus | 100 | 1.47 | [+0.80, +2.39] | 1.47 | 0 | – | – | 60 |
| depth | R4 | q/rw/flash/full | opus | 100 | 1.90 | [+1.10, +3.00] | 1.90 | 0 | – | – | 56 |
| depth | R4 | q/rw/opus/full | opus | 100 | 2.08 | [+1.23, +3.18] | 2.08 | 0 | – | – | 56 |
| depth | R4 | q/rw/qwen/full | opus | 99 | 1.92 | [+1.14, +3.01] | 1.92 | 0 | – | – | 56 |
| depth | R4 | q/rw/sonnet/full | opus | 100 | 2.20 | [+1.22, +3.46] | 1.88 | 1 | – | – | 56 |
| depth | ctrl | - | flash | 100 | 5.95 | [+4.04, +7.99] | 5.95 | 0 | – | – | 44 |
| depth | ctrl | - | opus | 100 | 8.34 | [+5.99, +10.92] | 8.34 | 0 | – | – | 35 |
| depth | ctrl | - | sonnet | 100 | 10.59 | [+8.04, +13.36] | 10.59 | 0 | – | – | 30 |
| oneply | R0 | - | hce | 100 | 3.58 | [+2.38, +5.02] | 3.58 | 0 | – | – | 47 |
| oneply | R2 | h-flash | opus | 98 | 1.80 | [+1.04, +2.67] | 1.80 | 0 | 0 | – | 59 |
| oneply | R2 | h-flash | queen | 98 | 1.39 | [+0.74, +2.29] | 1.39 | 0 | 0 | 0 | 61 |
| oneply | R2 | h-opus | opus | 100 | 1.97 | [+1.05, +3.24] | 1.97 | 0 | 0 | – | 56 |
| oneply | R2 | h-opus | queen | 100 | 1.58 | [+0.90, +2.49] | 1.58 | 0 | 0 | 0 | 59 |
| oneply | R2 | h-sonnet | opus | 94 | 2.80 | [+1.60, +4.21] | 2.80 | 0 | 0 | – | 55 |
| oneply | R2 | h-sonnet | queen | 94 | 1.76 | [+0.99, +2.75] | 1.76 | 0 | 0 | 0 | 57 |
| oneply | R2 | q | flash | 100 | 2.22 | [+1.32, +3.35] | 2.22 | 0 | 0 | – | 56 |
| oneply | R2 | q | flash | noFEN | 100 | 1.91 | [+1.23, +2.72] | 1.91 | 0 | 0 | – | 57 |
| oneply | R2 | q | opus | 100 | 3.63 | [+2.27, +5.24] | 3.63 | 0 | 0 | – | 48 |
| oneply | R2 | q | opus | noFEN | 100 | 2.19 | [+1.41, +3.12] | 2.19 | 0 | 0 | – | 53 |
| oneply | R2 | q | queen | 100 | 1.43 | [+0.77, +2.30] | 1.43 | 0 | 0 | 0 | 59 |
| oneply | R2 | q | sonnet | 100 | 3.15 | [+1.82, +4.83] | 3.15 | 0 | 0 | – | 53 |
| oneply | R2 | q | sonnet | noFEN | 100 | 2.62 | [+1.69, +3.75] | 2.62 | 0 | 0 | – | 49 |
| oneply | R3 | q | mech | 100 | 1.39 | [+0.76, +2.26] | 1.39 | 0 | – | – | 61 |
| oneply | R4 | h-flash | opus | 98 | 1.28 | [+0.81, +1.77] | 1.28 | 0 | 0 | – | 61 |
| oneply | R4 | h-opus | opus | 100 | 1.17 | [+0.58, +2.06] | 1.17 | 0 | 0 | – | 67 |
| oneply | R4 | h-sonnet | opus | 94 | 2.39 | [+1.30, +3.73] | 2.39 | 0 | 0 | – | 57 |
| oneply | R4 | q | flash | 100 | 1.45 | [+0.81, +2.33] | 1.45 | 0 | 0 | – | 59 |
| oneply | R4 | q | flash | noFEN | 100 | 1.45 | [+0.81, +2.33] | 1.45 | 0 | 0 | – | 59 |
| oneply | R4 | q | opus | 100 | 1.76 | [+0.99, +2.74] | 1.76 | 0 | 0 | – | 57 |
| oneply | R4 | q | opus | noFEN | 100 | 1.58 | [+0.93, +2.50] | 1.58 | 0 | 0 | – | 58 |
| oneply | R4 | q | sonnet | 100 | 3.61 | [+1.94, +5.52] | 3.61 | 0 | 0 | – | 54 |
| oneply | R4 | q | sonnet | noFEN | 100 | 1.48 | [+0.84, +2.38] | 1.48 | 0 | 0 | – | 62 |
| oneply | ctrl | - | flash | 100 | 6.49 | [+4.62, +8.43] | 6.49 | 0 | 0 | – | 34 |
| oneply | ctrl | - | opus | 100 | 3.86 | [+2.53, +5.34] | 3.86 | 0 | 0 | – | 44 |
| oneply | ctrl | - | sonnet | 100 | 5.40 | [+3.67, +7.50] | 5.40 | 0 | 0 | – | 32 |
