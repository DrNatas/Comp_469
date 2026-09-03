# Grading - Six Agents, One Chapter

Total: 100 points.

## Code (60)

| Part | File | Points | How it is checked |
|---|---|---|---|
| 1. Table-driven | `table_driven_agent.py` | 6 | `test_part1_table_driven` |
| 2. Simple reflex | `simple_reflex_agent.py` | 8 | `test_part2_simple_reflex` |
| 3. Model-based reflex | `model_based_agent.py` | 10 | `test_part3_model_based` |
| 4. Goal-based | `goal_based_agent.py` | 10 | `test_part4_goal_based` |
| 5. Utility-based | `utility_based_agent.py` | 18 | `test_part5_utility_based` |
| 6. Learning | `learning_agent.py` | 8 | `test_part6_learning` |

Credit within a part is proportional to the tests it passes, so a
half-finished part still scores. Two things are checked across all six at
once by `test_scope.py` and are folded into each part's score: no
environment access beyond the percept and the static maze, no
hand-written search, and no leftover `TODO(CH2-...)` markers.

Because Part 6 imports Part 5 directly, a broken `UtilityWeights` in Part
5 will make Part 6's file fail to import at all -- finish Part 5 first.

Code quality (comments explain intent, weight names in Part 5 match what
they do, no dead code) is read by hand and factored into the Part 5 and
Part 6 scores above, since those are the two parts with real design
freedom.

## Trials (10)

| Item | Points |
|---|---|
| `results/trials.csv`, `results/summary.csv`, `results/learned_weights.json` present, generated from your six agents | 4 |
| Part 5 (utility-based) win rate at or above 60% on `normal` | 4 |
| Part 5 mean performance beats the `greedy` baseline; Part 6's trained weights beat its own naive starting point | 2 |

## Write-up (30)

| Item | Points |
|---|---|
| PEAS description, all four parts, specific to this environment | 5 |
| Seven environment properties, each justified from the code | 6 |
| Each of the six parts mapped to its AIMA figure, with the one concrete thing it added | 6 |
| Performance measure vs. utility function, located in the code, difference explained | 5 |
| Rational-but-unsuccessful episode, with a seed and a real explanation | 4 |
| Trial table (all six agents, both difficulties) interpreted, tracing the progression across parts | 4 |

## Automatic deductions

| | |
|---|---|
| `pacman/` modified | -20, and regraded against the original package |
| Search algorithm implemented in any of the six files | -10 |
| Third-party dependency added | -5 |
| Submission missing one of the six agent files or the write-up | not gradeable, resubmit late |

## What full marks looks like

A submission that passes every test but whose write-up treats the six
parts as six unrelated homework problems will lose most of item 3 and
some of item 6 in the write-up. The point of building them together is
that each one is a specific, nameable fix to the one before it -- Part 3
adds exactly memory, Part 4 adds exactly a goal test, Part 5 adds exactly
a graded utility function. A strong write-up says which failure each part
fixes and points at the line of code that fixes it, the same way the
original single-agent version of this project asked you to point at
`Simulation.sensor_readings` instead of writing "partially observable"
and stopping there.
