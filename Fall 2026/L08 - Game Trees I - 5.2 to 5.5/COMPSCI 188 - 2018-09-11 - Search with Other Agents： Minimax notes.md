# Search with Other Agents: Minimax

## Lecture overview

This lecture introduces adversarial search for deterministic, perfect-information games. Unlike ordinary planning, an agent cannot simply choose a sequence of actions because another agent is actively changing the state of the world. The result of search is therefore a **strategy** (or policy): what action to take in every situation that may arise.

The main topics are:

- Modeling games as state-space search problems
- Zero-sum games and utility
- Game trees and minimax values
- Alpha–beta pruning
- Depth-limited search and evaluation functions
- Iterative deepening and practical game-playing agents

## 1. Game-playing AI

Game-playing programs are useful examples of intelligent decision-making because they must:

1. Consider possible future actions.
2. Account for an opponent who is trying to prevent success.
3. Choose an action under limited computational time.

Examples discussed in the lecture include checkers, chess, Go, and Pac-Man. A program being stronger than a human champion is different from a game being **solved**. A solved game has a mathematically established result under optimal play—for example, a forced win or a forced draw.

Go was historically difficult for classical search because its branching factor is very large (roughly 300 legal moves in a typical position). Modern systems combine search with learned evaluation functions and methods such as Monte Carlo Tree Search.

## 2. Types of games

Games can be classified along several dimensions:

| Dimension | Possibilities | Examples |
|---|---|---|
| Randomness | Deterministic / stochastic | Chess / backgammon |
| Number of agents | One / two / many | Solitaire / chess / poker |
| Utility relationship | Zero-sum / non-zero-sum | Pure competition / situations with possible cooperation |
| Information | Perfect / imperfect | Chess / poker |

This lecture focuses on **two-player, deterministic, perfect-information, zero-sum games**. Stochastic games and games with independent utilities require extensions that are covered later.

## 3. Formal game representation

A game can be represented by:

- A set of states (S)
- An initial state (s_0)
- A set of players, usually alternating turns
- An action function (A(s)), giving the legal actions in state (s)
- A transition function (Result(s,a)), giving the state after action (a)
- A terminal test (Terminal(s)), indicating whether the game is over
- A utility function (U(s)), assigning a value to terminal states

For a simple game, utilities might be:

\[
U(s) =
\begin{cases}
+1 & \text{win}\\
0 & \text{draw}\\
-1 & \text{loss}
\end{cases}
\]

More complex games may use a wider range of values. In Pac-Man, for example, utility can include points for food, penalties for time, and penalties for being caught.

The desired solution is a **policy**:

\[
\pi(s) = \text{the action to take in state }s.
\]

This differs from ordinary search, which often returns one fixed path from the start state to a goal. In a game, the opponent may make different moves, so the agent needs a contingent strategy.

## 4. Zero-sum games

In a zero-sum game, one player's gain is the other player's loss. If MAX's utility is (u), MIN's utility is (-u).

Consequences:

- Only one utility number is needed for each terminal state.
- MAX tries to maximize the utility.
- MIN tries to minimize the same utility.
- A rational player must assume that the opponent will choose the move that is worst for it.

Not all games are zero-sum. In a cooperative or non-zero-sum setting, agents may have separate utilities, and both agents may benefit from the same outcome.

## 5. Game trees

A **game tree** represents the possible future states of a game:

- Each node is a game state.
- Each edge is a legal action.
- Levels alternate between players.
- Leaves are terminal states with known utilities.

For a one-player game, the value of a state is the best achievable value among its children:

\[
V(s) = \max_{a \in A(s)} V(Result(s,a)).
\]

With an opponent, the value depends on whose turn it is. The player making the decision at a node is assumed to choose rationally.

## 6. Minimax

**Minimax** computes the value of a state assuming both players play optimally.

- At a MAX node, choose the child with the greatest value.
- At a MIN node, choose the child with the smallest value.
- At a terminal node, return the utility of that state.

The recursive definition is:

\[
V(s) =
\begin{cases}
U(s) & \text{if } Terminal(s)\\
\max\limits_{a \in A(s)} V(Result(s,a)) & \text{if MAX moves}\\
\min\limits_{a \in A(s)} V(Result(s,a)) & \text{if MIN moves}
\end{cases}
\]

### Minimax pseudocode

```text
MINIMAX-DECISION(state):
    choose the action a with the highest MIN-VALUE(Result(state, a))

MAX-VALUE(state):
    if TERMINAL(state):
        return UTILITY(state)
    value = -infinity
    for action in ACTIONS(state):
        value = max(value, MIN-VALUE(RESULT(state, action)))
    return value

MIN-VALUE(state):
    if TERMINAL(state):
        return UTILITY(state)
    value = +infinity
    for action in ACTIONS(state):
        value = min(value, MAX-VALUE(RESULT(state, action)))
    return value
```

### Interpreting minimax values

The minimax value is not necessarily the most desirable leaf visible in the tree. It is the outcome the player can **guarantee** against a perfect opponent.

For example, if MAX can see a very high-valued leaf but MIN controls the node immediately above it, MIN will avoid that leaf whenever another lower-valued outcome is available. MAX must therefore select the branch whose worst case is best.

This is the key idea:

> MAX chooses the move with the best worst-case result.

## 7. Tic-tac-toe as a minimax example

Tic-tac-toe is a small enough game to search to the end:

1. The initial state is an empty board.
2. A player places a mark in an empty square.
3. Players alternate turns.
4. The game ends when a player has three in a row or the board is full.

Assign utilities such as (+1) for a MAX win, (0) for a draw, and (-1) for a MAX loss. Minimax backs these values up through the tree.

With perfect play, the initial tic-tac-toe position has value 0: neither player can force a win, so optimal play results in a draw.

## 8. Complexity of minimax

Let:

- (b) = branching factor, the average number of legal actions per state
- (m) = maximum depth of the game tree

Minimax has approximately:

\[
O(b^m)
\]

time complexity and (O(bm)) space complexity when implemented with depth-first recursion.

The exponential time is the main problem. Even if each individual action is easy to generate, the number of possible sequences grows rapidly with depth. Searching all the way to the end is practical for small games such as tic-tac-toe, but not for games such as chess or Go.

## 9. Alpha–beta pruning

**Alpha–beta pruning** improves minimax by avoiding branches that cannot affect the final decision. It returns exactly the same minimax value as full minimax, but may examine far fewer nodes.

The central reasoning is:

- If MAX already has a way to obtain value (v), MAX will never choose a branch that MIN can force below (v).
- If MIN already has a way to hold MAX to value (v), MIN will never choose a branch that allows MAX to obtain more than (v).
- Once a branch cannot improve the decision for the player whose turn it is, the remainder of that branch can be ignored.

### Alpha and beta

- **Alpha**: the best value MAX can guarantee so far along the current path.
- **Beta**: the best value MIN can guarantee so far along the current path.

Initially:

\[
\alpha = -\infty, \qquad \beta = +\infty.
\]

The pruning conditions are:

- At a MAX node, prune when the current value is at least beta.
- At a MIN node, prune when the current value is at most alpha.

Equivalently, prune whenever:

\[
\alpha \geq \beta.
\]

### Alpha–beta pseudocode

```text
MAX-VALUE(state, alpha, beta):
    if TERMINAL(state):
        return UTILITY(state)

    value = -infinity
    for action in ACTIONS(state):
        value = max(value, MIN-VALUE(RESULT(state, action), alpha, beta))
        if value >= beta:
            return value          // beta cutoff
        alpha = max(alpha, value)
    return value

MIN-VALUE(state, alpha, beta):
    if TERMINAL(state):
        return UTILITY(state)

    value = +infinity
    for action in ACTIONS(state):
        value = min(value, MAX-VALUE(RESULT(state, action), alpha, beta))
        if value <= alpha:
            return value            // alpha cutoff
        beta = min(beta, value)
    return value
```

### Why pruning is safe

Suppose MAX has already found a branch worth 8. MAX will never choose a different branch if MIN can force that branch to 4 or less. The rest of that branch is irrelevant, regardless of whether a later leaf contains a high value, because MIN controls the choice that leads toward the low value.

Alpha–beta pruning does not change the game-theoretic answer. It only avoids proving information that is not needed.

### Effect of move ordering

Pruning effectiveness depends strongly on the order in which actions are explored.

- Good moves explored first produce more cutoffs.
- Poor ordering may produce little pruning.
- With ideal ordering, the effective time complexity can improve from (O(b^m)) to approximately:

\[
O(b^{m/2}).
\]

This roughly doubles the depth that can be searched with the same computation budget.

Move ordering can be improved by exploring actions that the evaluation function considers promising first.

## 10. Depth-limited minimax

For large games, the agent cannot search until terminal states. Instead, it stops after a fixed depth and treats the frontier states as if they were terminal.

The procedure is:

1. Search to a chosen depth.
2. If a real terminal state is reached, use its true utility.
3. Otherwise, apply an evaluation function to the frontier state.
4. Back up those estimated values using minimax or alpha–beta pruning.

Depth-limited search sacrifices the guarantee of optimal play because the frontier values are estimates rather than actual game outcomes. However, it allows the agent to make a decision within a practical time limit.

## 11. Evaluation functions

An **evaluation function** estimates how favorable a non-terminal state is for MAX:

\[
Eval(s) \approx V(s).
\]

A useful evaluation function should:

- Assign higher values to positions that are better for MAX.
- Assign lower values to positions that are better for MIN.
- Agree with the true utility when a terminal state is reached.
- Be fast enough to evaluate many states.

### Example: chess

A chess evaluation function might combine:

\[
Eval(s) =
w_1(\text{material advantage})
+ w_2(\text{mobility})
+ w_3(\text{king safety})
+ w_4(\text{positional features}).
\]

Material advantage could weight queens, rooks, bishops, knights, and pawns differently. More sophisticated systems use many features and may learn the weights from data.

### Example: Pac-Man

Using only the current score can produce poor behavior when the search horizon is short. Two states can have the same immediate score even though one has made more progress toward future food or is safer from ghosts.

Useful Pac-Man features may include:

- Distance to the nearest food pellet
- Number of remaining pellets
- Distance to ghosts
- Whether a ghost is vulnerable
- Availability of escape routes
- Distance to power pellets
- Progress toward a strategically useful position

An evaluation function must provide enough information to distinguish states that look identical at the current score but have different futures.

## 12. The horizon effect and shallow search

A shallow agent may behave strangely because it cannot see the consequences of an action beyond its search depth. This is sometimes called a **horizon effect**.

For example, Pac-Man may repeatedly move back and forth when two choices appear equally good within the shallow search horizon. The agent is solving the truncated problem, not the full game. A better evaluation function can give a small preference to progress, safety, or strategic positioning and break the tie.

Greater search depth generally improves decisions because the agent can use true terminal utilities—or better-informed estimates closer to the end of the game.

## 13. Iterative deepening

When the agent does not know exactly how much time is available, it can use **iterative deepening**:

1. Search to depth 1.
2. If time remains, search to depth 2.
3. Continue increasing the depth.
4. If time runs out, use the best completed result from the previous iteration.

The result from a completed shallow search is always available as a fallback. In practice, most of the computation is spent on the deepest completed iteration.

Iterative deepening is particularly useful in timed games, where returning a legal move before the deadline is essential.

## 14. Evaluation functions and alpha–beta together

These techniques solve different problems:

- An evaluation function estimates the value of a state when full search is impossible.
- Alpha–beta pruning skips subtrees that cannot affect the result.

They can also reinforce each other. If the evaluation function helps identify promising moves, the agent can search those moves first and obtain more alpha–beta cutoffs.

In some settings, an evaluation function may provide a bound on the possible value of a state. A sufficiently strong bound can also support early pruning.

## 15. Meta-reasoning

Alpha–beta pruning illustrates **meta-reasoning**: performing computation to decide which other computations are unnecessary.

The agent spends a small amount of effort maintaining alpha and beta bounds. Those bounds allow it to avoid exploring entire subtrees, saving much more computation overall.

## 16. Practical lessons for game agents

When implementing a game-playing agent:

1. Define the state, legal actions, transition function, terminal test, and utility clearly.
2. Use minimax when the full game tree is small enough to search.
3. Add alpha–beta pruning for exact search with fewer expansions.
4. Order actions so promising moves are considered first.
5. Use depth limits for games whose trees are too large.
6. Design an evaluation function that captures future as well as immediate value.
7. Use iterative deepening when operating under a time limit.
8. Return the best move from the last completed search before the deadline.
9. Test the evaluation function on hand-selected positions whose relative quality is understood.
10. Remember that the agent is optimizing against an opponent, not simply following the highest-valued path it can see.

## Key takeaways

- Adversarial search models decision-making when another agent actively opposes you.
- A policy is needed because the opponent's action is not under your control.
- In zero-sum games, MAX maximizes utility and MIN minimizes it.
- Minimax computes the result of optimal play by backing values up the game tree.
- Alpha–beta pruning gives the same answer as minimax while skipping irrelevant branches.
- Move ordering determines how effective alpha–beta pruning is.
- Depth-limited search replaces exact terminal utilities with evaluation-function estimates.
- Iterative deepening provides a reliable move under an uncertain time budget.
- Search depth and evaluation quality work together: deeper search delays approximation, while a better evaluation function makes shallow search more useful.
