"""
MechDrive AI — Chain Q-Learning Agent
=======================================
Agent Q-Learning cho tối ưu hóa bộ truyền xích.
"""

import sys
import os
import random
import json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ALPHA, GAMMA, EPSILON_START, EPSILON_END, EPSILON_DECAY,
    P_BUCKETS, N_BUCKETS, LOAD_TYPES,
    UX_VALUES, Z1_CHAIN_VALUES,
    discretize, state_to_key, chain_action_to_key, chain_key_to_action,
    OUTPUT_DIR,
)
from environment.chain_env import ChainEnvironment


class ChainAgent:
    """Q-Learning agent for chain transmission optimization."""

    def __init__(self, alpha: float = ALPHA, gamma: float = GAMMA,
                 epsilon: float = EPSILON_START):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.env = ChainEnvironment()

        # Q-Table
        self.q_table: dict[str, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

        # All action keys
        self.all_actions = []
        self.all_action_tuples = []
        for ux in UX_VALUES:
            for z1 in Z1_CHAIN_VALUES:
                key = chain_action_to_key(ux, z1)
                self.all_actions.append(key)
                self.all_action_tuples.append((ux, z1))

        # Stats
        self.total_reward = 0
        self.pass_count = 0
        self.fail_count = 0

    def _random_state(self) -> tuple:
        P = random.choice(P_BUCKETS)
        n = random.choice(N_BUCKETS)
        load = random.choice(LOAD_TYPES)
        return (P, n, load)

    def _get_action(self, state_key: str) -> tuple[int, str, tuple]:
        if random.random() < self.epsilon:
            idx = random.randint(0, len(self.all_actions) - 1)
        else:
            q_row = self.q_table[state_key]
            if not q_row:
                idx = random.randint(0, len(self.all_actions) - 1)
            else:
                best_key = max(q_row, key=q_row.get)
                idx = self.all_actions.index(best_key) if best_key in self.all_actions else 0
        return idx, self.all_actions[idx], self.all_action_tuples[idx]

    def train_step(self) -> float:
        state = self._random_state()
        state_key = state_to_key(*state)

        _, action_key, action_tuple = self._get_action(state_key)

        reward, info = self.env.step(state, action_tuple)

        old_q = self.q_table[state_key][action_key]
        new_q = (1 - self.alpha) * old_q + self.alpha * reward
        self.q_table[state_key][action_key] = new_q

        self.epsilon = max(EPSILON_END, self.epsilon * EPSILON_DECAY)

        self.total_reward += reward
        if info.get("pass", False):
            self.pass_count += 1
        else:
            self.fail_count += 1

        return reward

    def get_best_action(self, P: float, n: float, load: int) -> dict:
        state_key = state_to_key(P, n, load)
        q_row = self.q_table[state_key]
        if not q_row:
            return {"error": "No data for this state"}
        best_key = max(q_row, key=q_row.get)
        result = chain_key_to_action(best_key)
        result["q_value"] = q_row[best_key]
        return result

    def export_best_actions(self, filepath: str = None) -> dict:
        if filepath is None:
            filepath = str(OUTPUT_DIR / "chain_qtable.json")

        best_actions = {}
        for P in P_BUCKETS:
            for n in N_BUCKETS:
                for load in LOAD_TYPES:
                    key = state_to_key(P, n, load)
                    q_row = self.q_table[key]
                    if q_row:
                        best_key = max(q_row, key=q_row.get)
                        action = chain_key_to_action(best_key)
                        action["q_value"] = round(q_row[best_key], 2)
                        best_actions[key] = action
                    else:
                        best_actions[key] = {"error": "untrained"}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(best_actions, f, indent=2, ensure_ascii=False)

        print(f"[ChainAgent] Exported {len(best_actions)} states → {filepath}")
        return best_actions

    def get_stats(self) -> dict:
        total = self.pass_count + self.fail_count
        return {
            "total_episodes": total,
            "pass_rate": self.pass_count / total if total > 0 else 0,
            "fail_rate": self.fail_count / total if total > 0 else 0,
            "avg_reward": self.total_reward / total if total > 0 else 0,
            "epsilon": self.epsilon,
            "q_table_states": len(self.q_table),
        }
