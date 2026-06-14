# Chapter 7 Logical Agents - Classroom Code Demos

This teaching kit is standard-library-only Python. It is designed for live projection in class.

## Files

- `chapter7_logical_agents_demos.py` - the main demo program.
- `CHAPTER7_DEMO_README.md` - this guide.

## How to run

Use Python 3.10+.

```bash
python chapter7_logical_agents_demos.py --demo all
python chapter7_logical_agents_demos.py --demo all --pause
```

The `--pause` flag waits for Enter between major steps, which is useful for a step-by-step show-and-tell.

## Individual demos

```bash
python chapter7_logical_agents_demos.py --demo logic
python chapter7_logical_agents_demos.py --demo resolution
python chapter7_logical_agents_demos.py --demo horn
python chapter7_logical_agents_demos.py --demo dpll
python chapter7_logical_agents_demos.py --demo walksat
python chapter7_logical_agents_demos.py --demo satplan
python chapter7_logical_agents_demos.py --demo wumpus --pause
python chapter7_logical_agents_demos.py --demo puzzle8
python chapter7_logical_agents_demos.py --demo queens
```

## Demo-to-section mapping

| Demo | Chapter connection | What to point out |
|---|---|---|
| `logic` | 7.3-7.4 Logic and propositional logic | Models, entailment, truth tables, why `no pit in [1,2]` follows but `no pit in [2,2]` does not. |
| `resolution` | 7.5 Propositional theorem proving | Proof by contradiction; deriving the empty clause. |
| `horn` | 7.5.4 Forward/backward chaining | Data-driven vs goal-directed reasoning with Horn clauses. |
| `dpll` | 7.6.1 Complete SAT checking | DPLL uses unit clauses, pure symbols, and backtracking. |
| `walksat` | 7.6.2 Local search | Fast model finding, but failure is not a proof of unsatisfiability. |
| `satplan` | 7.7.4 Planning as SAT | A satisfying model can encode a sequence of actions. |
| `wumpus` | 7.2 and 7.7 Wumpus World logical agent | TELL percepts, ASK safe squares, infer hidden hazards, choose actions. |
| `puzzle8` | Contrast with earlier problem-solving agents | A* finds a path but does not reason with general facts. |
| `queens` | Mentioned under random/local-search landscapes | Min-conflicts repair search on N-Queens. |

## Suggested live lesson flow

1. Start with `--demo logic` to introduce KB, models, and entailment.
2. Run `--demo resolution` to show proof without enumerating every model.
3. Run `--demo horn` to show inference that looks like rules firing.
4. Run `--demo dpll` and `--demo walksat` to compare complete and incomplete SAT methods.
5. Run `--demo wumpus --pause` as the main game-style demo.
6. Run `--demo satplan` to show how a model can represent a plan.
7. Use `--demo puzzle8` as a contrast: search can solve explicit state-space problems, while logical agents infer hidden facts.

## Classroom questions to ask

- Which squares are guaranteed safe, and which are merely unknown?
- Why does `KB entails alpha` require every KB model to make alpha true?
- Why does resolution add the negation of the query?
- Why can WalkSAT find a model but not prove that no model exists?
- In the Wumpus demo, what did the agent infer that it did not directly perceive?
