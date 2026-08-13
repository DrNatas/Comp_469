from __future__ import annotations

import importlib.util
import inspect
import sys
import types
import unittest
from pathlib import Path


def load_module():
    if "pygame" not in sys.modules:
        pygame = types.ModuleType("pygame")
        pygame.time = types.SimpleNamespace(get_ticks=lambda: 0)
        sys.modules["pygame"] = pygame
    path = Path(__file__).resolve().parents[1] / "src" / "autonomous_pacman_agent.py"
    spec = importlib.util.spec_from_file_location("agent_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_under_test"] = module
    spec.loader.exec_module(module)
    return module


class FakeGame:
    def __init__(self, module):
        self.module = module
        self.cols = 5
        self.grid = [
            list("#####"),
            list("#   #"),
            list("#   #"),
            list("#   #"),
            list("#####"),
        ]

    def wrap_col(self, col: int) -> int:
        return col % self.cols

    def is_wall(self, row: int, col: int) -> bool:
        if row < 0 or row >= len(self.grid):
            return True
        return self.grid[row][col] == "#"

    def is_ghost_door(self, row: int, col: int) -> bool:
        return False


class Chapter2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_module()

    def test_percept_contains_required_dynamic_sensor_fields(self):
        fields = set(self.m.Percept.__dataclass_fields__)
        required = {
            "player",
            "current_direction",
            "pellets",
            "power_pellets",
            "released_ghosts",
            "legal_actions",
            "frightened_time_remaining",
        }
        self.assertTrue(required.issubset(fields), required - fields)

    def make_percept(self, **overrides):
        values = dict(
            player=(2, 2),
            current_direction=self.m.DIRECTIONS["RIGHT"],
            pellets=frozenset({(2, 3)}),
            power_pellets=frozenset(),
            released_ghosts=tuple(),
            legal_actions=(self.m.DIRECTIONS["LEFT"], self.m.DIRECTIONS["RIGHT"]),
            frightened_time_remaining=0.0,
        )
        values.update(overrides)
        return self.m.Percept(**values)

    def test_empty_legal_action_is_handled(self):
        agent = self.m.PacManAgent(FakeGame(self.m))
        percept = self.make_percept(legal_actions=tuple())
        self.assertEqual(agent.choose_action(percept), (0, 0))
        self.assertIn("No legal", agent.last_reason)

    def test_choose_action_returns_a_legal_action(self):
        agent = self.m.PacManAgent(FakeGame(self.m))
        percept = self.make_percept()
        action = agent.choose_action(percept)
        self.assertIn(action, percept.legal_actions)

    def test_internal_state_changes_and_affects_utility(self):
        agent = self.m.PacManAgent(FakeGame(self.m))
        percept = self.make_percept()
        agent.update_internal_state(percept)
        right = self.m.DIRECTIONS["RIGHT"]
        utility_before, details_before = agent.evaluate_action(percept, right)
        agent.visit_counts[(2, 3)] = 5
        utility_after, details_after = agent.evaluate_action(percept, right)
        self.assertLess(utility_after, utility_before)
        self.assertLess(details_after["revisit"], details_before["revisit"])

    def test_dynamic_data_is_not_read_through_choose_action_back_channel(self):
        source = inspect.getsource(self.m.PacManAgent.choose_action)
        forbidden = (
            "self.game.ghosts",
            "self.game.ghosts_are_frightened",
            "self.game.player.direction",
        )
        for text in forbidden:
            self.assertNotIn(text, source)

    def test_last_reason_contains_required_evidence(self):
        agent = self.m.PacManAgent(FakeGame(self.m))
        agent.choose_action(self.make_percept())
        for token in ("U=", "food=", "ghost=", "memory="):
            self.assertIn(token, agent.last_reason)


if __name__ == "__main__":
    unittest.main()
