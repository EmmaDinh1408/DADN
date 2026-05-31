"""
MechDrive AI — Gear Q-Learning Agent
======================================
Agent Q-Learning cho tối ưu hóa bộ truyền bánh răng.
Quản lý Q-Table, ε-greedy policy, Bellman update.
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
    GEAR_TYPES, UD_VALUES, PSI_BA_VALUES, ZG1_VALUES, MAT_IDS,
    discretize, state_to_key, gear_action_to_key, gear_key_to_action,
    OUTPUT_DIR,
)
from environment.gear_env import GearEnvironment


class GearAgent:
    """Q-Learning agent for gear transmission optimization."""

    def __init__(self, alpha: float = ALPHA, gamma: float = GAMMA,
                 epsilon: float = EPSILON_START):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.env = GearEnvironment()

        # Q-Table: dict[state_key][action_key] = float
        self.q_table: dict[str, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

        # Tất cả action keys (pre-computed)
        self.all_actions = []
        self.all_action_tuples = []
        for gt in GEAR_TYPES:
            for ud in UD_VALUES:
                for psi in PSI_BA_VALUES:
                    for z in ZG1_VALUES:
                        for mat in MAT_IDS:
                            key = gear_action_to_key(gt, ud, psi, z, mat)
                            self.all_actions.append(key)
                            self.all_action_tuples.append((gt, ud, psi, z, mat))

        # Stats
        self.total_reward = 0
        self.episode_rewards = []
        self.pass_count = 0
        self.fail_count = 0

    def _random_state(self) -> tuple:
        """Generate a random state."""
        P = random.choice(P_BUCKETS)
        n = random.choice(N_BUCKETS)
        load = random.choice(LOAD_TYPES)
        return (P, n, load)

    def _get_action(self, state_key: str) -> tuple[int, str, tuple]:
        """
        ε-greedy action selection.
        Returns (action_index, action_key, action_tuple).
        """
        if random.random() < self.epsilon:
            # Exploration: random action
            idx = random.randint(0, len(self.all_actions) - 1)
        else:
            # Exploitation: best action from Q-Table
            q_row = self.q_table[state_key]
            if not q_row:
                idx = random.randint(0, len(self.all_actions) - 1)
            else:
                best_key = max(q_row, key=q_row.get)
                idx = self.all_actions.index(best_key) if best_key in self.all_actions else 0

        return idx, self.all_actions[idx], self.all_action_tuples[idx]

    def train_step(self) -> float:
        """
        Execute one training step.
        Returns reward.
        """
        # 1. Random state
        state = self._random_state()
        state_key = state_to_key(*state)

        # 2. ε-greedy action
        _, action_key, action_tuple = self._get_action(state_key)

        # 3. Environment step
        reward, info = self.env.step(state, action_tuple)

        # 4. Bellman update (contextual bandit: no next state)
        old_q = self.q_table[state_key][action_key]
        new_q = (1 - self.alpha) * old_q + self.alpha * reward
        self.q_table[state_key][action_key] = new_q

        # 5. Decay epsilon
        self.epsilon = max(EPSILON_END, self.epsilon * EPSILON_DECAY)

        # Stats
        self.total_reward += reward
        if info.get("pass", False):
            self.pass_count += 1
        else:
            self.fail_count += 1

        return reward

    def get_best_action(self, P: float, n: float, load: int) -> dict:
        """Get the best action for a given state (after training)."""
        state_key = state_to_key(P, n, load)
        q_row = self.q_table[state_key]
        if not q_row:
            return {"error": "No data for this state"}
        best_key = max(q_row, key=q_row.get)
        result = gear_key_to_action(best_key)
        result["q_value"] = q_row[best_key]
        return result

    def export_best_actions(self, filepath: str = None) -> dict:
        """Export the best action for every state."""
        if filepath is None:
            filepath = str(OUTPUT_DIR / "gear_qtable.json")

        best_actions = {}
        for P in P_BUCKETS:
            for n in N_BUCKETS:
                for load in LOAD_TYPES:
                    key = state_to_key(P, n, load)
                    q_row = self.q_table[key]
                    if q_row:
                        best_key = max(q_row, key=q_row.get)
                        action = gear_key_to_action(best_key)
                        action["q_value"] = round(q_row[best_key], 2)
                        best_actions[key] = action
                    else:
                        best_actions[key] = {"error": "untrained"}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(best_actions, f, indent=2, ensure_ascii=False)

        print(f"[GearAgent] Exported {len(best_actions)} states → {filepath}")
        return best_actions

    def get_stats(self) -> dict:
        """Get training statistics."""
        total = self.pass_count + self.fail_count
        return {
            "total_episodes": total,
            "pass_rate": self.pass_count / total if total > 0 else 0,
            "fail_rate": self.fail_count / total if total > 0 else 0,
            "avg_reward": self.total_reward / total if total > 0 else 0,
            "epsilon": self.epsilon,
            "q_table_states": len(self.q_table),
        }
