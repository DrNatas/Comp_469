# Chapter 8 First-Order Logic Teaching Kit

This kit gives you colorful, runnable demonstrations for teaching Chapter 8: First-Order Logic.
It is designed for live classroom use. Everything runs locally.

## Files

- `chapter8_fol_visual_demos.py` — main Python teaching script, standard library only.
- `chapter8_fol_visual_playground.html` — optional browser playground with colorful Wumpus, quantifier, and circuit visuals.
- `CHAPTER8_FOL_TEACHING_GUIDE.md` — this guide.

## Quick start

Python 3.10 or newer is recommended.

```bash
python chapter8_fol_visual_demos.py --demo all
```

For live teaching, use pauses:

```bash
python chapter8_fol_visual_demos.py --demo all --pause
```

For detailed formula-evaluation traces:

```bash
python chapter8_fol_visual_demos.py --demo model --trace
python chapter8_fol_visual_demos.py --demo quantifiers --trace
```

Open the browser playground by double-clicking:

```text
chapter8_fol_visual_playground.html
```

No internet connection is required.

## Demo menu

```bash
python chapter8_fol_visual_demos.py --demo representation
python chapter8_fol_visual_demos.py --demo model
python chapter8_fol_visual_demos.py --demo quantifiers
python chapter8_fol_visual_demos.py --demo database
python chapter8_fol_visual_demos.py --demo wumpus --pause
python chapter8_fol_visual_demos.py --demo circuit
python chapter8_fol_visual_demos.py --demo circuit --inputs 1 0 1
python chapter8_fol_visual_demos.py --demo engineering
```

## Recommended classroom sequence

### 1. Representation Revisited

Run:

```bash
python chapter8_fol_visual_demos.py --demo representation
```

Show students the difference between writing many propositional rules and one first-order rule:

```text
B_1_1 ⇔ (P_1_2 ∨ P_2_1)
B_1_2 ⇔ (P_1_1 ∨ P_1_3 ∨ P_2_2)
...

∀s Breezy(s) ⇔ ∃p (Pit(p) ∧ Adjacent(p,s))
```

Ask: “Which representation scales to a 100 x 100 game board?”

### 2. Models, Objects, Relations, Functions

Run:

```bash
python chapter8_fol_visual_demos.py --demo model --trace
```

Teaching goals:

- A model has objects.
- Constant symbols name objects.
- Predicate symbols name relations.
- Function symbols name functions.
- Terms refer to objects.
- Atomic sentences are true when the named relation holds among the named objects.

Key formulas shown:

```text
Brother(Richard, John)
¬Brother(LeftLeg(Richard), John)
∀x (King(x) ⇒ Person(x))
∃x (Crown(x) ∧ OnHead(x, John))
```

Stop on this translation mistake:

```text
∃x (Crown(x) ⇒ OnHead(x, John))
```

Explain that existential implication is usually too weak because any non-crown object makes the implication true.

### 3. Quantifier Quest

Run:

```bash
python chapter8_fol_visual_demos.py --demo quantifiers --trace
```

Show:

```text
∀x ∃y Loves(x,y)
∃y ∀x Loves(x,y)
```

Class prompt: “Does everyone having a password mean one password works for everyone?”

### 4. Standard FOL vs Database Semantics

Run:

```bash
python chapter8_fol_visual_demos.py --demo database
```

Use the Richard/John/Geoffrey brother example.

Teaching goals:

- Standard FOL is open-world: missing facts are not automatically false.
- Database semantics uses unique names, closed world, and domain closure.
- Different semantics produce different practical inferences.

### 5. FOL Wumpus World

Run:

```bash
python chapter8_fol_visual_demos.py --demo wumpus --pause
```

This is the most game-like classroom demo.

Students see:

- A hidden Wumpus board.
- Percepts such as Breeze, Stench, and Glitter.
- TELLed percept history.
- ASK queries.
- A colored grid showing known safe squares, possible pits, certain pits, and the certain Wumpus.

Core FOL rules:

```text
∀s Breezy(s) ⇔ ∃p (Pit(p) ∧ Adjacent(p,s))
∀s Smelly(s) ⇔ ∃w (Wumpus(w) ∧ Adjacent(w,s))
∀s OK(s) ⇔ ¬Pit(s) ∧ ¬Wumpus(s)
```

Teaching prompt at each step:

1. What did the agent perceive?
2. What sentence did it TELL the KB?
3. Which possible worlds remain?
4. What can the agent ASK and prove?
5. Which squares are safe enough to enter?

### 6. Digital Circuit Logic Lab

Run:

```bash
python chapter8_fol_visual_demos.py --demo circuit
```

Or choose specific input bits:

```bash
python chapter8_fol_visual_demos.py --demo circuit --inputs 1 0 1
```

Students see:

- The one-bit full-adder circuit.
- Gate-by-gate signal propagation.
- Query results for input combinations that produce SUM=0 and CARRY=1.
- A complete truth table verifying the full adder.
- A debugging example: forgetting to assert `1 ≠ 0` breaks XOR reasoning for mixed inputs.

Useful class question:

“Why does a theorem prover need the fact `1 ≠ 0`? Isn’t it obvious to us?”

Answer: it is obvious to humans, but a formal system can only use what is represented in its KB.

### 7. Knowledge Engineering Process

Run:

```bash
python chapter8_fol_visual_demos.py --demo engineering
```

Use this as a closing summary:

1. Identify questions.
2. Assemble relevant knowledge.
3. Choose vocabulary.
4. Encode general knowledge.
5. Encode the specific problem instance.
6. Pose queries.
7. Debug and evaluate.

## Suggested 50-minute lesson plan

| Time | Activity |
|---:|---|
| 0-5 min | Run `--demo representation`; compare propositional vs FOL rule size. |
| 5-15 min | Run `--demo model --trace`; explain models, objects, predicates, functions. |
| 15-25 min | Run `--demo quantifiers --trace`; students predict formula truth values. |
| 25-35 min | Run `--demo wumpus --pause`; students reason from percepts. |
| 35-45 min | Run `--demo circuit`; verify the full adder. |
| 45-50 min | Run `--demo engineering`; connect demos to the knowledge engineering process. |

## Suggested student mini-projects

1. Add a new predicate to the kingdom model, such as `Royal(x)`.
2. Add a new Wumpus percept rule.
3. Change the Wumpus map and see how the possible-world count changes.
4. Add a NOT gate to the circuit demo.
5. Build a first-order vocabulary for a campus map, network diagram, or tabletop game.

## Troubleshooting

### Colors do not show correctly

Use:

```bash
python chapter8_fol_visual_demos.py --demo all --no-color
```

### The Wumpus demo prints the hidden answer key

For a student-facing run, hide it:

```bash
python chapter8_fol_visual_demos.py --demo wumpus --pause --hide-answers
```

### The output moves too fast

Use:

```bash
python chapter8_fol_visual_demos.py --demo all --pause
```

