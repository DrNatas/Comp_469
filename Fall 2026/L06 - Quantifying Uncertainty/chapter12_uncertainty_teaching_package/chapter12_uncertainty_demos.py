"""
Chapter 12: Quantifying Uncertainty - classroom demos.

Run all demos:
    python chapter12_uncertainty_demos.py

Run one demo:
    python chapter12_uncertainty_demos.py expected_utility
    python chapter12_uncertainty_demos.py full_joint
    python chapter12_uncertainty_demos.py bayes
    python chapter12_uncertainty_demos.py naive_bayes
    python chapter12_uncertainty_demos.py wumpus
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from math import log, exp
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple
import re
import sys


def normalize(scores: Mapping[str, float]) -> Dict[str, float]:
    """Return a normalized probability distribution from nonnegative scores."""
    total = sum(scores.values())
    if total <= 0:
        raise ValueError("Cannot normalize scores with nonpositive total.")
    return {key: value / total for key, value in scores.items()}


def print_distribution(title: str, dist: Mapping[str, float]) -> None:
    print(f"\n{title}")
    for key, value in sorted(dist.items()):
        print(f"  {key:>12}: {value:.6f}")


# ---------------------------------------------------------------------------
# Demo 1: Maximum expected utility
# ---------------------------------------------------------------------------

def expected_utility(outcomes: Sequence[Tuple[float, float]]) -> float:
    """Compute sum_i P(outcome_i) * U(outcome_i)."""
    return sum(probability * utility for probability, utility in outcomes)


def expected_utility_demo() -> None:
    print("\n=== Demo 1: Expected utility for airport plans ===")
    plans = {
        "A60": [(0.80, 100), (0.20, -500)],
        "A90": [(0.97, 90), (0.03, -500)],
        "A180": [(0.995, 40), (0.005, -500)],
        "A1440": [(0.999, -200), (0.001, -500)],
    }
    utilities = {plan: expected_utility(outcomes) for plan, outcomes in plans.items()}
    for plan, eu in sorted(utilities.items(), key=lambda item: item[1], reverse=True):
        print(f"  {plan:>5}: expected utility = {eu:8.2f}")
    best = max(utilities, key=utilities.get)
    print(f"\nBest plan under these numbers: {best}")
    print("Try changing the utility for waiting or missing the flight and rerun.")


# ---------------------------------------------------------------------------
# Demo 2: Inference with a full joint distribution
# ---------------------------------------------------------------------------

VARIABLES = ("Cavity", "Toothache", "Catch")
# Key order is (Cavity, Toothache, Catch), with 1=True and 0=False.
FULL_JOINT: Dict[Tuple[int, int, int], float] = {
    (1, 1, 1): 0.108,
    (1, 1, 0): 0.012,
    (1, 0, 1): 0.072,
    (1, 0, 0): 0.008,
    (0, 1, 1): 0.016,
    (0, 1, 0): 0.064,
    (0, 0, 1): 0.144,
    (0, 0, 0): 0.576,
}


def world_matches(world: Tuple[int, int, int], conditions: Mapping[str, bool]) -> bool:
    assignment = dict(zip(VARIABLES, map(bool, world)))
    return all(assignment[var] == value for var, value in conditions.items())


def probability(conditions: Mapping[str, bool]) -> float:
    """Sum entries in the full joint that satisfy the given conditions."""
    return sum(prob for world, prob in FULL_JOINT.items() if world_matches(world, conditions))


def posterior_from_joint(query_var: str, evidence: Mapping[str, bool]) -> Dict[str, float]:
    """Compute P(query_var | evidence) by summing and normalizing full-joint entries."""
    scores = {}
    for value in (True, False):
        conditions = dict(evidence)
        conditions[query_var] = value
        scores[str(value)] = probability(conditions)
    return normalize(scores)


def full_joint_demo() -> None:
    print("\n=== Demo 2: Full joint inference ===")
    print(f"Full joint sums to: {sum(FULL_JOINT.values()):.3f}")
    print(f"P(Cavity) = {probability({'Cavity': True}):.3f}")
    p_cavity_given_toothache = posterior_from_joint("Cavity", {"Toothache": True})
    print_distribution("P(Cavity | Toothache)", p_cavity_given_toothache)
    p_cavity_given_toothache_catch = posterior_from_joint(
        "Cavity", {"Toothache": True, "Catch": True}
    )
    print_distribution("P(Cavity | Toothache, Catch)", p_cavity_given_toothache_catch)


# ---------------------------------------------------------------------------
# Demo 3: Bayes' rule and base rates
# ---------------------------------------------------------------------------

def bayes_posterior(prior_cause: float, likelihood_e_given_cause: float, prior_evidence: float) -> float:
    """Compute P(cause | evidence) from P(evidence | cause), P(cause), and P(evidence)."""
    return likelihood_e_given_cause * prior_cause / prior_evidence


def bayes_demo() -> None:
    print("\n=== Demo 3: Bayes' rule and base rates ===")
    p_stiff_given_meningitis = 0.70
    p_stiff = 0.01
    priors = [1 / 50_000, 1 / 10_000, 1 / 1_000, 1 / 100]
    print("Assume P(stiff neck | meningitis) = 0.70 and P(stiff neck) = 0.01.")
    for prior in priors:
        posterior = bayes_posterior(prior, p_stiff_given_meningitis, p_stiff)
        print(f"  P(meningitis)={prior:9.6f} -> P(meningitis | stiff)={posterior:9.6f}")
    print("\nThe posterior rises with the prior. Base rates matter.")


# ---------------------------------------------------------------------------
# Demo 4: Bernoulli naive Bayes for tiny text classification
# ---------------------------------------------------------------------------

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def train_bernoulli_naive_bayes(docs: Sequence[Tuple[str, str]], alpha: float = 1.0):
    """Train a tiny Bernoulli naive Bayes model with Laplace smoothing."""
    labels = sorted({label for label, _ in docs})
    vocabulary = sorted({word for _, text in docs for word in tokenize(text)})
    docs_by_label: Dict[str, List[set[str]]] = defaultdict(list)
    for label, text in docs:
        docs_by_label[label].append(set(tokenize(text)))

    total_docs = len(docs)
    priors = {label: len(docs_by_label[label]) / total_docs for label in labels}
    likelihoods: Dict[str, Dict[str, float]] = {label: {} for label in labels}
    for label in labels:
        n_label = len(docs_by_label[label])
        for word in vocabulary:
            containing_word = sum(1 for words in docs_by_label[label] if word in words)
            # Bernoulli probability that the word is present in a document of this label.
            likelihoods[label][word] = (containing_word + alpha) / (n_label + 2 * alpha)
    return labels, vocabulary, priors, likelihoods


def predict_bernoulli_naive_bayes(model, text: str) -> Dict[str, float]:
    labels, vocabulary, priors, likelihoods = model
    words = set(tokenize(text))
    log_scores = {}
    for label in labels:
        score = log(priors[label])
        for word in vocabulary:
            p_present = likelihoods[label][word]
            score += log(p_present if word in words else 1 - p_present)
        log_scores[label] = score

    # Convert log scores back to normalized probabilities safely.
    max_log = max(log_scores.values())
    scores = {label: exp(value - max_log) for label, value in log_scores.items()}
    return normalize(scores)


def naive_bayes_demo() -> None:
    print("\n=== Demo 4: Naive Bayes text classification ===")
    training_docs = [
        ("business", "stocks rallied as earnings optimism lifted indexes"),
        ("business", "market indexes gained after strong quarterly earnings"),
        ("weather", "heavy rain caused flooding and warnings along the coast"),
        ("weather", "rain and flood warnings continued through monday"),
        ("sports", "the team won after a strong first quarter"),
        ("sports", "the coach praised the team after the game"),
    ]
    model = train_bernoulli_naive_bayes(training_docs)
    samples = [
        "stocks and earnings lifted the market",
        "heavy rain and flood warnings",
        "team gained momentum in the first quarter",
    ]
    for sample in samples:
        posterior = predict_bernoulli_naive_bayes(model, sample)
        print_distribution(f"Document: {sample!r}", posterior)


# ---------------------------------------------------------------------------
# Demo 5: Wumpus world pit probabilities by enumeration
# ---------------------------------------------------------------------------

Square = Tuple[int, int]


def neighbors(square: Square) -> List[Square]:
    x, y = square
    candidates = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    return [(a, b) for a, b in candidates if 1 <= a <= 4 and 1 <= b <= 4]


def has_breeze(config: Mapping[Square, bool], square: Square) -> bool:
    return any(config.get(nb, False) for nb in neighbors(square))


def pit_configuration_probability(config: Mapping[Square, bool], pit_prior: float = 0.2) -> float:
    # The starting square (1,1) is excluded from the independent pit prior.
    non_start_squares = [(i, j) for i in range(1, 5) for j in range(1, 5) if (i, j) != (1, 1)]
    n_pits = sum(1 for square in non_start_squares if config.get(square, False))
    n_non_pits = len(non_start_squares) - n_pits
    return (pit_prior ** n_pits) * ((1 - pit_prior) ** n_non_pits)


def wumpus_posterior(pit_prior: float = 0.2) -> Dict[Square, float]:
    all_non_start = [(i, j) for i in range(1, 5) for j in range(1, 5) if (i, j) != (1, 1)]
    known_no_pit = {(1, 1), (1, 2), (2, 1)}
    observed_breezes = {(1, 1): False, (1, 2): True, (2, 1): True}
    query_squares = [(1, 3), (2, 2), (3, 1)]

    total_weight = 0.0
    query_weights = Counter({square: 0.0 for square in query_squares})

    for bits in product([False, True], repeat=len(all_non_start)):
        config = dict(zip(all_non_start, bits))
        config[(1, 1)] = False

        if any(config.get(square, False) for square in known_no_pit):
            continue
        if any(has_breeze(config, square) != observed for square, observed in observed_breezes.items()):
            continue

        weight = pit_configuration_probability(config, pit_prior)
        total_weight += weight
        for square in query_squares:
            if config.get(square, False):
                query_weights[square] += weight

    if total_weight <= 0:
        raise ValueError("Evidence had zero probability under the model.")
    return {square: query_weights[square] / total_weight for square in query_squares}


def wumpus_demo() -> None:
    print("\n=== Demo 5: Wumpus world pit probabilities ===")
    posterior = wumpus_posterior(pit_prior=0.2)
    for square, probability_value in posterior.items():
        print(f"  P(pit at {square} | evidence) = {probability_value:.3f}")
    print("\nThe center frontier square (2,2) is much riskier than (1,3) or (3,1).")


DEMOS = {
    "expected_utility": expected_utility_demo,
    "full_joint": full_joint_demo,
    "bayes": bayes_demo,
    "naive_bayes": naive_bayes_demo,
    "wumpus": wumpus_demo,
}


def run_all() -> None:
    for demo in DEMOS.values():
        demo()


def main(argv: Sequence[str]) -> None:
    if len(argv) <= 1 or argv[1] == "all":
        run_all()
        return
    name = argv[1].lower()
    if name not in DEMOS:
        available = ", ".join(["all", *DEMOS.keys()])
        raise SystemExit(f"Unknown demo {name!r}. Available: {available}")
    DEMOS[name]()


if __name__ == "__main__":
    main(sys.argv)
