#!/usr/bin/env python3
"""
Chapter 7 Logical Agents - classroom demos

A single-file, standard-library-only teaching kit for the main ideas in
Chapter 7: knowledge-based agents, propositional logic, model checking,
resolution, DPLL, WalkSAT, SATPLAN, and the Wumpus World.

Run examples:
    python chapter7_logical_agents_demos.py --demo all
    python chapter7_logical_agents_demos.py --demo wumpus --pause
    python chapter7_logical_agents_demos.py --demo logic
    python chapter7_logical_agents_demos.py --demo resolution
    python chapter7_logical_agents_demos.py --demo horn
    python chapter7_logical_agents_demos.py --demo dpll
    python chapter7_logical_agents_demos.py --demo walksat
    python chapter7_logical_agents_demos.py --demo satplan
    python chapter7_logical_agents_demos.py --demo puzzle8
    python chapter7_logical_agents_demos.py --demo queens

The code is intentionally explicit and readable rather than minimal.
"""

from __future__ import annotations

import argparse
import heapq
import itertools
import math
import random
import statistics
from collections import deque
from dataclasses import dataclass
from functools import reduce
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple


# -----------------------------------------------------------------------------
# Shared printing helpers
# -----------------------------------------------------------------------------


def title(text: str) -> None:
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def section(text: str) -> None:
    print("\n" + text)
    print("-" * len(text))


def pause_if(enabled: bool) -> None:
    if enabled:
        input("\nPress Enter to continue...")


def fmt_cell(c: Tuple[int, int]) -> str:
    return f"[{c[0]},{c[1]}]"


def fmt_cells(cells: Iterable[Tuple[int, int]]) -> str:
    items = sorted(cells)
    if not items:
        return "{}"
    return "{" + ", ".join(fmt_cell(c) for c in items) + "}"


# -----------------------------------------------------------------------------
# 1. Tiny propositional logic engine for truth-table model checking
# -----------------------------------------------------------------------------


class Expr:
    """Base class for propositional logic expressions."""

    def eval(self, model: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def symbols(self) -> Set[str]:
        raise NotImplementedError

    def __invert__(self) -> "Expr":
        return Not(self)

    def __and__(self, other: "Expr") -> "Expr":
        return And(self, as_expr(other))

    def __or__(self, other: "Expr") -> "Expr":
        return Or(self, as_expr(other))

    def __rshift__(self, other: "Expr") -> "Expr":
        return Implies(self, as_expr(other))

    def iff(self, other: "Expr") -> "Expr":
        return Iff(self, as_expr(other))


@dataclass(frozen=True)
class Var(Expr):
    name: str

    def eval(self, model: Dict[str, bool]) -> bool:
        return bool(model[self.name])

    def symbols(self) -> Set[str]:
        return {self.name}

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Const(Expr):
    value: bool

    def eval(self, model: Dict[str, bool]) -> bool:
        return self.value

    def symbols(self) -> Set[str]:
        return set()

    def __str__(self) -> str:
        return "True" if self.value else "False"


@dataclass(frozen=True)
class Not(Expr):
    x: Expr

    def eval(self, model: Dict[str, bool]) -> bool:
        return not self.x.eval(model)

    def symbols(self) -> Set[str]:
        return self.x.symbols()

    def __str__(self) -> str:
        return f"not {paren(self.x)}"


@dataclass(frozen=True)
class And(Expr):
    a: Expr
    b: Expr

    def eval(self, model: Dict[str, bool]) -> bool:
        return self.a.eval(model) and self.b.eval(model)

    def symbols(self) -> Set[str]:
        return self.a.symbols() | self.b.symbols()

    def __str__(self) -> str:
        return f"({self.a} and {self.b})"


@dataclass(frozen=True)
class Or(Expr):
    a: Expr
    b: Expr

    def eval(self, model: Dict[str, bool]) -> bool:
        return self.a.eval(model) or self.b.eval(model)

    def symbols(self) -> Set[str]:
        return self.a.symbols() | self.b.symbols()

    def __str__(self) -> str:
        return f"({self.a} or {self.b})"


@dataclass(frozen=True)
class Implies(Expr):
    a: Expr
    b: Expr

    def eval(self, model: Dict[str, bool]) -> bool:
        return (not self.a.eval(model)) or self.b.eval(model)

    def symbols(self) -> Set[str]:
        return self.a.symbols() | self.b.symbols()

    def __str__(self) -> str:
        return f"({self.a} => {self.b})"


@dataclass(frozen=True)
class Iff(Expr):
    a: Expr
    b: Expr

    def eval(self, model: Dict[str, bool]) -> bool:
        return self.a.eval(model) == self.b.eval(model)

    def symbols(self) -> Set[str]:
        return self.a.symbols() | self.b.symbols()

    def __str__(self) -> str:
        return f"({self.a} <=> {self.b})"


TRUE = Const(True)
FALSE = Const(False)


def as_expr(x: Expr) -> Expr:
    if isinstance(x, Expr):
        return x
    raise TypeError(f"Expected Expr, got {type(x)!r}")


def paren(x: Expr) -> str:
    if isinstance(x, (Var, Const)):
        return str(x)
    return f"({x})"


def sym(name: str) -> Var:
    return Var(name)


def and_all(parts: Sequence[Expr]) -> Expr:
    if not parts:
        return TRUE
    return reduce(lambda a, b: a & b, parts)


def or_all(parts: Sequence[Expr]) -> Expr:
    if not parts:
        return FALSE
    return reduce(lambda a, b: a | b, parts)


def all_models(symbols: Sequence[str]) -> Iterable[Dict[str, bool]]:
    for bits in itertools.product([False, True], repeat=len(symbols)):
        yield dict(zip(symbols, bits))


def truth_table_entails(kb: Expr, alpha: Expr) -> Tuple[bool, List[Dict[str, bool]], List[Dict[str, bool]]]:
    """Return (entailed?, kb_true_models, counterexamples)."""
    symbols = sorted(kb.symbols() | alpha.symbols())
    kb_true_models: List[Dict[str, bool]] = []
    counterexamples: List[Dict[str, bool]] = []
    for model in all_models(symbols):
        if kb.eval(model):
            kb_true_models.append(model)
            if not alpha.eval(model):
                counterexamples.append(model)
    return len(counterexamples) == 0, kb_true_models, counterexamples


def demo_logic_basics() -> None:
    title("Sections 7.3-7.4: propositional logic, models, and entailment")
    print("We build the small Wumpus knowledge base from the chapter.")
    print("Symbols: P12 means pit in [1,2], B11 means breeze in [1,1], etc.")

    B11, B21 = sym("B11"), sym("B21")
    P11, P12, P21, P22, P31 = sym("P11"), sym("P12"), sym("P21"), sym("P22"), sym("P31")

    r1 = ~P11
    r2 = B11.iff(P12 | P21)
    r3 = B21.iff(P11 | P22 | P31)
    r4 = ~B11
    r5 = B21
    kb = and_all([r1, r2, r3, r4, r5])

    print("\nKnowledge base KB = R1 and R2 and R3 and R4 and R5")
    for i, r in enumerate([r1, r2, r3, r4, r5], 1):
        print(f"  R{i}: {r}")

    for query, label in [
        (~P12, "There is no pit in [1,2]"),
        (~P22, "There is no pit in [2,2]"),
        (P22, "There is a pit in [2,2]"),
    ]:
        entailed, kb_models, counter = truth_table_entails(kb, query)
        print("\nASK:", label)
        print("Query:", query)
        print(f"Models where KB is true: {len(kb_models)}")
        print("Entailed?", entailed)
        if counter:
            print("Counterexample model:")
            print("  " + ", ".join(f"{k}={v}" for k, v in sorted(counter[0].items())))

    print("\nThe key classroom point:")
    print("  KB entails alpha when every model that makes KB true also makes alpha true.")
    print("  Here, no pit in [1,2] is guaranteed, but [2,2] is still unknown.")


# -----------------------------------------------------------------------------
# 2. CNF clauses, DPLL SAT solving, and resolution
# -----------------------------------------------------------------------------


Literal = Tuple[str, bool]       # (symbol, True) means symbol; (symbol, False) means not symbol
Clause = FrozenSet[Literal]
Model = Dict[str, bool]


def pos(name: str) -> Literal:
    return (name, True)


def neg(name: str) -> Literal:
    return (name, False)


def comp(lit: Literal) -> Literal:
    return (lit[0], not lit[1])


def lit_str(lit: Literal) -> str:
    return lit[0] if lit[1] else "not " + lit[0]


def clause(*lits: Literal) -> Clause:
    return frozenset(lits)


def clause_str(c: Clause) -> str:
    if len(c) == 0:
        return "EMPTY"
    return "(" + " or ".join(lit_str(l) for l in sorted(c)) + ")"


def clauses_str(clauses: Iterable[Clause]) -> str:
    return " and\n".join("  " + clause_str(c) for c in clauses)


def symbols_in_clauses(clauses: Iterable[Clause]) -> List[str]:
    return sorted({symb for c in clauses for symb, _ in c})


def eval_lit(lit: Literal, model: Model) -> Optional[bool]:
    name, positive = lit
    if name not in model:
        return None
    return model[name] if positive else not model[name]


def clause_value(c: Clause, model: Model) -> Optional[bool]:
    """True if satisfied, False if falsified, None if still undecided."""
    undecided = False
    for lit in c:
        val = eval_lit(lit, model)
        if val is True:
            return True
        if val is None:
            undecided = True
    return None if undecided else False


def clauses_satisfied(clauses: Sequence[Clause], model: Model) -> bool:
    return all(clause_value(c, model) is True for c in clauses)


def some_clause_false(clauses: Sequence[Clause], model: Model) -> bool:
    return any(clause_value(c, model) is False for c in clauses)


@dataclass
class DPLLStats:
    calls: int = 0
    pure_assignments: int = 0
    unit_assignments: int = 0
    branches: int = 0


def find_pure_symbol(symbols: Sequence[str], clauses: Sequence[Clause], model: Model) -> Tuple[Optional[str], Optional[bool]]:
    signs: Dict[str, Set[bool]] = {}
    for c in clauses:
        if clause_value(c, model) is True:
            continue
        for name, positive in c:
            if name in model:
                continue
            signs.setdefault(name, set()).add(positive)
    for name in symbols:
        if name not in model and len(signs.get(name, set())) == 1:
            return name, next(iter(signs[name]))
    return None, None


def find_unit_clause(clauses: Sequence[Clause], model: Model) -> Tuple[Optional[str], Optional[bool]]:
    for c in clauses:
        if clause_value(c, model) is True:
            continue
        unassigned: List[Literal] = []
        all_assigned_literals_false = True
        for lit in c:
            val = eval_lit(lit, model)
            if val is True:
                all_assigned_literals_false = False
                break
            if val is None:
                unassigned.append(lit)
        if all_assigned_literals_false and len(unassigned) == 1:
            name, positive = unassigned[0]
            return name, positive
    return None, None


def dpll_satisfiable(clauses_input: Sequence[Clause]) -> Tuple[bool, Optional[Model], DPLLStats]:
    clauses = list(clauses_input)
    symbols = symbols_in_clauses(clauses)
    stats = DPLLStats()

    def dpll(symbols_left: List[str], model: Model) -> Tuple[bool, Optional[Model]]:
        stats.calls += 1
        if clauses_satisfied(clauses, model):
            return True, dict(model)
        if some_clause_false(clauses, model):
            return False, None

        p, value = find_pure_symbol(symbols_left, clauses, model)
        if p is not None:
            stats.pure_assignments += 1
            rest = [s for s in symbols_left if s != p]
            new_model = dict(model)
            new_model[p] = bool(value)
            return dpll(rest, new_model)

        p, value = find_unit_clause(clauses, model)
        if p is not None:
            stats.unit_assignments += 1
            rest = [s for s in symbols_left if s != p]
            new_model = dict(model)
            new_model[p] = bool(value)
            return dpll(rest, new_model)

        if not symbols_left:
            return False, None
        p = symbols_left[0]
        rest = symbols_left[1:]
        stats.branches += 1
        model_true = dict(model)
        model_true[p] = True
        ok, found = dpll(rest, model_true)
        if ok:
            return ok, found
        model_false = dict(model)
        model_false[p] = False
        return dpll(rest, model_false)

    return_value, model = dpll(symbols, {})
    return return_value, model, stats


def is_tautological_clause(c: Clause) -> bool:
    return any(comp(l) in c for l in c)


def pl_resolve(ci: Clause, cj: Clause) -> Set[Clause]:
    resolvents: Set[Clause] = set()
    for lit in ci:
        if comp(lit) in cj:
            resolvent = frozenset((set(ci) - {lit}) | (set(cj) - {comp(lit)}))
            if not is_tautological_clause(resolvent):
                resolvents.add(resolvent)
    return resolvents


def pl_resolution(clauses_input: Sequence[Clause], verbose: bool = True, max_rounds: int = 20) -> bool:
    clauses_set: Set[Clause] = set(clauses_input)
    if verbose:
        print("Initial CNF clauses:")
        for c in sorted(clauses_set, key=clause_str):
            print(" ", clause_str(c))

    for round_no in range(1, max_rounds + 1):
        new: Set[Clause] = set()
        pairs = list(itertools.combinations(sorted(clauses_set, key=clause_str), 2))
        if verbose:
            print(f"\nResolution round {round_no}: checking {len(pairs)} clause pairs")
        for ci, cj in pairs:
            for r in pl_resolve(ci, cj):
                if len(r) == 0:
                    if verbose:
                        print("  Derived EMPTY from", clause_str(ci), "and", clause_str(cj))
                    return True
                if r not in clauses_set and r not in new:
                    new.add(r)
                    if verbose:
                        print("  New:", clause_str(r), "from", clause_str(ci), "and", clause_str(cj))
        if new.issubset(clauses_set):
            if verbose:
                print("No new clauses. The query is not entailed.")
            return False
        clauses_set |= new
    raise RuntimeError("Resolution stopped after max_rounds; increase max_rounds for this example.")


def demo_resolution() -> None:
    title("Section 7.5: proof by resolution")
    print("We prove that there is no pit in [1,2].")
    print("Use KB = (B11 <=> (P12 or P21)) and not B11.")
    print("To prove alpha = not P12, prove KB and not alpha is unsatisfiable.")
    print("So we add P12 and try to derive EMPTY.")

    # CNF for B11 <=> (P12 or P21):
    # (not B11 or P12 or P21) and (not P12 or B11) and (not P21 or B11)
    clauses = [
        clause(neg("B11"), pos("P12"), pos("P21")),
        clause(neg("P12"), pos("B11")),
        clause(neg("P21"), pos("B11")),
        clause(neg("B11")),       # percept: no breeze in [1,1]
        clause(pos("P12")),       # negated query: assume there is a pit in [1,2]
    ]
    entailed = pl_resolution(clauses, verbose=True)
    print("\nResult: KB entails not P12?", entailed)
    print("Classroom point: resolution proves entailment by contradiction.")


@dataclass(frozen=True)
class HornRule:
    premises: Tuple[str, ...]
    conclusion: str

    def __str__(self) -> str:
        if not self.premises:
            return self.conclusion
        return " and ".join(self.premises) + " => " + self.conclusion


def horn_forward_chain(rules: Sequence[HornRule], facts: Set[str], query: str) -> Tuple[bool, Set[str]]:
    """Forward chaining for definite clauses.

    This is the executable version of the chapter's PL-FC-ENTAILS? idea.
    The agenda starts with known facts, and each rule fires when all of its
    premises have been inferred.
    """
    inferred: Set[str] = set()
    agenda: List[str] = sorted(facts)
    remaining = {rule: len(rule.premises) for rule in rules}

    print("Initial agenda:", agenda)
    while agenda:
        p = agenda.pop(0)
        print(f"Process {p}")
        if p == query:
            print(f"Query {query} has been reached.")
            return True, inferred | {p}
        if p in inferred:
            print(f"  {p} was already processed; skip it.")
            continue
        inferred.add(p)
        for rule in rules:
            if p in rule.premises:
                remaining[rule] -= 1
                print(f"  Rule {rule}: {remaining[rule]} premise(s) still missing")
                if remaining[rule] == 0:
                    print(f"  Fire rule and infer {rule.conclusion}")
                    agenda.append(rule.conclusion)
    return query in inferred, inferred


def horn_backward_chain(rules: Sequence[HornRule], facts: Set[str], query: str, depth: int = 0, active: Optional[Set[str]] = None) -> bool:
    """Backward chaining for definite clauses.

    This is a goal-directed proof search: to prove q, find a rule whose head is q
    and recursively prove the rule's body.
    """
    if active is None:
        active = set()
    indent = "  " * depth
    print(f"{indent}Try to prove {query}")
    if query in facts:
        print(f"{indent}  {query} is a known fact")
        return True
    if query in active:
        print(f"{indent}  Loop avoided on {query}")
        return False
    path = set(active)
    path.add(query)
    for rule in rules:
        if rule.conclusion == query:
            print(f"{indent}  Use rule {rule}")
            if all(horn_backward_chain(rules, facts, prem, depth + 1, set(path)) for prem in rule.premises):
                print(f"{indent}  Therefore {query}")
                return True
    print(f"{indent}  No proof found for {query}")
    return False


def demo_horn() -> None:
    title("Section 7.5.4: Horn clauses, forward chaining, and backward chaining")
    print("This is the Horn-clause example from the chapter, with A and B as facts.")
    print("Goal: prove Q.")

    rules = [
        HornRule(("P",), "Q"),
        HornRule(("L", "M"), "P"),
        HornRule(("B", "L"), "M"),
        HornRule(("A", "P"), "L"),
        HornRule(("A", "B"), "L"),
    ]
    facts = {"A", "B"}

    print("\nKnowledge base:")
    for rule in rules:
        print(" ", rule)
    print(" Facts:", ", ".join(sorted(facts)))

    print("\nForward chaining: data-driven reasoning")
    ok, inferred = horn_forward_chain(rules, facts, "Q")
    print("Forward chaining result:", ok)
    print("Inferred symbols:", sorted(inferred))

    print("\nBackward chaining: goal-directed reasoning")
    ok = horn_backward_chain(rules, facts, "Q")
    print("Backward chaining result:", ok)

    print("\nClassroom point:")
    print("  Forward chaining starts with facts and pushes consequences forward.")
    print("  Backward chaining starts with the query and searches for supporting facts.")


def demo_dpll() -> None:
    title("Section 7.6.1: DPLL satisfiability checking")
    print("DPLL decides whether a CNF sentence has a satisfying model.")
    print("We run it on the same KB and not alpha sentence from the resolution demo.")

    unsat_clauses = [
        clause(neg("B11"), pos("P12"), pos("P21")),
        clause(neg("P12"), pos("B11")),
        clause(neg("P21"), pos("B11")),
        clause(neg("B11")),
        clause(pos("P12")),
    ]
    sat, model, stats = dpll_satisfiable(unsat_clauses)
    print("\nCNF:")
    print(clauses_str(unsat_clauses))
    print("\nSatisfiable?", sat)
    print("DPLL stats:", stats)
    print("Because KB and not alpha is unsatisfiable, KB entails alpha.")

    print("\nNow remove the negated query P12. The KB itself is satisfiable:")
    sat_clauses = unsat_clauses[:-1]
    sat, model, stats = dpll_satisfiable(sat_clauses)
    print("Satisfiable?", sat)
    print("One model:", {k: model[k] for k in sorted(model)} if model else None)
    print("DPLL stats:", stats)


# -----------------------------------------------------------------------------
# 3. WalkSAT local search for satisfiability
# -----------------------------------------------------------------------------


def random_planted_3sat(n_vars: int, m_clauses: int, seed: int = 0) -> Tuple[List[Clause], Model]:
    """Create a random 3-CNF that is guaranteed to be satisfiable."""
    rng = random.Random(seed)
    symbols = [f"X{i}" for i in range(1, n_vars + 1)]
    planted = {s: rng.choice([False, True]) for s in symbols}
    clauses: Set[Clause] = set()
    while len(clauses) < m_clauses:
        chosen = rng.sample(symbols, 3)
        lits: List[Literal] = []
        # Keep resampling signs until the clause is true in the planted model.
        while True:
            lits = [(s, rng.choice([False, True])) for s in chosen]
            if any((planted[s] if positive else not planted[s]) for s, positive in lits):
                break
        clauses.add(frozenset(lits))
    return list(clauses), planted


def clause_is_true_full(c: Clause, model: Model) -> bool:
    return any(eval_lit(l, model) is True for l in c)


def num_satisfied(clauses: Sequence[Clause], model: Model) -> int:
    return sum(1 for c in clauses if clause_is_true_full(c, model))


def walksat(clauses: Sequence[Clause], p: float = 0.5, max_flips: int = 1000, seed: int = 0,
            verbose: bool = False) -> Tuple[Optional[Model], int]:
    rng = random.Random(seed)
    symbols = symbols_in_clauses(clauses)
    model = {s: rng.choice([False, True]) for s in symbols}
    for flip in range(max_flips + 1):
        false_clauses = [c for c in clauses if not clause_is_true_full(c, model)]
        if not false_clauses:
            return model, flip
        if verbose and flip % 25 == 0:
            print(f"  flip {flip:4d}: {len(false_clauses)} unsatisfied clauses")
        c = rng.choice(false_clauses)
        if rng.random() < p:
            symbol_to_flip = rng.choice(list(c))[0]
        else:
            best_score = -1
            best_symbols: List[str] = []
            for symbol_to_test, _ in c:
                trial = dict(model)
                trial[symbol_to_test] = not trial[symbol_to_test]
                score = num_satisfied(clauses, trial)
                if score > best_score:
                    best_score = score
                    best_symbols = [symbol_to_test]
                elif score == best_score:
                    best_symbols.append(symbol_to_test)
            symbol_to_flip = rng.choice(best_symbols)
        model[symbol_to_flip] = not model[symbol_to_flip]
    return None, max_flips


def demo_walksat(seed: int = 7) -> None:
    title("Section 7.6.2: WalkSAT local search")
    print("WalkSAT searches through complete truth assignments by flipping variables.")
    print("It is good for finding a model when one exists, but failure is not a proof.")

    clauses, planted = random_planted_3sat(n_vars=16, m_clauses=60, seed=seed)
    print(f"\nGenerated a planted satisfiable 3-SAT problem with {len(symbols_in_clauses(clauses))} variables and {len(clauses)} clauses.")
    print("The hidden planted model exists, so WalkSAT should usually find a solution.")
    model, flips = walksat(clauses, p=0.45, max_flips=2000, seed=seed, verbose=True)
    if model is None:
        print("WalkSAT returned failure. This does not prove unsatisfiability.")
    else:
        print(f"WalkSAT found a satisfying model in {flips} flips.")
        print("First eight assignments:", {k: model[k] for k in sorted(model)[:8]})

    print("\nClassroom point:")
    print("  DPLL is complete; WalkSAT is often fast but cannot reliably prove no solution.")


# -----------------------------------------------------------------------------
# 4. SATPLAN: making a tiny plan by SAT solving
# -----------------------------------------------------------------------------


def at_symbol(cell: Tuple[int, int], t: int) -> str:
    return f"At_{cell[0]}_{cell[1]}_{t}"


def act_symbol(action: str, t: int) -> str:
    return f"Do_{action}_{t}"


def exactly_one(symbols: Sequence[str]) -> List[Clause]:
    clauses: List[Clause] = [frozenset(pos(s) for s in symbols)]
    for a, b in itertools.combinations(symbols, 2):
        clauses.append(clause(neg(a), neg(b)))
    return clauses


def grid_result(cell: Tuple[int, int], action: str, width: int, height: int) -> Tuple[int, int]:
    x, y = cell
    dx, dy = {
        "East": (1, 0),
        "North": (0, 1),
        "West": (-1, 0),
        "South": (0, -1),
        "Stay": (0, 0),
    }[action]
    nx, ny = x + dx, y + dy
    if 1 <= nx <= width and 1 <= ny <= height:
        return (nx, ny)
    return cell


def satplan_grid(width: int, height: int, start: Tuple[int, int], goal: Tuple[int, int],
                 max_t: int = 6) -> Tuple[Optional[List[str]], Optional[int], Optional[Model], List[Clause]]:
    cells = [(x, y) for x in range(1, width + 1) for y in range(1, height + 1)]
    actions = ["East", "North", "West", "South", "Stay"]

    for horizon in range(max_t + 1):
        clauses: List[Clause] = []

        # Exactly one location at each time.
        for t in range(horizon + 1):
            clauses.extend(exactly_one([at_symbol(c, t) for c in cells]))

        # Initial state and goal.
        clauses.append(clause(pos(at_symbol(start, 0))))
        clauses.append(clause(pos(at_symbol(goal, horizon))))

        # Exactly one action per time step and transition model.
        for t in range(horizon):
            clauses.extend(exactly_one([act_symbol(a, t) for a in actions]))
            for cell in cells:
                for action in actions:
                    result = grid_result(cell, action, width, height)
                    # At(cell,t) and Do(action,t) => At(result,t+1)
                    clauses.append(clause(neg(at_symbol(cell, t)), neg(act_symbol(action, t)), pos(at_symbol(result, t + 1))))

        sat, model, stats = dpll_satisfiable(clauses)
        if sat and model is not None:
            plan: List[str] = []
            for t in range(horizon):
                chosen = [a for a in actions if model.get(act_symbol(a, t), False)]
                plan.append(chosen[0] if chosen else "<unassigned>")
            return plan, horizon, model, clauses
    return None, None, None, []


def demo_satplan() -> None:
    title("Section 7.7.4: SATPLAN in a tiny grid world")
    print("SATPLAN turns planning into satisfiability.")
    print("Goal: start at [1,1] in a 2x2 grid and reach [2,2].")
    print("The solver tries horizon 0, then 1, then 2, ... until a model exists.")

    plan, horizon, model, clauses = satplan_grid(2, 2, (1, 1), (2, 2), max_t=4)
    if plan is None:
        print("No plan found.")
        return
    print(f"\nShortest horizon found: {horizon}")
    print("Plan:", plan)
    print(f"CNF size at solution horizon: {len(clauses)} clauses")
    print("\nAction variables set to true:")
    for t, a in enumerate(plan):
        print(f"  t={t}: {act_symbol(a, t)}")
    print("\nClassroom point:")
    print("  A satisfying model is not just a truth assignment; action variables encode a plan.")


# -----------------------------------------------------------------------------
# 5. Wumpus World game with a knowledge-based model-checking agent
# -----------------------------------------------------------------------------


DIRECTIONS = ["North", "East", "South", "West"]
DIR_DELTA = {
    "North": (0, 1),
    "East": (1, 0),
    "South": (0, -1),
    "West": (-1, 0),
}


@dataclass
class Percept:
    stench: bool
    breeze: bool
    glitter: bool
    bump: bool
    scream: bool

    def as_list(self) -> List[str]:
        return [
            "Stench" if self.stench else "None",
            "Breeze" if self.breeze else "None",
            "Glitter" if self.glitter else "None",
            "Bump" if self.bump else "None",
            "Scream" if self.scream else "None",
        ]

    def __str__(self) -> str:
        return "[" + ", ".join(self.as_list()) + "]"


class WumpusWorld:
    """A small deterministic Wumpus World."""

    def __init__(self) -> None:
        self.size = 4
        self.start = (1, 1)
        self.agent = self.start
        self.facing = "East"
        self.wumpus = (1, 3)
        self.pits = {(3, 1), (3, 3), (4, 4)}
        self.gold = (2, 3)
        self.has_gold = False
        self.wumpus_alive = True
        self.terminal = False
        self.dead = False
        self.last_bump = False
        self.last_scream = False
        self.score = 0

    def in_bounds(self, cell: Tuple[int, int]) -> bool:
        x, y = cell
        return 1 <= x <= self.size and 1 <= y <= self.size

    def neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = cell
        result = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            c = (x + dx, y + dy)
            if self.in_bounds(c):
                result.append(c)
        return result

    def percept(self) -> Percept:
        stench = self.wumpus_alive and self.wumpus in self.neighbors(self.agent)
        breeze = any(p in self.neighbors(self.agent) for p in self.pits)
        glitter = (self.agent == self.gold and not self.has_gold)
        p = Percept(stench, breeze, glitter, self.last_bump, self.last_scream)
        self.last_bump = False
        self.last_scream = False
        return p

    def turn_left(self) -> None:
        i = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(i - 1) % len(DIRECTIONS)]

    def turn_right(self) -> None:
        i = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(i + 1) % len(DIRECTIONS)]

    def execute(self, action: str) -> None:
        if self.terminal:
            return
        self.score -= 1
        if action == "TurnLeft":
            self.turn_left()
        elif action == "TurnRight":
            self.turn_right()
        elif action == "Forward":
            dx, dy = DIR_DELTA[self.facing]
            next_cell = (self.agent[0] + dx, self.agent[1] + dy)
            if not self.in_bounds(next_cell):
                self.last_bump = True
            else:
                self.agent = next_cell
                if self.agent in self.pits or (self.agent == self.wumpus and self.wumpus_alive):
                    self.dead = True
                    self.terminal = True
                    self.score -= 1000
        elif action == "Grab":
            if self.agent == self.gold and not self.has_gold:
                self.has_gold = True
        elif action == "Shoot":
            self.score -= 10
            # Not needed for the default demo, but included for completeness.
            dx, dy = DIR_DELTA[self.facing]
            x, y = self.agent
            while self.in_bounds((x + dx, y + dy)):
                x, y = x + dx, y + dy
                if (x, y) == self.wumpus and self.wumpus_alive:
                    self.wumpus_alive = False
                    self.last_scream = True
                    break
        elif action == "Climb":
            if self.agent == self.start:
                self.terminal = True
                if self.has_gold:
                    self.score += 1000
        else:
            raise ValueError(f"Unknown action: {action}")

    def reveal_board(self) -> None:
        print("Teacher view of hidden world: W=wumpus, P=pit, G=gold, A=start")
        for y in range(self.size, 0, -1):
            row = []
            for x in range(1, self.size + 1):
                c = (x, y)
                marks = []
                if c == self.start:
                    marks.append("A")
                if c == self.wumpus:
                    marks.append("W")
                if c in self.pits:
                    marks.append("P")
                if c == self.gold:
                    marks.append("G")
                row.append("".join(marks).ljust(3) if marks else ".  ")
            print(f"y={y}  " + " ".join(row))
        print("     x=1 x=2 x=3 x=4")


class WumpusModelChecker:
    """Model checker over possible pit masks and one wumpus location.

    This version precomputes all static worlds once, then filters them with
    bit operations each time the agent receives a percept. That keeps the
    classroom demo quick while still showing exact model checking.
    """

    _cache: Dict[int, Tuple[List[Tuple[Tuple[int, int], int, int, int, int]], List[Tuple[int, int]], List[Tuple[int, int]], Dict[Tuple[int, int], int], Dict[Tuple[int, int], int]]] = {}

    def __init__(self, size: int = 4) -> None:
        self.size = size
        self.start = (1, 1)
        cache = self._get_cache(size)
        self.worlds, self.cells, self.nonstart, self.cell_index, self.bit_index = cache
        self.observations: Dict[Tuple[int, int], Tuple[bool, bool]] = {}
        self.visited: Set[Tuple[int, int]] = set()

    @classmethod
    def _get_cache(cls, size: int) -> Tuple[List[Tuple[Tuple[int, int], int, int, int, int]], List[Tuple[int, int]], List[Tuple[int, int]], Dict[Tuple[int, int], int], Dict[Tuple[int, int], int]]:
        if size in cls._cache:
            return cls._cache[size]

        start = (1, 1)
        cells = [(x, y) for x in range(1, size + 1) for y in range(1, size + 1)]
        nonstart = [c for c in cells if c != start]
        cell_index = {c: i for i, c in enumerate(cells)}
        bit_index = {c: i for i, c in enumerate(nonstart)}

        def in_bounds(cell: Tuple[int, int]) -> bool:
            x, y = cell
            return 1 <= x <= size and 1 <= y <= size

        def neighbors(cell: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = cell
            result = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                c = (x + dx, y + dy)
                if in_bounds(c):
                    result.append(c)
            return result

        def cell_bit(cell: Tuple[int, int]) -> int:
            return 1 << cell_index[cell]

        def pit_bit(cell: Tuple[int, int]) -> int:
            if cell == start:
                return 0
            return 1 << bit_index[cell]

        n = len(nonstart)
        breeze_by_pit_mask: List[int] = [0] * (1 << n)
        for pit_mask in range(1 << n):
            breeze_mask = 0
            for loc in cells:
                if any(pit_bit(nb) and (pit_mask & pit_bit(nb)) for nb in neighbors(loc)):
                    breeze_mask |= cell_bit(loc)
            breeze_by_pit_mask[pit_mask] = breeze_mask

        stench_by_wumpus: Dict[Tuple[int, int], int] = {}
        for w in nonstart:
            stench_mask = 0
            for loc in cells:
                if w in neighbors(loc):
                    stench_mask |= cell_bit(loc)
            stench_by_wumpus[w] = stench_mask

        worlds: List[Tuple[Tuple[int, int], int, int, int, int]] = []
        for w in nonstart:
            w_bit = cell_bit(w)
            stench_mask = stench_by_wumpus[w]
            for pit_mask in range(1 << n):
                worlds.append((w, w_bit, pit_mask, breeze_by_pit_mask[pit_mask], stench_mask))

        cls._cache[size] = (worlds, cells, nonstart, cell_index, bit_index)
        return cls._cache[size]

    def in_bounds(self, cell: Tuple[int, int]) -> bool:
        x, y = cell
        return 1 <= x <= self.size and 1 <= y <= self.size

    def neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = cell
        result = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            c = (x + dx, y + dy)
            if self.in_bounds(c):
                result.append(c)
        return result

    def cell_bit(self, cell: Tuple[int, int]) -> int:
        return 1 << self.cell_index[cell]

    def pit_bit(self, cell: Tuple[int, int]) -> int:
        if cell == self.start:
            return 0
        return 1 << self.bit_index[cell]

    def add_percept(self, location: Tuple[int, int], percept: Percept) -> None:
        self.visited.add(location)
        self.observations[location] = (percept.breeze, percept.stench)

    def infer(self) -> Dict[str, object]:
        n = len(self.nonstart)
        all_pit_bits = (1 << n) - 1

        visited_cell_mask = 0
        visited_pit_mask = 0
        for v in self.visited:
            visited_cell_mask |= self.cell_bit(v)
            visited_pit_mask |= self.pit_bit(v)

        breeze_true_mask = 0
        breeze_false_mask = 0
        stench_true_mask = 0
        stench_false_mask = 0
        for loc, (breeze, stench) in self.observations.items():
            bit = self.cell_bit(loc)
            if breeze:
                breeze_true_mask |= bit
            else:
                breeze_false_mask |= bit
            if stench:
                stench_true_mask |= bit
            else:
                stench_false_mask |= bit

        model_count = 0
        pit_possible_mask = 0
        pit_certain_mask = all_pit_bits
        wumpus_possible: Set[Tuple[int, int]] = set()

        for w_cell, w_bit, pit_mask, breeze_mask, stench_mask in self.worlds:
            if pit_mask & visited_pit_mask:
                continue
            if w_bit & visited_cell_mask:
                continue
            if (breeze_mask & breeze_true_mask) != breeze_true_mask:
                continue
            if breeze_mask & breeze_false_mask:
                continue
            if (stench_mask & stench_true_mask) != stench_true_mask:
                continue
            if stench_mask & stench_false_mask:
                continue

            model_count += 1
            pit_possible_mask |= pit_mask
            pit_certain_mask &= pit_mask
            wumpus_possible.add(w_cell)

        if model_count == 0:
            return {
                "models": 0,
                "safe": set(),
                "possible_pits": set(),
                "certain_pits": set(),
                "possible_wumpus": set(),
                "certain_wumpus": set(),
            }

        possible_pits = {c for c in self.nonstart if pit_possible_mask & self.pit_bit(c)}
        certain_pits = {c for c in self.nonstart if pit_certain_mask & self.pit_bit(c)}
        certain_wumpus = set(wumpus_possible) if len(wumpus_possible) == 1 else set()
        safe = {
            c for c in self.cells
            if c not in possible_pits and c not in wumpus_possible
        } | set(self.visited)
        return {
            "models": model_count,
            "safe": safe,
            "possible_pits": possible_pits,
            "certain_pits": certain_pits,
            "possible_wumpus": wumpus_possible,
            "certain_wumpus": certain_wumpus,
        }


class LogicWumpusAgent:
    """Hybrid Wumpus agent: logic for safety, search for route planning."""

    def __init__(self, size: int = 4) -> None:
        self.size = size
        self.location = (1, 1)
        self.facing = "East"
        self.kb = WumpusModelChecker(size)
        self.plan: List[str] = []
        self.has_gold = False

    def in_bounds(self, cell: Tuple[int, int]) -> bool:
        x, y = cell
        return 1 <= x <= self.size and 1 <= y <= self.size

    def turn_left_dir(self, direction: str) -> str:
        i = DIRECTIONS.index(direction)
        return DIRECTIONS[(i - 1) % len(DIRECTIONS)]

    def turn_right_dir(self, direction: str) -> str:
        i = DIRECTIONS.index(direction)
        return DIRECTIONS[(i + 1) % len(DIRECTIONS)]

    def forward_cell(self, cell: Tuple[int, int], direction: str) -> Tuple[int, int]:
        dx, dy = DIR_DELTA[direction]
        nxt = (cell[0] + dx, cell[1] + dy)
        return nxt if self.in_bounds(nxt) else cell

    def update_internal_state_after_action(self, action: str) -> None:
        if action == "TurnLeft":
            self.facing = self.turn_left_dir(self.facing)
        elif action == "TurnRight":
            self.facing = self.turn_right_dir(self.facing)
        elif action == "Forward":
            self.location = self.forward_cell(self.location, self.facing)
        elif action == "Grab":
            self.has_gold = True

    def plan_route(self, goals: Set[Tuple[int, int]], allowed: Set[Tuple[int, int]]) -> List[str]:
        if not goals:
            return []
        start = (self.location, self.facing)
        q = deque([(start, [])])
        seen = {start}
        action_order = ["Forward", "TurnLeft", "TurnRight"]
        while q:
            (cell, direction), path = q.popleft()
            if cell in goals:
                return path
            for action in action_order:
                if action == "Forward":
                    new_cell = self.forward_cell(cell, direction)
                    new_dir = direction
                    if new_cell == cell or new_cell not in allowed:
                        continue
                elif action == "TurnLeft":
                    new_cell = cell
                    new_dir = self.turn_left_dir(direction)
                else:
                    new_cell = cell
                    new_dir = self.turn_right_dir(direction)
                state = (new_cell, new_dir)
                if state not in seen:
                    seen.add(state)
                    q.append((state, path + [action]))
        return []

    def act(self, percept: Percept) -> Tuple[str, Dict[str, object]]:
        self.kb.add_percept(self.location, percept)
        info = self.kb.infer()
        safe: Set[Tuple[int, int]] = info["safe"]  # type: ignore[assignment]

        if percept.glitter and not self.has_gold:
            route_home = self.plan_route({(1, 1)}, safe | {self.location})
            self.plan = ["Grab"] + route_home + ["Climb"]

        if not self.plan:
            unvisited_safe = set(safe) - self.kb.visited
            self.plan = self.plan_route(unvisited_safe, safe)

        if not self.plan:
            # If no safe unvisited square is known, go home and climb out.
            route_home = self.plan_route({(1, 1)}, safe | {self.location})
            self.plan = route_home + ["Climb"]

        action = self.plan.pop(0) if self.plan else "Climb"
        report = dict(info)
        report["chosen_action"] = action
        report["remaining_plan"] = list(self.plan)
        self.update_internal_state_after_action(action)
        return action, report


def run_wumpus_demo(pause: bool = False) -> None:
    title("Sections 7.1, 7.2, and 7.7: a knowledge-based Wumpus agent")
    world = WumpusWorld()
    agent = LogicWumpusAgent(size=4)
    world.reveal_board()
    print("\nThe agent will not see P/W/G directly. It receives percepts and uses model checking.")
    pause_if(pause)

    for t in range(40):
        if world.terminal:
            break
        percept = world.percept()
        old_loc = agent.location
        old_dir = agent.facing
        action, report = agent.act(percept)

        section(f"Time {t}")
        print(f"Agent thinks it is at {fmt_cell(old_loc)}, facing {old_dir}.")
        print("Percept:", percept)
        print("Consistent possible worlds:", report["models"])
        print("Entailed safe squares:", fmt_cells(report["safe"]))
        print("Possible pit squares:", fmt_cells(report["possible_pits"]))
        print("Certain pit squares:", fmt_cells(report["certain_pits"]))
        print("Possible wumpus squares:", fmt_cells(report["possible_wumpus"]))
        print("Certain wumpus square:", fmt_cells(report["certain_wumpus"]))
        print("Chosen action:", action)
        if report["remaining_plan"]:
            print("Remaining plan:", report["remaining_plan"])

        world.execute(action)
        print(f"World score after action: {world.score}")
        if world.dead:
            print("The agent died.")
        if world.terminal and world.has_gold and world.agent == world.start:
            print("Success: the agent climbed out with the gold.")
        pause_if(pause)

    if not world.terminal:
        print("Demo stopped before terminal state.")
    print("Final world score:", world.score)


# -----------------------------------------------------------------------------
# 6. 8-puzzle A* demo: contrast with non-logical problem solving agents
# -----------------------------------------------------------------------------


PuzzleState = Tuple[int, ...]


def puzzle_goal() -> PuzzleState:
    return (1, 2, 3, 4, 5, 6, 7, 8, 0)


def puzzle_manhattan(state: PuzzleState) -> int:
    total = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        x, y = i % 3, i // 3
        gx, gy = (tile - 1) % 3, (tile - 1) // 3
        total += abs(x - gx) + abs(y - gy)
    return total


def puzzle_neighbors(state: PuzzleState) -> Iterable[Tuple[str, PuzzleState]]:
    blank = state.index(0)
    x, y = blank % 3, blank // 3
    moves = [("Up", 0, -1), ("Down", 0, 1), ("Left", -1, 0), ("Right", 1, 0)]
    for name, dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            j = ny * 3 + nx
            new_state = list(state)
            new_state[blank], new_state[j] = new_state[j], new_state[blank]
            yield name, tuple(new_state)


def astar_puzzle(start: PuzzleState) -> Tuple[List[str], List[PuzzleState], int]:
    goal = puzzle_goal()
    frontier: List[Tuple[int, int, PuzzleState]] = []
    heapq.heappush(frontier, (puzzle_manhattan(start), 0, start))
    came_from: Dict[PuzzleState, Tuple[Optional[PuzzleState], Optional[str]]] = {start: (None, None)}
    cost: Dict[PuzzleState, int] = {start: 0}
    expansions = 0

    while frontier:
        _, g, state = heapq.heappop(frontier)
        expansions += 1
        if state == goal:
            actions: List[str] = []
            states: List[PuzzleState] = []
            cur: Optional[PuzzleState] = state
            while cur is not None:
                states.append(cur)
                prev, action = came_from[cur]
                if action is not None:
                    actions.append(action)
                cur = prev
            actions.reverse()
            states.reverse()
            return actions, states, expansions
        for action, nxt in puzzle_neighbors(state):
            new_cost = cost[state] + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                priority = new_cost + puzzle_manhattan(nxt)
                came_from[nxt] = (state, action)
                heapq.heappush(frontier, (priority, new_cost, nxt))
    raise RuntimeError("No solution")


def print_puzzle(state: PuzzleState) -> None:
    for r in range(3):
        row = state[3 * r:3 * r + 3]
        print(" ".join("." if x == 0 else str(x) for x in row))


def demo_puzzle8() -> None:
    title("Contrast example: 8-puzzle with A* search")
    print("The chapter contrasts logical agents with problem-solving agents.")
    print("This A* agent searches states using actions and a heuristic; it has no KB.")
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    actions, states, expansions = astar_puzzle(start)
    print("\nStart:")
    print_puzzle(start)
    print("\nSolution actions:", actions)
    print("Nodes expanded:", expansions)
    for i, state in enumerate(states):
        print(f"\nStep {i}:")
        print_puzzle(state)


# -----------------------------------------------------------------------------
# 7. N-Queens min-conflicts demo: local search flavor
# -----------------------------------------------------------------------------


def queen_conflicts(board: List[int], col: int, row: int) -> int:
    conflicts = 0
    for c, r in enumerate(board):
        if c == col:
            continue
        if r == row or abs(r - row) == abs(c - col):
            conflicts += 1
    return conflicts


def total_queen_conflicts(board: List[int]) -> int:
    total = 0
    n = len(board)
    for c1 in range(n):
        for c2 in range(c1 + 1, n):
            r1, r2 = board[c1], board[c2]
            if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                total += 1
    return total


def min_conflicts_queens(n: int = 8, max_steps: int = 1000, seed: int = 0) -> Tuple[Optional[List[int]], int]:
    rng = random.Random(seed)
    board = [rng.randrange(n) for _ in range(n)]
    for step in range(max_steps + 1):
        conflicted = [c for c in range(n) if queen_conflicts(board, c, board[c]) > 0]
        if not conflicted:
            return board, step
        col = rng.choice(conflicted)
        scores = [(queen_conflicts(board, col, row), row) for row in range(n)]
        min_score = min(s for s, _ in scores)
        best_rows = [row for s, row in scores if s == min_score]
        board[col] = rng.choice(best_rows)
    return None, max_steps


def print_queens(board: List[int]) -> None:
    n = len(board)
    for row in range(n - 1, -1, -1):
        print(" ".join("Q" if board[col] == row else "." for col in range(n)))


def demo_queens(seed: int = 4) -> None:
    title("Related puzzle: N-Queens with min-conflicts local search")
    print("The chapter mentions N-Queens while discussing why some local-search problems are easy.")
    board, steps = min_conflicts_queens(n=8, max_steps=1000, seed=seed)
    if board is None:
        print("No solution found within the limit. Try a different seed.")
        return
    print(f"Solved 8-Queens in {steps} repair steps.")
    print("Board representation: board[col] = row")
    print(board)
    print_queens(board)
    print("Total attacking pairs:", total_queen_conflicts(board))


# -----------------------------------------------------------------------------
# Main CLI
# -----------------------------------------------------------------------------


def run_all(seed: int, pause: bool) -> None:
    demo_logic_basics()
    pause_if(pause)
    demo_resolution()
    pause_if(pause)
    demo_horn()
    pause_if(pause)
    demo_dpll()
    pause_if(pause)
    demo_walksat(seed=seed)
    pause_if(pause)
    demo_satplan()
    pause_if(pause)
    run_wumpus_demo(pause=pause)
    pause_if(pause)
    demo_puzzle8()
    pause_if(pause)
    demo_queens(seed=seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chapter 7 logical agents classroom demos")
    parser.add_argument("--demo", default="all", choices=[
        "all", "logic", "resolution", "horn", "dpll", "walksat", "satplan", "wumpus", "puzzle8", "queens"
    ])
    parser.add_argument("--pause", action="store_true", help="pause between major steps; useful for class")
    parser.add_argument("--seed", type=int, default=7, help="random seed for stochastic demos")
    args = parser.parse_args()

    if args.demo == "all":
        run_all(seed=args.seed, pause=args.pause)
    elif args.demo == "logic":
        demo_logic_basics()
    elif args.demo == "resolution":
        demo_resolution()
    elif args.demo == "horn":
        demo_horn()
    elif args.demo == "dpll":
        demo_dpll()
    elif args.demo == "walksat":
        demo_walksat(seed=args.seed)
    elif args.demo == "satplan":
        demo_satplan()
    elif args.demo == "wumpus":
        run_wumpus_demo(pause=args.pause)
    elif args.demo == "puzzle8":
        demo_puzzle8()
    elif args.demo == "queens":
        demo_queens(seed=args.seed)


if __name__ == "__main__":
    main()
