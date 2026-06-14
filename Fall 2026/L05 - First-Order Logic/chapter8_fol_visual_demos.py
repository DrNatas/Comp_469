#!/usr/bin/env python3
"""
Chapter 8: First-Order Logic visual teaching demos.

This is a no-dependency Python teaching kit for classroom demonstrations.
It uses colored terminal output to show the main ideas behind Chapter 8:

    8.1  Why first-order logic is more expressive than propositional logic
    8.2  Models, objects, relations, functions, terms, atoms, connectives,
         universal quantifiers, and existential quantifiers
    8.2.8 Standard first-order semantics vs database semantics
    8.4  Knowledge engineering with the one-bit full-adder circuit domain

It also includes a FOL-style Wumpus World visualization, because the chapter
uses Wumpus examples to motivate concise first-order rules such as:

    For every square s, Breezy(s) iff there exists an adjacent pit.

Run examples:

    python chapter8_fol_visual_demos.py --demo all
    python chapter8_fol_visual_demos.py --demo all --pause
    python chapter8_fol_visual_demos.py --demo representation
    python chapter8_fol_visual_demos.py --demo model
    python chapter8_fol_visual_demos.py --demo quantifiers
    python chapter8_fol_visual_demos.py --demo database
    python chapter8_fol_visual_demos.py --demo wumpus --pause
    python chapter8_fol_visual_demos.py --demo circuit
    python chapter8_fol_visual_demos.py --demo circuit --inputs 1 0 1

Teacher note:
This file is intentionally verbose and readable. It is meant to be displayed,
modified, and discussed in class.
"""

from __future__ import annotations

import argparse
import itertools
import os
import random
import sys
import textwrap
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

# -----------------------------------------------------------------------------
# Terminal color helpers
# -----------------------------------------------------------------------------

class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def enable_windows_ansi() -> None:
    """Enable ANSI escape handling in many modern Windows terminals."""
    if os.name == "nt":
        os.system("")


def color(text: object, *styles: str, no_color: bool = False) -> str:
    s = str(text)
    if no_color:
        return s
    return "".join(styles) + s + Style.RESET


def truth_color(value: Optional[bool], no_color: bool = False) -> str:
    if value is True:
        return color("TRUE", Style.BOLD, Style.GREEN, no_color=no_color)
    if value is False:
        return color("FALSE", Style.BOLD, Style.RED, no_color=no_color)
    return color("UNKNOWN", Style.BOLD, Style.YELLOW, no_color=no_color)


def onezero(value: int, no_color: bool = False) -> str:
    if value == 1:
        return color("1", Style.BOLD, Style.GREEN, no_color=no_color)
    return color("0", Style.BOLD, Style.RED, no_color=no_color)


def header(title: str, no_color: bool = False) -> None:
    line = "=" * len(title)
    print("\n" + color(line, Style.BOLD, Style.CYAN, no_color=no_color))
    print(color(title, Style.BOLD, Style.CYAN, no_color=no_color))
    print(color(line, Style.BOLD, Style.CYAN, no_color=no_color))


def subheader(title: str, no_color: bool = False) -> None:
    print("\n" + color(title, Style.BOLD, Style.MAGENTA, no_color=no_color))
    print(color("-" * len(title), Style.MAGENTA, no_color=no_color))


def teacher_note(text: str, no_color: bool = False) -> None:
    wrapped = textwrap.fill(text, width=88)
    print(color("Teacher note: ", Style.BOLD, Style.YELLOW, no_color=no_color) + wrapped)


def bullet(text: str, no_color: bool = False) -> None:
    print("  " + color("- ", Style.BOLD, Style.BLUE, no_color=no_color) + text)


def wait_if_needed(pause: bool, message: str = "Press Enter for the next step...") -> None:
    if pause:
        try:
            input(color("\n" + message, Style.BOLD, Style.YELLOW))
        except EOFError:
            pass


def wrap_print(text: str, indent: int = 0) -> None:
    print(textwrap.fill(text, width=92, initial_indent=" " * indent, subsequent_indent=" " * indent))


# -----------------------------------------------------------------------------
# Tiny first-order logic evaluator over finite models
# -----------------------------------------------------------------------------

class EvaluationError(Exception):
    pass


@dataclass(frozen=True)
class Term:
    def eval(self, model: "FOLModel", env: Dict[str, str]) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Const(Term):
    name: str

    def eval(self, model: "FOLModel", env: Dict[str, str]) -> str:
        if self.name not in model.constants:
            raise EvaluationError(f"Unknown constant symbol {self.name!r}")
        return model.constants[self.name]

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Var(Term):
    name: str

    def eval(self, model: "FOLModel", env: Dict[str, str]) -> str:
        if self.name not in env:
            raise EvaluationError(f"Unbound variable {self.name!r}")
        return env[self.name]

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Func(Term):
    name: str
    args: Tuple[Term, ...]

    def __init__(self, name: str, args: Sequence[Term]):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "args", tuple(args))

    def eval(self, model: "FOLModel", env: Dict[str, str]) -> str:
        if self.name not in model.functions:
            raise EvaluationError(f"Unknown function symbol {self.name!r}")
        key = tuple(arg.eval(model, env) for arg in self.args)
        mapping = model.functions[self.name]
        if key not in mapping:
            raise EvaluationError(f"Function {self.name}{key} is not defined in this model")
        return mapping[key]

    def __str__(self) -> str:
        return f"{self.name}(" + ", ".join(map(str, self.args)) + ")"


@dataclass(frozen=True)
class Formula:
    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Pred(Formula):
    name: str
    args: Tuple[Term, ...]

    def __init__(self, name: str, args: Sequence[Term]):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "args", tuple(args))

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        if self.name not in model.relations:
            raise EvaluationError(f"Unknown predicate symbol {self.name!r}")
        tup = tuple(arg.eval(model, env) for arg in self.args)
        result = tup in model.relations[self.name]
        if trace is not None:
            trace.append("  " * depth + f"{self} becomes {self.name}{tup} -> {result}")
        return result

    def __str__(self) -> str:
        if self.args:
            return f"{self.name}(" + ", ".join(map(str, self.args)) + ")"
        return self.name


@dataclass(frozen=True)
class Eq(Formula):
    left: Term
    right: Term

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        left_val = self.left.eval(model, env)
        right_val = self.right.eval(model, env)
        result = left_val == right_val
        if trace is not None:
            trace.append("  " * depth + f"{self}: {left_val!r} == {right_val!r} -> {result}")
        return result

    def __str__(self) -> str:
        return f"{self.left} = {self.right}"


@dataclass(frozen=True)
class Not(Formula):
    child: Formula

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        result = not self.child.eval(model, env or {}, trace, depth + 1)
        if trace is not None:
            trace.append("  " * depth + f"¬({self.child}) -> {result}")
        return result

    def __str__(self) -> str:
        return f"¬{self.child}"


@dataclass(frozen=True)
class And(Formula):
    parts: Tuple[Formula, ...]

    def __init__(self, *parts: Formula):
        object.__setattr__(self, "parts", tuple(parts))

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        results = [p.eval(model, env, trace, depth + 1) for p in self.parts]
        result = all(results)
        if trace is not None:
            trace.append("  " * depth + f"({self}) -> {result}")
        return result

    def __str__(self) -> str:
        return " ∧ ".join(f"({p})" for p in self.parts)


@dataclass(frozen=True)
class Or(Formula):
    parts: Tuple[Formula, ...]

    def __init__(self, *parts: Formula):
        object.__setattr__(self, "parts", tuple(parts))

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        results = [p.eval(model, env, trace, depth + 1) for p in self.parts]
        result = any(results)
        if trace is not None:
            trace.append("  " * depth + f"({self}) -> {result}")
        return result

    def __str__(self) -> str:
        return " ∨ ".join(f"({p})" for p in self.parts)


@dataclass(frozen=True)
class Implies(Formula):
    premise: Formula
    conclusion: Formula

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        p = self.premise.eval(model, env, trace, depth + 1)
        q = self.conclusion.eval(model, env, trace, depth + 1)
        result = (not p) or q
        if trace is not None:
            trace.append("  " * depth + f"({self}) -> {result}")
        return result

    def __str__(self) -> str:
        return f"({self.premise}) ⇒ ({self.conclusion})"


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = env or {}
        left_val = self.left.eval(model, env, trace, depth + 1)
        right_val = self.right.eval(model, env, trace, depth + 1)
        result = left_val == right_val
        if trace is not None:
            trace.append("  " * depth + f"({self}) -> {result}")
        return result

    def __str__(self) -> str:
        return f"({self.left}) ⇔ ({self.right})"


@dataclass(frozen=True)
class ForAll(Formula):
    var: str
    body: Formula

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = dict(env or {})
        if trace is not None:
            trace.append("  " * depth + f"∀{self.var}: check every object in domain")
        all_true = True
        for obj in model.domain:
            env[self.var] = obj
            value = self.body.eval(model, env, trace, depth + 1)
            if trace is not None:
                trace.append("  " * (depth + 1) + f"with {self.var} = {obj}: {value}")
            if not value:
                all_true = False
        if trace is not None:
            trace.append("  " * depth + f"∀{self.var} result -> {all_true}")
        return all_true

    def __str__(self) -> str:
        return f"∀{self.var} ({self.body})"


@dataclass(frozen=True)
class Exists(Formula):
    var: str
    body: Formula

    def eval(self, model: "FOLModel", env: Optional[Dict[str, str]] = None,
             trace: Optional[List[str]] = None, depth: int = 0) -> bool:
        env = dict(env or {})
        if trace is not None:
            trace.append("  " * depth + f"∃{self.var}: look for at least one object that works")
        any_true = False
        for obj in model.domain:
            env[self.var] = obj
            value = self.body.eval(model, env, trace, depth + 1)
            if trace is not None:
                trace.append("  " * (depth + 1) + f"with {self.var} = {obj}: {value}")
            if value:
                any_true = True
        if trace is not None:
            trace.append("  " * depth + f"∃{self.var} result -> {any_true}")
        return any_true

    def __str__(self) -> str:
        return f"∃{self.var} ({self.body})"


@dataclass
class FOLModel:
    domain: Tuple[str, ...]
    constants: Dict[str, str]
    relations: Dict[str, Set[Tuple[str, ...]]]
    functions: Dict[str, Dict[Tuple[str, ...], str]]

    def check_domain(self) -> None:
        d = set(self.domain)
        for name, value in self.constants.items():
            if value not in d:
                raise EvaluationError(f"Constant {name} points outside the domain: {value}")
        for fname, mapping in self.functions.items():
            for args, value in mapping.items():
                if value not in d:
                    raise EvaluationError(f"Function {fname}{args} returns outside the domain: {value}")
                for arg in args:
                    if arg not in d:
                        raise EvaluationError(f"Function {fname}{args} has argument outside the domain: {arg}")
        for rname, tuples in self.relations.items():
            for tup in tuples:
                for item in tup:
                    if item not in d:
                        raise EvaluationError(f"Relation {rname}{tup} mentions object outside the domain: {item}")


def evaluate_and_show(formula: Formula, model: FOLModel, no_color: bool = False,
                      show_trace: bool = True) -> bool:
    trace: List[str] = []
    result = formula.eval(model, trace=trace)
    print(color("Formula: ", Style.BOLD, Style.BLUE, no_color=no_color) + str(formula))
    print(color("Result:  ", Style.BOLD, Style.BLUE, no_color=no_color) + truth_color(result, no_color=no_color))
    if show_trace:
        print(color("Trace:", Style.BOLD, Style.DIM, no_color=no_color))
        for line in trace:
            print("  " + line)
    return result


# -----------------------------------------------------------------------------
# Section 8.1: representation revisited
# -----------------------------------------------------------------------------


def demo_representation(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.1 Representation Revisited: why first-order logic matters", no_color)
    wrap_print(
        "Propositional logic gives each small fact its own symbol. First-order logic adds objects, "
        "relations, functions, and quantifiers. That lets us write one general rule instead of many "
        "nearly identical rules."
    )
    print()
    print(color("Propositional style for a 4 x 4 Wumpus grid:", Style.BOLD, no_color=no_color))
    examples = [
        "B_1_1 ⇔ (P_1_2 ∨ P_2_1)",
        "B_1_2 ⇔ (P_1_1 ∨ P_1_3 ∨ P_2_2)",
        "B_1_3 ⇔ (P_1_2 ∨ P_1_4 ∨ P_2_3)",
        "... one rule for every square ...",
    ]
    for e in examples:
        print("   " + color(e, Style.YELLOW, no_color=no_color))

    print("\n" + color("First-order style:", Style.BOLD, no_color=no_color))
    fol_rule = "∀s  Breezy(s) ⇔ ∃p (Pit(p) ∧ Adjacent(p, s))"
    print("   " + color(fol_rule, Style.GREEN, Style.BOLD, no_color=no_color))

    print()
    print(color("Axiom count comparison", Style.BOLD, Style.BLUE, no_color=no_color))
    print("   Grid size       Propositional breeze rules       First-order breeze rules")
    print("   ------------------------------------------------------------------------")
    for n in [4, 8, 16, 100]:
        prop_rules = n * n
        print(f"   {n:>3} x {n:<3}      {prop_rules:>8}                         {1:>3}")

    teacher_note(
        "Ask students: Which representation would you rather maintain for a 100 x 100 game? "
        "This is the core reason Chapter 8 moves from propositional logic to first-order logic.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Section 8.2: model, symbols, terms, atoms, quantifiers
# -----------------------------------------------------------------------------


def make_kingdom_model() -> FOLModel:
    domain = (
        "Richard",
        "John",
        "RichardLeg",
        "JohnLeg",
        "Crown",
        "NoLeg",
    )
    constants = {
        "Richard": "Richard",
        "John": "John",
        "TheCrown": "Crown",
    }
    relations = {
        "Brother": {("Richard", "John"), ("John", "Richard")},
        "OnHead": {("Crown", "John")},
        "Person": {("Richard",), ("John",)},
        "King": {("John",)},
        "Crown": {("Crown",)},
        "Leg": {("RichardLeg",), ("JohnLeg",)},
        # For nested quantifier examples.
        "Loves": {("Richard", "John"), ("John", "John"), ("Crown", "John")},
    }
    functions = {
        "LeftLeg": {
            ("Richard",): "RichardLeg",
            ("John",): "JohnLeg",
            ("RichardLeg",): "NoLeg",
            ("JohnLeg",): "NoLeg",
            ("Crown",): "NoLeg",
            ("NoLeg",): "NoLeg",
        }
    }
    model = FOLModel(domain, constants, relations, functions)
    model.check_domain()
    return model


def print_kingdom_diagram(model: FOLModel, no_color: bool = False) -> None:
    subheader("A tiny first-order model", no_color)
    print("Objects in the domain:")
    for obj in model.domain:
        style = Style.DIM if obj == "NoLeg" else Style.WHITE
        print("  " + color(obj, style, no_color=no_color))
    print()
    print(color("Relations:", Style.BOLD, no_color=no_color))
    print("  " + color("Brother", Style.CYAN, no_color=no_color) + ": Richard <--> John")
    print("  " + color("OnHead", Style.CYAN, no_color=no_color) + ": Crown ---> John")
    print("  " + color("Person", Style.CYAN, no_color=no_color) + ": Richard, John")
    print("  " + color("King", Style.CYAN, no_color=no_color) + ": John")
    print("  " + color("Crown", Style.CYAN, no_color=no_color) + ": Crown")
    print()
    print(color("Function:", Style.BOLD, no_color=no_color))
    print("  " + color("LeftLeg(Richard)", Style.MAGENTA, no_color=no_color) + " = RichardLeg")
    print("  " + color("LeftLeg(John)", Style.MAGENTA, no_color=no_color) + " = JohnLeg")
    print("  " + color("LeftLeg(Crown)", Style.MAGENTA, no_color=no_color) + " = NoLeg  " + color("(a harmless total-function placeholder)", Style.DIM, no_color=no_color))
    print()
    print("        Crown")
    print("          | OnHead")
    print("          v")
    print("  Richard <------ Brother ------> John")
    print("     | LeftLeg                    | LeftLeg")
    print("     v                            v")
    print("  RichardLeg                   JohnLeg")


def demo_model(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.2 First-Order Logic Models: objects, relations, functions", no_color)
    model = make_kingdom_model()
    print_kingdom_diagram(model, no_color)

    formulas = [
        Pred("Brother", [Const("Richard"), Const("John")]),
        Not(Pred("Brother", [Func("LeftLeg", [Const("Richard")]), Const("John")])) ,
        ForAll("x", Implies(Pred("King", [Var("x")]), Pred("Person", [Var("x")]))),
        Exists("x", And(Pred("Crown", [Var("x")]), Pred("OnHead", [Var("x"), Const("John")]))),
        Exists("x", Implies(Pred("Crown", [Var("x")]), Pred("OnHead", [Var("x"), Const("John")]))),
    ]

    explanations = [
        "Atomic sentence: a predicate applied to terms.",
        "Complex sentence with a function term: LeftLeg(Richard) names an object.",
        "Universal quantifier: every king is a person.",
        "Existential quantifier with AND: some object is a crown and is on John's head.",
        "Existential with implication: usually too weak. It becomes true if any object is not a crown.",
    ]
    for exp, f in zip(explanations, formulas):
        wait_if_needed(args.pause)
        subheader(exp, no_color)
        evaluate_and_show(f, model, no_color=no_color, show_trace=args.trace)

    teacher_note(
        "Pause on the last example. It shows a classic FOL translation trap: ∃ with ⇒ often says "
        "almost nothing, because an implication with a false premise is true.",
        no_color,
    )


def make_loves_model(case: int) -> FOLModel:
    domain = ("Alice", "Bob", "Cara")
    constants = {name: name for name in domain}
    if case == 1:
        loves = {("Alice", "Bob"), ("Bob", "Bob"), ("Cara", "Bob")}
    else:
        loves = {("Alice", "Bob"), ("Bob", "Alice"), ("Cara", "Cara")}
    relations = {"Loves": loves, "Person": {(x,) for x in domain}}
    return FOLModel(domain, constants, relations, functions={})


def print_loves_matrix(model: FOLModel, no_color: bool = False) -> None:
    names = list(model.domain)
    print("\nLoves(x, y) table. Rows are x; columns are y.")
    print("         " + "  ".join(f"{n[:5]:>5}" for n in names))
    for x in names:
        cells = []
        for y in names:
            value = (x, y) in model.relations["Loves"]
            if no_color:
                cells.append(" yes " if value else "  no ")
            else:
                cells.append(color(" YES ", Style.GREEN, no_color=no_color) if value else color("  no ", Style.DIM, no_color=no_color))
        print(f"  {x[:7]:>7} " + " ".join(cells))


def demo_quantifiers(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.2.6 Quantifier Quest: why quantifier order matters", no_color)
    wrap_print(
        "We will test two similar-looking sentences. They are not the same: "
        "∀x ∃y Loves(x,y) means everybody loves somebody. "
        "∃y ∀x Loves(x,y) means there is one person loved by everybody."
    )

    f_everyone_loves_someone = ForAll("x", Exists("y", Pred("Loves", [Var("x"), Var("y")])) )
    f_someone_loved_by_all = Exists("y", ForAll("x", Pred("Loves", [Var("x"), Var("y")])) )

    for case in [1, 2]:
        wait_if_needed(args.pause)
        model = make_loves_model(case)
        subheader(f"Round {case}: inspect the world, then guess the formulas", no_color)
        print_loves_matrix(model, no_color)
        print()
        evaluate_and_show(f_everyone_loves_someone, model, no_color=no_color, show_trace=args.trace)
        print()
        evaluate_and_show(f_someone_loved_by_all, model, no_color=no_color, show_trace=args.trace)

    teacher_note(
        "Class prompt: Ask students to invent a real-life sentence where changing the quantifier "
        "order changes the meaning. Example: everyone has a password vs one password works for everyone.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Section 8.2.8: database semantics vs standard FOL semantics
# -----------------------------------------------------------------------------


def demo_database_semantics(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.2.8 Standard FOL semantics vs database semantics", no_color)
    wrap_print(
        "Suppose the knowledge base says Brother(John, Richard) and Brother(Geoffrey, Richard). "
        "Does that mean John and Geoffrey are Richard's only brothers? In standard first-order logic, "
        "not necessarily. In database semantics, usually yes, because of the unique-names assumption, "
        "closed-world assumption, and domain closure."
    )
    known_facts = [
        "Brother(John, Richard)",
        "Brother(Geoffrey, Richard)",
        "John ≠ Geoffrey",
    ]
    print("\nKnown facts:")
    for f in known_facts:
        print("  " + color(f, Style.GREEN, no_color=no_color))

    wait_if_needed(args.pause)
    subheader("Standard first-order semantics", no_color)
    print(color("Question: ", Style.BOLD, no_color=no_color) + "Can there be another brother named Henry?")
    print(color("Answer:   ", Style.BOLD, no_color=no_color) + truth_color(None, no_color=no_color))
    wrap_print(
        "The KB does not rule out extra unnamed or newly named objects. A model with Brother(Henry, Richard) "
        "can still satisfy the facts above. So the exact-brothers conclusion is not entailed.",
        indent=2,
    )

    wait_if_needed(args.pause)
    subheader("Database semantics", no_color)
    print(color("Extra assumptions:", Style.BOLD, no_color=no_color))
    bullet("Unique names: John, Geoffrey, and Richard name distinct objects.", no_color)
    bullet("Closed world: if an atom is not known true, treat it as false.", no_color)
    bullet("Domain closure: the named constants are all the objects we care about.", no_color)
    print(color("Question: ", Style.BOLD, no_color=no_color) + "Are John and Geoffrey the only brothers of Richard?")
    print(color("Answer:   ", Style.BOLD, no_color=no_color) + truth_color(True, no_color=no_color))

    teacher_note(
        "This is a practical classroom moment: databases often use closed-world thinking, but FOL normally "
        "uses open-world thinking. The same written facts can support different inferences under different semantics.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Wumpus World with FOL-style rules and model checking
# -----------------------------------------------------------------------------

Square = Tuple[int, int]
WumpusModel = Tuple[frozenset[Square], Square]  # pits, wumpus


class WumpusFOLDemo:
    def __init__(self, size: int = 4) -> None:
        self.size = size
        self.start: Square = (1, 1)
        self.actual_pits: Set[Square] = {(3, 1), (3, 3), (4, 4)}
        self.actual_wumpus: Square = (1, 3)
        self.actual_gold: Square = (2, 3)
        self.all_squares: List[Square] = [(x, y) for y in range(1, size + 1) for x in range(1, size + 1)]
        self.observations: List[Tuple[Square, bool, bool, bool]] = []  # square, breeze, stench, glitter
        self._all_worlds: Optional[List[WumpusModel]] = None

    def adjacent(self, s: Square) -> List[Square]:
        x, y = s
        candidates = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [(a, b) for (a, b) in candidates if 1 <= a <= self.size and 1 <= b <= self.size]

    def square_name(self, s: Square) -> str:
        return f"S{s[0]}{s[1]}"

    def percept_at(self, s: Square) -> Tuple[bool, bool, bool]:
        breeze = any(a in self.actual_pits for a in self.adjacent(s))
        stench = any(a == self.actual_wumpus for a in self.adjacent(s))
        glitter = s == self.actual_gold
        return breeze, stench, glitter

    def all_worlds(self) -> List[WumpusModel]:
        if self._all_worlds is not None:
            return self._all_worlds
        candidates = [s for s in self.all_squares if s != self.start]
        worlds: List[WumpusModel] = []
        for w in candidates:
            pit_candidates = [s for s in candidates if s != w]
            # For teaching speed and clarity we enumerate every subset. In a 4 x 4 world this is fine.
            for bits in itertools.product([False, True], repeat=len(pit_candidates)):
                pits = frozenset(s for s, bit in zip(pit_candidates, bits) if bit)
                worlds.append((pits, w))
        self._all_worlds = worlds
        return worlds

    def world_consistent_with_observations(self, world: WumpusModel) -> bool:
        pits, wumpus = world
        for square, breeze, stench, glitter in self.observations:
            expected_breeze = any(a in pits for a in self.adjacent(square))
            expected_stench = any(a == wumpus for a in self.adjacent(square))
            # We keep gold out of the logical uncertainty demo. The actual glitter is shown as a percept.
            if expected_breeze != breeze:
                return False
            if expected_stench != stench:
                return False
            if square in pits or square == wumpus:
                # Agent would be dead; visited squares must be safe.
                return False
        return True

    def consistent_worlds(self) -> List[WumpusModel]:
        return [w for w in self.all_worlds() if self.world_consistent_with_observations(w)]

    def ask_pit(self, square: Square, models: List[WumpusModel]) -> Optional[bool]:
        if not models:
            return None
        values = [square in pits for pits, _ in models]
        if all(values):
            return True
        if not any(values):
            return False
        return None

    def ask_wumpus(self, square: Square, models: List[WumpusModel]) -> Optional[bool]:
        if not models:
            return None
        values = [square == w for _, w in models]
        if all(values):
            return True
        if not any(values):
            return False
        return None

    def ask_ok(self, square: Square, models: List[WumpusModel]) -> Optional[bool]:
        if not models:
            return None
        values = [(square not in pits and square != w) for pits, w in models]
        if all(values):
            return True
        if not any(values):
            return False
        return None

    def possible_pit(self, square: Square, models: List[WumpusModel]) -> bool:
        return any(square in pits for pits, _ in models)

    def possible_wumpus(self, square: Square, models: List[WumpusModel]) -> bool:
        return any(square == w for _, w in models)

    def tell_observation(self, square: Square) -> Tuple[bool, bool, bool]:
        percept = self.percept_at(square)
        self.observations.append((square, *percept))
        return percept

    def print_fol_rules(self, no_color: bool = False) -> None:
        print(color("General FOL-style rules used by the agent:", Style.BOLD, no_color=no_color))
        print("  " + color("∀s  Breezy(s) ⇔ ∃p (Pit(p) ∧ Adjacent(p, s))", Style.GREEN, no_color=no_color))
        print("  " + color("∀s  Smelly(s) ⇔ ∃w (Wumpus(w) ∧ Adjacent(w, s))", Style.GREEN, no_color=no_color))
        print("  " + color("∀s  OK(s) ⇔ ¬Pit(s) ∧ ¬Wumpus(s)", Style.GREEN, no_color=no_color))
        print("  " + color("Exactly one Wumpus exists.", Style.GREEN, no_color=no_color))

    def print_actual_board(self, no_color: bool = False) -> None:
        print(color("Teacher answer key: hidden world", Style.BOLD, Style.YELLOW, no_color=no_color))
        for y in range(self.size, 0, -1):
            row = []
            for x in range(1, self.size + 1):
                s = (x, y)
                label = " . "
                style = Style.DIM
                if s == self.start:
                    label, style = " A ", Style.CYAN
                if s in self.actual_pits:
                    label, style = " P ", Style.RED
                if s == self.actual_wumpus:
                    label, style = " W ", Style.MAGENTA
                if s == self.actual_gold:
                    label, style = " G ", Style.YELLOW
                row.append(color(label, Style.BOLD, style, no_color=no_color))
            print("  " + "".join(row) + f"   y={y}")
        print("   " + "  ".join(str(x) for x in range(1, self.size + 1)) + "    x")

    def cell_label(self, square: Square, agent_square: Square, models: List[WumpusModel], no_color: bool = False) -> str:
        if square == agent_square:
            return color(" A ", Style.BOLD, Style.BG_CYAN, no_color=no_color)
        ok = self.ask_ok(square, models)
        pit = self.ask_pit(square, models)
        wumpus = self.ask_wumpus(square, models)
        if wumpus is True:
            return color("W! ", Style.BOLD, Style.BG_MAGENTA, no_color=no_color)
        if pit is True:
            return color("P! ", Style.BOLD, Style.BG_RED, no_color=no_color)
        if ok is True:
            return color("OK ", Style.BOLD, Style.BG_GREEN, no_color=no_color)
        if self.possible_wumpus(square, models):
            return color("W? ", Style.BOLD, Style.BG_MAGENTA, no_color=no_color)
        if self.possible_pit(square, models):
            return color("P? ", Style.BOLD, Style.BG_YELLOW, no_color=no_color)
        return color(" ? ", Style.BOLD, Style.BG_YELLOW, no_color=no_color)

    def print_knowledge_grid(self, agent_square: Square, models: List[WumpusModel], no_color: bool = False) -> None:
        print(color("Agent's logical map from ASK queries", Style.BOLD, no_color=no_color))
        print(color("Legend: A=agent, OK=known safe, P!=certain pit, W!=certain wumpus, P?/W?=possible", Style.DIM, no_color=no_color))
        for y in range(self.size, 0, -1):
            labels = [self.cell_label((x, y), agent_square, models, no_color) for x in range(1, self.size + 1)]
            print("  " + "".join(labels) + f"   y={y}")
        print("   " + "  ".join(str(x) for x in range(1, self.size + 1)) + "    x")

    def print_observations(self, no_color: bool = False) -> None:
        print(color("TELLed percept history:", Style.BOLD, no_color=no_color))
        if not self.observations:
            print("  " + color("No percepts yet.", Style.DIM, no_color=no_color))
            return
        for t, (s, breeze, stench, glitter) in enumerate(self.observations):
            parts = []
            parts.append("Breeze" if breeze else "¬Breeze")
            parts.append("Stench" if stench else "¬Stench")
            parts.append("Glitter" if glitter else "¬Glitter")
            print(f"  t={t}: At({self.square_name(s)}) ∧ " + " ∧ ".join(parts))

    def print_queries(self, models: List[WumpusModel], no_color: bool = False) -> None:
        checks = [(1, 2), (2, 1), (2, 2), (1, 3), (3, 1), (2, 3)]
        print(color("Sample ASK queries:", Style.BOLD, no_color=no_color))
        for sq in checks:
            print(
                f"  ASK(KB, OK({self.square_name(sq)})) = "
                + truth_color(self.ask_ok(sq, models), no_color=no_color)
                + "   "
                + f"ASK(KB, Pit({self.square_name(sq)})) = "
                + truth_color(self.ask_pit(sq, models), no_color=no_color)
                + "   "
                + f"ASK(KB, Wumpus({self.square_name(sq)})) = "
                + truth_color(self.ask_wumpus(sq, models), no_color=no_color)
            )


def demo_wumpus(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("FOL Wumpus World: colorful logical agent show-and-tell", no_color)
    demo = WumpusFOLDemo()
    demo.print_fol_rules(no_color)
    print()
    if not args.hide_answers:
        demo.print_actual_board(no_color)
        print()
    wrap_print(
        "The agent does not see the hidden board. It receives percepts, TELLs them to the KB, and uses ASK "
        "queries to determine which squares are known safe, possible pits, or possible Wumpus locations. "
        "The important Chapter 8 idea is that the rules are written once with quantifiers over squares."
    )

    path: List[Square] = [(1, 1), (2, 1), (1, 1), (1, 2), (2, 2), (2, 3)]
    actions = ["Start", "Forward", "Backtrack", "Move North", "Move East", "Move North to Gold"]
    for step, (action, square) in enumerate(zip(actions, path)):
        wait_if_needed(args.pause)
        subheader(f"Step {step}: {action}; agent is at {demo.square_name(square)}", no_color)
        breeze, stench, glitter = demo.tell_observation(square)
        print(color("Percept: ", Style.BOLD, no_color=no_color), end="")
        print(
            (color("Breeze ", Style.YELLOW, no_color=no_color) if breeze else color("NoBreeze ", Style.DIM, no_color=no_color))
            + (color("Stench ", Style.MAGENTA, no_color=no_color) if stench else color("NoStench ", Style.DIM, no_color=no_color))
            + (color("Glitter", Style.YELLOW, Style.BOLD, no_color=no_color) if glitter else color("NoGlitter", Style.DIM, no_color=no_color))
        )
        models = demo.consistent_worlds()
        print(color("Number of possible worlds still consistent with the KB: ", Style.BOLD, no_color=no_color) + str(len(models)))
        demo.print_observations(no_color)
        print()
        demo.print_knowledge_grid(square, models, no_color)
        print()
        demo.print_queries(models, no_color)
        if glitter:
            print("\n" + color("Action recommendation: GRAB the gold, then plan a route home.", Style.BOLD, Style.GREEN, no_color=no_color))
        elif square == (1, 2):
            print("\n" + color("Key inference: No breeze at S12 rules out pits at S22 and S13; stench points to Wumpus at S13.", Style.BOLD, Style.YELLOW, no_color=no_color))

    teacher_note(
        "Ask students why a single FOL rule over Adjacent(s,p) is more scalable than writing one propositional "
        "breeze rule for every square.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Section 8.4: knowledge engineering with electronic circuits
# -----------------------------------------------------------------------------


def xor(a: int, b: int) -> int:
    return 1 if a != b else 0


def gate_and(a: int, b: int) -> int:
    return 1 if a == 1 and b == 1 else 0


def gate_or(a: int, b: int) -> int:
    return 1 if a == 1 or b == 1 else 0


@dataclass
class FullAdderResult:
    a: int
    b: int
    cin: int
    x1: int
    a1: int
    x2: int
    a2: int
    o1: int
    sum_bit: int
    carry_bit: int


class FullAdderCircuit:
    """A direct executable version of the one-bit full adder from the chapter."""

    def evaluate(self, a: int, b: int, cin: int) -> FullAdderResult:
        x1 = xor(a, b)
        a1 = gate_and(a, b)
        x2 = xor(x1, cin)
        a2 = gate_and(x1, cin)
        o1 = gate_or(a1, a2)
        return FullAdderResult(a, b, cin, x1, a1, x2, a2, o1, x2, o1)

    def print_fol_axioms(self, no_color: bool = False) -> None:
        print(color("General circuit axioms in FOL style:", Style.BOLD, no_color=no_color))
        axioms = [
            "∀t1,t2 Terminal(t1) ∧ Terminal(t2) ∧ Connected(t1,t2) ⇒ Signal(t1)=Signal(t2)",
            "∀g Gate(g) ∧ Type(g)=AND ⇒ Signal(Out(1,g))=0 ⇔ ∃n Signal(In(n,g))=0",
            "∀g Gate(g) ∧ Type(g)=OR  ⇒ Signal(Out(1,g))=1 ⇔ ∃n Signal(In(n,g))=1",
            "∀g Gate(g) ∧ Type(g)=XOR ⇒ Signal(Out(1,g))=1 ⇔ Signal(In(1,g))≠Signal(In(2,g))",
            "∀g Gate(g) ∧ Type(g)=NOT ⇒ Signal(Out(1,g))≠Signal(In(1,g))",
        ]
        for ax in axioms:
            print("  " + color(ax, Style.GREEN, no_color=no_color))

    def print_circuit(self, r: FullAdderResult, no_color: bool = False) -> None:
        a = onezero(r.a, no_color)
        b = onezero(r.b, no_color)
        c = onezero(r.cin, no_color)
        x1 = onezero(r.x1, no_color)
        a1 = onezero(r.a1, no_color)
        x2 = onezero(r.x2, no_color)
        a2 = onezero(r.a2, no_color)
        o1 = onezero(r.o1, no_color)
        print("\n" + color("One-bit full-adder circuit", Style.BOLD, Style.CYAN, no_color=no_color))
        print("\n")
        print(f"       A={a} ───────┐")
        print(f"                    ├── [X1 XOR] = {x1} ───┐")
        print(f"       B={b} ───────┘                       ├── [X2 XOR] = SUM {x2}")
        print(f"                                            │")
        print(f"       Cin={c} ─────────────────────────────┘")
        print("\n")
        print(f"       A={a} ───────┐")
        print(f"                    ├── [A1 AND] = {a1} ───┐")
        print(f"       B={b} ───────┘                       ├── [O1 OR] = CARRY {o1}")
        print(f"       X1={x1} ─────┐                       │")
        print(f"                    ├── [A2 AND] = {a2} ───┘")
        print(f"       Cin={c} ─────┘")

    def print_step_explanation(self, r: FullAdderResult, no_color: bool = False) -> None:
        print(color("Gate-by-gate reasoning:", Style.BOLD, no_color=no_color))
        lines = [
            f"X1 is XOR(A,B):       {r.a} XOR {r.b} = {r.x1}",
            f"A1 is AND(A,B):       {r.a} AND {r.b} = {r.a1}",
            f"X2 is XOR(X1,Cin):    {r.x1} XOR {r.cin} = {r.x2}  so SUM={r.sum_bit}",
            f"A2 is AND(X1,Cin):    {r.x1} AND {r.cin} = {r.a2}",
            f"O1 is OR(A1,A2):      {r.a1} OR {r.a2} = {r.o1}    so CARRY={r.carry_bit}",
        ]
        for line in lines:
            print("  " + line)

    def truth_table(self) -> List[FullAdderResult]:
        return [self.evaluate(a, b, c) for a, b, c in itertools.product([0, 1], repeat=3)]


def print_full_adder_truth_table(circuit: FullAdderCircuit, no_color: bool = False) -> None:
    print(color("Complete input/output table", Style.BOLD, Style.BLUE, no_color=no_color))
    print("  A B Cin | Sum Carry | Arithmetic check")
    print("  ---------------------------------------")
    for r in circuit.truth_table():
        total = r.a + r.b + r.cin
        expected_sum = total % 2
        expected_carry = 1 if total >= 2 else 0
        ok = (r.sum_bit == expected_sum and r.carry_bit == expected_carry)
        status = color("OK", Style.GREEN, Style.BOLD, no_color=no_color) if ok else color("BAD", Style.RED, Style.BOLD, no_color=no_color)
        print(
            f"  {r.a} {r.b}  {r.cin}  |  {r.sum_bit}     {r.carry_bit}   | "
            f"{r.a}+{r.b}+{r.cin}={total} -> sum {expected_sum}, carry {expected_carry}  {status}"
        )


def demo_circuit(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.4 Knowledge Engineering: the digital circuit logic lab", no_color)
    circuit = FullAdderCircuit()
    circuit.print_fol_axioms(no_color)

    if args.inputs is not None:
        a, b, cin = args.inputs
    else:
        a, b, cin = 1, 0, 1
    wait_if_needed(args.pause)
    subheader(f"Run the circuit with inputs A={a}, B={b}, Cin={cin}", no_color)
    result = circuit.evaluate(a, b, cin)
    circuit.print_circuit(result, no_color)
    circuit.print_step_explanation(result, no_color)

    wait_if_needed(args.pause)
    subheader("Query: Which inputs make SUM=0 and CARRY=1?", no_color)
    answers = []
    for r in circuit.truth_table():
        if r.sum_bit == 0 and r.carry_bit == 1:
            answers.append((r.a, r.b, r.cin))
    print("  ASKVARS would return substitutions like:")
    for a, b, cin in answers:
        print("   " + color(f"{{i1/{a}, i2/{b}, i3/{cin}}}", Style.GREEN, no_color=no_color))

    wait_if_needed(args.pause)
    print()
    print_full_adder_truth_table(circuit, no_color)

    wait_if_needed(args.pause)
    subheader("Debugging moment: what if we forget to assert 1 ≠ 0?", no_color)
    print("  XOR rule instance for X1:")
    print("   " + color("Signal(Out(1,X1)) = 1 ⇔ Signal(In(1,X1)) ≠ Signal(In(2,X1))", Style.GREEN, no_color=no_color))
    print("  If the inputs are 1 and 0, the system needs to know:")
    print("   " + color("1 ≠ 0", Style.YELLOW, Style.BOLD, no_color=no_color))
    print("  Without that fact, a theorem prover may fail to prove the XOR output for mixed inputs.")
    teacher_note(
        "This is the knowledge engineering loop: encode a vocabulary, add axioms, test queries, then debug missing or weak axioms.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Knowledge engineering process checklist
# -----------------------------------------------------------------------------


def demo_engineering_process(args: argparse.Namespace) -> None:
    no_color = args.no_color
    header("8.4.1 The knowledge engineering process", no_color)
    steps = [
        ("Identify the questions", "What must the KB answer? Safe squares? Circuit outputs? Feedback loops?"),
        ("Assemble relevant knowledge", "Collect domain facts before formalizing them."),
        ("Choose the vocabulary", "Pick constants, predicates, and functions."),
        ("Encode general knowledge", "Write axioms such as gate behavior or Wumpus adjacency rules."),
        ("Encode the problem instance", "Add the specific board, circuit, percepts, inputs, or connections."),
        ("Pose queries", "Use ASK/ASKVARS to get answers from the inference procedure."),
        ("Debug and evaluate", "Find missing axioms, weak axioms, and false axioms with test queries."),
    ]
    for i, (name, desc) in enumerate(steps, 1):
        print(color(f"{i}. {name}", Style.BOLD, Style.BLUE, no_color=no_color))
        wrap_print(desc, indent=4)
    teacher_note(
        "Have students apply these seven steps to a domain they know: a board game, a campus map, "
        "a help-desk ticket workflow, or a network security rule set.",
        no_color,
    )


# -----------------------------------------------------------------------------
# Main CLI
# -----------------------------------------------------------------------------


def run_all(args: argparse.Namespace) -> None:
    demos = [
        demo_representation,
        demo_model,
        demo_quantifiers,
        demo_database_semantics,
        demo_wumpus,
        demo_circuit,
        demo_engineering_process,
    ]
    for demo in demos:
        demo(args)
        wait_if_needed(args.pause, "Press Enter for the next demo...")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Colorful classroom demos for Chapter 8: First-Order Logic."
    )
    parser.add_argument(
        "--demo",
        choices=["all", "representation", "model", "quantifiers", "database", "wumpus", "circuit", "engineering"],
        default="all",
        help="Which classroom demo to run.",
    )
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause between major steps for live teaching.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Show detailed formula evaluation traces for FOL model demos.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors.",
    )
    parser.add_argument(
        "--hide-answers",
        action="store_true",
        help="In the Wumpus demo, do not print the teacher answer-key board.",
    )
    parser.add_argument(
        "--inputs",
        nargs=3,
        type=int,
        choices=[0, 1],
        metavar=("A", "B", "CIN"),
        help="For the circuit demo, choose full-adder input bits, e.g. --inputs 1 0 1.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    enable_windows_ansi()
    args = parse_args(argv)
    if args.demo == "all":
        run_all(args)
    elif args.demo == "representation":
        demo_representation(args)
    elif args.demo == "model":
        demo_model(args)
    elif args.demo == "quantifiers":
        demo_quantifiers(args)
    elif args.demo == "database":
        demo_database_semantics(args)
    elif args.demo == "wumpus":
        demo_wumpus(args)
    elif args.demo == "circuit":
        demo_circuit(args)
    elif args.demo == "engineering":
        demo_engineering_process(args)
    else:
        raise AssertionError(args.demo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
