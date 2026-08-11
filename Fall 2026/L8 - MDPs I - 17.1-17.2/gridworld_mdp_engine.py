"""Gridworld MDP engine used to generate lecture figures with correct numbers."""
import numpy as np

ACTIONS = ['U', 'D', 'L', 'R']
DELTA = {'U': (0, 1), 'D': (0, -1), 'L': (-1, 0), 'R': (1, 0)}
PERP = {'U': ['L', 'R'], 'D': ['L', 'R'], 'L': ['D', 'U'], 'R': ['D', 'U']}


class Grid43:
    """AIMA 4x3 world. Rewards on transition. Terminals absorb.

    mode='aima'  : reward r on every non-terminal transition, terminals +1/-1
                   received on entering; terminal is absorbing with 0 after.
    mode='cs188' : living reward r, terminal squares have a single EXIT action
                   yielding +1/-1 then going to a sink.
    """

    def __init__(self, r=-0.04, gamma=1.0, noise=0.2, mode='aima',
                 reward_at_state=False):
        # reward_at_state=True reproduces the R(s) convention used to draw
        # AIMA Figure 17.3: U(s) = R(s) + gamma * max_a sum_s' P(s'|s,a) U(s').
        # It shifts every non-terminal utility by exactly r relative to the
        # R(s,a,s') convention stated in the 4th-edition text.
        self.r = r
        self.gamma = gamma
        self.noise = noise
        self.mode = mode
        self.reward_at_state = reward_at_state
        self.wall = {(2, 2)}
        self.terminals = {(4, 3): 1.0, (4, 2): -1.0}
        self.states = [(x, y) for x in range(1, 5) for y in range(1, 4)
                       if (x, y) not in self.wall]

    def legal(self, s):
        return s in self.states

    def move(self, s, a):
        dx, dy = DELTA[a]
        ns = (s[0] + dx, s[1] + dy)
        return ns if self.legal(ns) else s

    def actions(self, s):
        if s in self.terminals:
            return ['EXIT'] if self.mode == 'cs188' else []
        return ACTIONS

    def transitions(self, s, a):
        """Return list of (prob, s', reward)."""
        if s in self.terminals:
            if self.mode == 'cs188':
                return [(1.0, 'SINK', self.terminals[s])]
            return []
        p_main = 1.0 - self.noise
        p_side = self.noise / 2.0
        out = {}
        for prob, act in [(p_main, a), (p_side, PERP[a][0]), (p_side, PERP[a][1])]:
            ns = self.move(s, act)
            out[ns] = out.get(ns, 0.0) + prob
        res = []
        for ns, p in out.items():
            if self.mode == 'aima':
                rew = self.terminals.get(ns, self.r)
            else:
                rew = self.r
            res.append((p, ns, rew))
        return res

    def q(self, s, a, V):
        if self.reward_at_state:
            tot = 0.0
            for p, ns, _rew in self.transitions(s, a):
                v_next = self.terminals.get(ns, V.get(ns, 0.0))
                tot += p * v_next
            return self.r + self.gamma * tot
        tot = 0.0
        for p, ns, rew in self.transitions(s, a):
            v_next = 0.0 if ns == 'SINK' else V.get(ns, 0.0)
            if self.mode == 'aima' and ns in self.terminals:
                v_next = 0.0  # terminal absorbs, no further reward
            tot += p * (rew + self.gamma * v_next)
        return tot

    def value_iteration(self, iters=None, eps=1e-10, record=False):
        V = {s: 0.0 for s in self.states}
        hist = [dict(V)]
        k = 0
        while True:
            k += 1
            Vn = {}
            for s in self.states:
                acts = self.actions(s)
                if not acts:
                    Vn[s] = 0.0
                else:
                    Vn[s] = max(self.q(s, a, V) for a in acts)
            delta = max(abs(Vn[s] - V[s]) for s in self.states)
            V = Vn
            if record:
                hist.append(dict(V))
            if iters is not None:
                if k >= iters:
                    break
            elif delta < eps:
                break
        return (V, hist) if record else V

    def policy(self, V):
        pi = {}
        for s in self.states:
            acts = self.actions(s)
            if not acts or acts == ['EXIT']:
                pi[s] = 'EXIT' if acts else None
                continue
            pi[s] = max(acts, key=lambda a: self.q(s, a, V))
        return pi

    def qvalues(self, V):
        Q = {}
        for s in self.states:
            for a in self.actions(s):
                Q[(s, a)] = self.q(s, a, V)
        return Q

    def policy_evaluation(self, pi, iters=None, eps=1e-12):
        V = {s: 0.0 for s in self.states}
        k = 0
        while True:
            k += 1
            Vn = {}
            for s in self.states:
                a = pi.get(s)
                Vn[s] = 0.0 if a is None else self.q(s, a, V)
            delta = max(abs(Vn[s] - V[s]) for s in self.states)
            V = Vn
            if iters is not None and k >= iters:
                break
            if iters is None and delta < eps:
                break
        return V

    def policy_iteration(self, record=False):
        pi = {s: ('EXIT' if self.actions(s) == ['EXIT'] else
                  (ACTIONS[0] if self.actions(s) else None)) for s in self.states}
        rounds = []
        for i in range(200):
            V = self.policy_evaluation(pi)
            newpi = self.policy(V)
            rounds.append((dict(pi), dict(V)))
            if all(newpi[s] == pi[s] for s in self.states):
                break
            pi = newpi
        return (pi, V, rounds) if record else (pi, V)


if __name__ == '__main__':
    print('=== AIMA 4x3, r=-0.04, gamma=1 (Figure 17.3) ===')
    g = Grid43(r=-0.04, gamma=1.0, noise=0.2, mode='aima')
    V = g.value_iteration()
    for y in [3, 2, 1]:
        row = []
        for x in range(1, 5):
            if (x, y) in g.wall:
                row.append('  WALL ')
            elif (x, y) in g.terminals:
                row.append('%+7.3f' % g.terminals[(x, y)])
            else:
                row.append('%7.3f' % V[(x, y)])
        print(' '.join(row))

    print('\n=== CS188 gridworld, living=0, gamma=0.9, noise=0.2 ===')
    c = Grid43(r=0.0, gamma=0.9, noise=0.2, mode='cs188')
    Vc = c.value_iteration()
    for y in [3, 2, 1]:
        row = []
        for x in range(1, 5):
            if (x, y) in c.wall:
                row.append('  WALL')
            else:
                row.append('%6.2f' % Vc[(x, y)])
        print(' '.join(row))
    print('policy:', {k: v for k, v in c.policy(Vc).items()})

    print('\n=== r ranges: optimal policies ===')
    for rr in [-2.0, -0.6, -0.1, 0.05]:
        gg = Grid43(r=rr, gamma=1.0 if rr < 0 else 0.99, noise=0.2, mode='aima')
        Vr = gg.value_iteration(iters=2000)
        print(rr, gg.policy(Vr))
