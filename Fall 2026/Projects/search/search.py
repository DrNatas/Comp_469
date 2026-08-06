# search.py
# ---------


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    # ==========================================================================
    # BEGIN SOLUTION -- Q1 (3 pts): Finding a Fixed Food Dot using DFS
    # https://inst.eecs.berkeley.edu/~cs188/sp26/projects/proj1/#q1-3-pts-finding-a-fixed-food-dot-using-depth-first-search
    #
    # LIFO fringe (util.Stack). This is one instance of the same graph-search
    # template used by all four algorithms in this file (BFS/UCS/A* below):
    # pop -> goal-test the *popped* state -> skip if already visited -> mark
    # visited -> push unvisited successors. Marking `visited` at pop time
    # (not at push time) is what prevents infinite loops on mazes with
    # cycles (e.g. openMaze) while still matching the reference algorithm's
    # exact node-expansion trace (see the BFS note below for why that trace
    # matters, not just the final path).
    # ==========================================================================
    fringe = util.Stack()
    fringe.push((problem.getStartState(), []))
    visited = set()

    while not fringe.isEmpty():
        state, actions = fringe.pop()

        if problem.isGoalState(state):
            return actions

        if state in visited:
            continue
        visited.add(state)

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in visited:
                fringe.push((successor, actions + [action]))

    return []
    # END SOLUTION -- Q1

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    # ==========================================================================
    # BEGIN SOLUTION -- Q2 (3 pts): Breadth First Search
    # https://inst.eecs.berkeley.edu/~cs188/sp26/projects/proj1/#q2-3-pts-breadth-first-search
    #
    # Same template as DFS, just with a FIFO fringe (util.Queue).
    #
    # GOTCHA (worth knowing before debugging a student's BFS): the tempting
    # "optimization" here is to goal-test a successor and mark it visited at
    # *generation* time, before pushing it, so the fringe never holds
    # duplicates:
    #
    #   if successor not in visited:
    #       if problem.isGoalState(successor):
    #           return actions + [action]
    #       visited.add(successor)
    #       fringe.push((successor, actions + [action]))
    #
    # That's still a *correct* BFS -- it returns a shortest path -- but it
    # expands a different set/order of nodes than this project's reference
    # solution, which goal-tests and marks visited on *pop*, like every
    # other algorithm here. Berkeley's synthetic graph tests
    # (graph_manypaths.test, graph_backtrack.test, ...) assert the exact
    # `expanded_states` trace, not just path optimality, so the early-exit
    # version passes on path cost but fails those specific unit tests. Keep
    # the same pop-time-goal-test shape as DFS/UCS/A* here for that reason.
    # ==========================================================================
    fringe = util.Queue()
    fringe.push((problem.getStartState(), []))
    visited = set()

    while not fringe.isEmpty():
        state, actions = fringe.pop()

        if problem.isGoalState(state):
            return actions

        if state in visited:
            continue
        visited.add(state)

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in visited:
                fringe.push((successor, actions + [action]))

    return []
    # END SOLUTION -- Q2

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    # ==========================================================================
    # BEGIN SOLUTION -- Q3 (3 pts): Varying the Cost Function
    # https://inst.eecs.berkeley.edu/~cs188/sp26/projects/proj1/#q3-3-pts-varying-the-cost-function
    #
    # Same template again, now with a PriorityQueue keyed on *cumulative*
    # path cost (not the incremental stepCost of the last edge alone).
    # `bestCost` tracks the cheapest known cost to reach each state so far:
    #   - on pop, if we've already finished that state more cheaply, skip it
    #     (it's a stale duplicate left over from a costlier earlier push).
    #   - on generating a successor, only push if this path beats the best
    #     known cost to that successor (or it's unseen).
    # Goal-testing happens on pop, not on generation -- a node can be
    # enqueued more than once at different costs, and only the *cheapest*
    # dequeue is guaranteed optimal (this is exactly what
    # ucs_5_goalAtDequeue.test checks for).
    # ==========================================================================
    startState = problem.getStartState()
    fringe = util.PriorityQueue()
    fringe.push((startState, [], 0), 0)
    bestCost = {}

    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()

        if state in bestCost and bestCost[state] <= cost:
            continue
        bestCost[state] = cost

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if successor not in bestCost or newCost < bestCost[successor]:
                fringe.push((successor, actions + [action], newCost), newCost)

    return []
    # END SOLUTION -- Q3

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    # ==========================================================================
    # BEGIN SOLUTION -- Q4 (3 pts): A* search
    # https://inst.eecs.berkeley.edu/~cs188/sp26/projects/proj1/#q4-3-pts-a-search
    #
    # Identical to UCS, except the fringe priority is g(successor) +
    # h(successor) instead of just g(successor). `bestCost` still stores
    # the true cumulative cost g (never the heuristic-inflated priority) --
    # that distinction matters because g is what the final path cost has to
    # be correct, and because an inconsistent-but-admissible heuristic can
    # make A* revisit a state at a lower g after already popping it once;
    # the bestCost re-expansion guard is what keeps that case correct
    # instead of merely "usually fine."
    # astar_3_goalAtDequeue.test targets the same pop-time-goal-test
    # requirement as UCS's ucs_5_goalAtDequeue.test.
    # ==========================================================================
    startState = problem.getStartState()
    fringe = util.PriorityQueue()
    fringe.push((startState, [], 0), heuristic(startState, problem))
    bestCost = {}

    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()

        if state in bestCost and bestCost[state] <= cost:
            continue
        bestCost[state] = cost

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if successor not in bestCost or newCost < bestCost[successor]:
                priority = newCost + heuristic(successor, problem)
                fringe.push((successor, actions + [action], newCost), priority)

    return []
    # END SOLUTION -- Q4


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
