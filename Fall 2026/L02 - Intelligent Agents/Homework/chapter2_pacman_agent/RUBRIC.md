# Grading - Chapter 2 Pac-Man Agent

Total: 100 points.

## Part 1 - Agent program (60)

| Item | Points | How it is checked |
|---|---|---|
| CH2-1 Percept declares all seven sensor fields, and only sensable ones | 7 | `test_ch2_1_*` |
| CH2-2 Preferences are named weights that actually drive the decision | 7 | `test_ch2_2_*` |
| CH2-3 / CH2-4 Internal state exists, is updated once per turn, stays bounded | 9 | `test_ch2_3_*`, `test_ch2_4_*` |
| CH2-5 Utility function returns named contributions that sum correctly, handles ghosts both ways, applies memory, rejects illegal actions | 15 | `test_ch2_5_*` |
| CH2-6 Selection is separate from evaluation, always legal, deterministic ties | 7 | `test_ch2_6_*` |
| CH2-7 `last_reason` reports direction, utility, and evidence | 4 | `test_ch2_7_*` |
| Scope: no environment access, no search implementation, no leftover markers | 5 | `test_scope_*` |
| Code quality: comments explain intent, weight names match behaviour, no dead code | 6 | read by hand |

The first seven rows total 54 and are scored automatically. Credit within a
row is proportional to the tests passed in that group, so a half-finished
task still scores.

## Part 2 - Trials (10)

| Item | Points |
|---|---|
| `results/trials.csv` and `results/summary.csv` present, generated from your agent | 4 |
| Normal-difficulty win rate at or above 60 percent | 4 |
| Mean performance beats the `simple_reflex` baseline | 2 |

## Part 3 - Write-up (30)

| Item | Points |
|---|---|
| PEAS description, all four parts, specific to this environment | 5 |
| Seven environment properties, each justified from the code | 7 |
| Agent type identified and mapped to a Section 2.4 figure, with a defensible next step | 5 |
| Performance measure vs utility function, located in the code, difference explained | 6 |
| Rational-but-unsuccessful episode, with a seed and a real explanation | 4 |
| Trial table interpreted in three to five sentences | 3 |

## Automatic deductions

| | |
|---|---|
| `pacman/` modified | -20, and regraded against the original package |
| Search algorithm implemented in `agent.py` | -10 |
| Third-party dependency added | -5 |
| Submission missing `agent.py` or the write-up | not gradeable, resubmit late |

## What full marks looks like

A submission that passes every test but whose write-up says the environment
is "partially observable because Pac-Man cannot see everything" will lose
most of Part 3. Answer from the code: point at `Simulation.sensor_readings`
and note that a declared field is always filled in completely, which makes
this environment fully observable for any agent that asks for the right
fields.

The write-up is where you show you understand what you built.
