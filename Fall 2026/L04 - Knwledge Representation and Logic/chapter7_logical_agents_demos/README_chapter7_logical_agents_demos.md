# Chapter 7 Logical Agents: Classroom Code Demos

This folder contains one runnable Python file:

- `chapter7_logical_agents_demos.py`

It uses only the Python standard library. No packages need to be installed.

## Quick start

```bash
python chapter7_logical_agents_demos.py --demo all
```

Use pause mode for a live lecture:

```bash
python chapter7_logical_agents_demos.py --demo wumpus --pause
```

## Recommended class flow

### 1. Sections 7.1-7.2 and 7.7: Wumpus World logical agent

```bash
python chapter7_logical_agents_demos.py --demo wumpus --pause
```

Show students:

1. The hidden teacher board has a Wumpus, pits, and gold.
2. The agent only receives percepts: stench, breeze, glitter, bump, scream.
3. The agent maintains a knowledge base of observations.
4. It model-checks all worlds consistent with the percept history.
5. It marks squares as safe only when every consistent model agrees they are safe.
6. It plans routes through known safe squares and eventually grabs the gold.

Discussion prompts:

- Why does no breeze at [1,1] prove [1,2] and [2,1] have no pits?
- Why does a breeze at [2,1] not tell us exactly where the pit is?
- Why is the Wumpus location eventually certain?

### 2. Sections 7.3-7.4: Models, truth, and entailment

```bash
python chapter7_logical_agents_demos.py --demo logic
```

Show students:

1. A knowledge base is a sentence made from smaller sentences.
2. A model is a truth assignment.
3. Entailment means every model that satisfies the KB also satisfies the query.
4. `not P12` is entailed, but neither `P22` nor `not P22` is entailed.

### 3. Section 7.5: Resolution theorem proving

```bash
python chapter7_logical_agents_demos.py --demo resolution
```

Show students:

1. To prove alpha, assume not alpha.
2. Convert the KB plus not alpha into clauses.
3. Resolve clauses until the empty clause appears.
4. The empty clause is a contradiction, so alpha is entailed.

### 4. Section 7.6.1: DPLL SAT solver

```bash
python chapter7_logical_agents_demos.py --demo dpll
```

Show students:

1. DPLL is model checking, but smarter than truth-table enumeration.
2. It uses early stopping, pure symbols, and unit clauses.
3. If `KB and not alpha` is unsatisfiable, then `KB entails alpha`.

### 5. Section 7.6.2: WalkSAT local search

```bash
python chapter7_logical_agents_demos.py --demo walksat
```

Show students:

1. WalkSAT starts with a random complete assignment.
2. It flips variables to reduce unsatisfied clauses.
3. If it finds a model, the sentence is satisfiable.
4. If it fails, that does not prove unsatisfiability.

### 6. Section 7.7.4: SATPLAN

```bash
python chapter7_logical_agents_demos.py --demo satplan
```

Show students:

1. Planning can be encoded as a SAT problem.
2. Action variables become part of the satisfying model.
3. Extracting the true action variables gives a plan.

### 7. Related puzzle demos mentioned in the chapter

```bash
python chapter7_logical_agents_demos.py --demo puzzle8
python chapter7_logical_agents_demos.py --demo queens
```

Use these to contrast:

- 8-puzzle: a problem-solving agent searches concrete states.
- N-Queens: local search can solve some huge spaces quickly.

## Command list

```bash
python chapter7_logical_agents_demos.py --demo all
python chapter7_logical_agents_demos.py --demo logic
python chapter7_logical_agents_demos.py --demo resolution
python chapter7_logical_agents_demos.py --demo dpll
python chapter7_logical_agents_demos.py --demo walksat
python chapter7_logical_agents_demos.py --demo satplan
python chapter7_logical_agents_demos.py --demo wumpus --pause
python chapter7_logical_agents_demos.py --demo puzzle8
python chapter7_logical_agents_demos.py --demo queens
```

## Requirements

- Python 3.9 or newer recommended.
- No third-party libraries.
