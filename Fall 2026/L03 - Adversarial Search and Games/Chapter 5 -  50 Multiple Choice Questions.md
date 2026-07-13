# Chapter 5 Multiple-Choice Questions: Adversarial Search and Games

Based only on Chapter 5: *Adversarial Search and Games*, including game theory, minimax, alpha-beta pruning, heuristic evaluation, Monte Carlo tree search, stochastic games, partially observable games, and game-search limitations.    

---

## Questions

1. **What is the main focus of adversarial search?**
   A. Searching in environments with no uncertainty
   B. Searching when other agents have conflicting goals
   C. Searching only in single-agent pathfinding problems
   D. Searching without utility values

2. **Why are games useful for studying adversarial search in AI?**
   A. They usually have vague rules and unlimited actions
   B. Their states, actions, and rules are often clearly defined
   C. They avoid competition between agents
   D. They do not require search trees

3. **Which stance explicitly models opponents as agents trying to defeat us?**
   A. Treating agents as an economy
   B. Treating agents as random noise
   C. Adversarial game-tree search
   D. Ignoring other agents

4. **In Chapter 5, “perfect information” means the game is:**
   A. Fully observable
   B. Randomly observable
   C. Partially observable
   D. Unknown to both players

5. **A zero-sum game is one in which:**
   A. Both players always win
   B. One player’s gain is exactly the other player’s loss
   C. No player receives utility
   D. Utilities are always zero

6. **In a two-player zero-sum game, MAX is the player who:**
   A. Minimizes the opponent’s branching factor
   B. Tries to maximize the utility value
   C. Always moves second
   D. Chooses randomly

7. **MIN is called MIN because that player:**
   A. Has fewer legal actions
   B. Tries to minimize MAX’s utility
   C. Always loses in minimax
   D. Controls the terminal states only

8. **Which formal game component specifies the starting setup of the game?**
   A. ACTIONS(s)
   B. RESULT(s, a)
   C. S₀
   D. UTILITY(s, p)

9. **Which formal game component tells whose turn it is in a state?**
   A. TO-MOVE(s)
   B. ACTION-COST(s, a, s′)
   C. PATH-COST(s)
   D. HEURISTIC(s)

10. **Which function returns the legal moves available from a state?**
    A. RESULT(s, a)
    B. ACTIONS(s)
    C. IS-TERMINAL(s)
    D. UTILITY(s, p)

11. **Which function defines the state reached after taking an action?**
    A. RESULT(s, a)
    B. TO-MOVE(s)
    C. UTILITY(s, p)
    D. IS-CUTOFF(s, d)

12. **A terminal state is a state where:**
    A. The search depth is always zero
    B. The game is over
    C. MAX always wins
    D. MIN has no utility

13. **The utility function gives:**
    A. The path cost from the root
    B. The final numeric value for a player at a terminal state
    C. The number of legal moves
    D. The current search depth

14. **A complete game tree contains:**
    A. Only the current player’s best moves
    B. Every possible sequence of moves to terminal states
    C. Only terminal states
    D. Only heuristic estimates

15. **In tic-tac-toe, why is the game tree much easier to analyze than chess?**
    A. Tic-tac-toe has no terminal states
    B. Tic-tac-toe has a much smaller game tree
    C. Chess has no legal actions
    D. Tic-tac-toe is stochastic

16. **A strategy in an adversarial game must often be a conditional plan because:**
    A. The opponent’s moves affect what should be done next
    B. The agent never knows the rules
    C. Terminal states are impossible
    D. All actions have the same value

17. **The minimax value of a terminal state is:**
    A. Its heuristic depth
    B. Its utility
    C. Its branching factor
    D. Its alpha value

18. **At a MAX node, minimax chooses the successor with the:**
    A. Minimum value
    B. Maximum value
    C. Random value
    D. Lowest depth

19. **At a MIN node, minimax chooses the successor with the:**
    A. Minimum value for MAX
    B. Maximum value for MAX
    C. Largest branching factor
    D. Highest alpha value

20. **If a MIN node has leaf utilities 3, 12, and 8, its minimax value is:**
    A. 3
    B. 8
    C. 12
    D. 23

21. **If a MAX root has successor minimax values 3, 2, and 2, MAX should choose:**
    A. The first successor
    B. The second successor
    C. The third successor
    D. Any successor equally

22. **The minimax algorithm explores the game tree primarily using:**
    A. Breadth-first search only
    B. Depth-first recursive search
    C. Random sampling only
    D. Greedy hill climbing

23. **If the branching factor is b and the maximum game-tree depth is m, minimax time complexity is:**
    A. O(b + m)
    B. O(bm)
    C. O(b^m)
    D. O(m / b)

24. **Why is full minimax impractical for games like chess?**
    A. Chess has no utility function
    B. The game tree is too large to search completely
    C. Chess is not turn-taking
    D. MIN never moves

25. **In multiplayer games, utilities are often represented as:**
    A. A single number only
    B. A vector of values, one for each player
    C. A random Boolean value
    D. A path-cost table

26. **In a three-player game with players A, B, and C, a terminal utility vector might represent:**
    A. Only MAX’s utility
    B. Only MIN’s utility
    C. Each player’s utility in that outcome
    D. The number of moves left

27. **Why can alliances emerge in multiplayer games?**
    A. They are always required by the rules
    B. Players may find cooperation useful for selfish reasons
    C. Minimax forbids competition
    D. Utility vectors cannot represent conflict

28. **Alpha-beta pruning improves minimax by:**
    A. Changing the final minimax answer
    B. Ignoring branches that cannot affect the final decision
    C. Removing terminal states from the game
    D. Replacing all utilities with random numbers

29. **In alpha-beta search, alpha represents:**
    A. The best value found so far for MAX along the path
    B. The best value found so far for MIN along the path
    C. The number of terminal states
    D. The probability of a dice roll

30. **In alpha-beta search, beta represents:**
    A. The best lowest-value choice found so far for MIN
    B. The maximum game depth
    C. The utility of the root only
    D. The number of players

31. **A branch can be pruned when:**
    A. It is guaranteed not to affect the final minimax decision
    B. It contains a legal move
    C. It is the first branch searched
    D. It has a terminal state

32. **The effectiveness of alpha-beta pruning depends heavily on:**
    A. Move ordering
    B. The font used to draw the tree
    C. Whether MAX moves second
    D. Whether the game has no utility values

33. **With perfect move ordering, alpha-beta can reduce the effective complexity to roughly:**
    A. O(b^m)
    B. O(b^(m/2))
    C. O(m^b)
    D. O(1)

34. **The purpose of iterative deepening in game search is to:**
    A. Search one depth, then deeper depths, reusing information
    B. Avoid ever using heuristics
    C. Remove the need for legal moves
    D. Guarantee no branching

35. **A transposition table stores:**
    A. Previously evaluated states to avoid repeated work
    B. Only the names of players
    C. Random dice outcomes
    D. The order of moves in a rulebook

36. **A transposition occurs when:**
    A. A player changes utility functions
    B. Different move sequences reach the same position
    C. A game becomes single-agent
    D. A terminal state becomes nonterminal

37. **Claude Shannon’s Type A strategy searches:**
    A. A wide but shallow tree to a fixed depth, then evaluates
    B. Only one random path
    C. No legal moves
    D. Only terminal positions in Go

38. **Claude Shannon’s Type B strategy searches:**
    A. Every possible move equally
    B. Promising lines more deeply while ignoring bad-looking moves
    C. Only chance nodes
    D. Only positions with no opponent

39. **Heuristic alpha-beta search replaces UTILITY at cutoff states with:**
    A. EVAL
    B. ACTIONS
    C. TO-MOVE
    D. RESULT

40. **A cutoff test should return true for:**
    A. Terminal states and selected nonterminal states where search should stop
    B. Only the initial state
    C. Only illegal moves
    D. Every MAX node

41. **A good heuristic evaluation function should be:**
    A. Slow and unrelated to winning chances
    B. Fast and strongly correlated with actual chances of winning
    C. Random and expensive
    D. Independent of the game state

42. **A weighted linear evaluation function combines:**
    A. Features and weights
    B. Dice and cards only
    C. Alpha and beta as player names
    D. Random actions and terminal tests

43. **In the chess material example, a queen is commonly valued at about:**
    A. 1 pawn
    B. 3 pawns
    C. 5 pawns
    D. 9 pawns

44. **Quiescence search tries to avoid evaluating positions that:**
    A. Are stable and quiet
    B. Have obvious pending tactical swings
    C. Are terminal wins
    D. Have no legal moves

45. **The horizon effect occurs when:**
    A. A bad outcome is delayed beyond the search depth and therefore missed
    B. The game tree has no depth limit
    C. The utility function is exact
    D. The opponent has no moves

46. **Forward pruning differs from alpha-beta pruning because forward pruning:**
    A. Prunes only branches proven irrelevant
    B. Prunes moves that merely appear poor, risking mistakes
    C. Always gives the exact minimax value
    D. Searches every possible move

47. **Beam search in game playing is an example of:**
    A. Forward pruning
    B. Terminal testing
    C. Utility assignment
    D. Complete minimax

48. **Monte Carlo Tree Search estimates move quality mainly by:**
    A. Averaging results of many simulations or playouts
    B. Searching every possible terminal state exactly
    C. Ignoring outcomes
    D. Using no tree at all

49. **The four core phases of Monte Carlo Tree Search are:**
    A. Sort, prune, delete, restart
    B. Selection, expansion, simulation, backpropagation
    C. Ask, tell, infer, act
    D. Encode, decode, compile, halt

50. **Stochastic and partially observable games make search harder because they introduce:**
    A. Chance outcomes and hidden information
    B. No legal moves
    C. No opponents
    D. Only deterministic fully visible states

---

## Answer Key

1. B
2. B
3. C
4. A
5. B
6. B
7. B
8. C
9. A
10. B
11. A
12. B
13. B
14. B
15. B
16. A
17. B
18. B
19. A
20. A
21. A
22. B
23. C
24. B
25. B
26. C
27. B
28. B
29. A
30. A
31. A
32. A
33. B
34. A
35. A
36. B
37. A
38. B
39. A
40. A
41. B
42. A
43. D
44. B
45. A
46. B
47. A
48. A
49. B
50. A
