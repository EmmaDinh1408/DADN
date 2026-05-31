"""
MechDrive AI — Unified Q-Learning Agent
==========================================
1 Agent duy nhất cho cả gear + chain.
5 biến State (3024 states) × 5 biến Action (2000 actions).

Bellman (Phần IV Spec):
Q(S,A) ← Q(S,A) + α × [R_total - Q(S,A)]
"""

import sys
import os
import random
import json
import math
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ALPHA, GAMMA, EPSILON_START, EPSILON_END, EPSILON_LINEAR_DECAY,
    EPOCHS,
    P_YC_BINS, N_YC_BINS, U_TOTAL_BINS, LH_BINS, LOAD_TYPES,
    UD_VALUES, PSI_BA_VALUES, MAT_IDS, GEAR_TYPES, Z1_CHAIN_VALUES,
    TOTAL_STATES, TOTAL_ACTIONS,
    state_to_key, action_to_key, key_to_action, key_to_state,
    OUTPUT_DIR,
)
from environment.mech_env import MechEnvironment


class QLAgent:
    """
    Unified Q-Learning Agent.
    
    State = (P_yc, n_yc, u_total, L_h, load_type)
    Action = (u_d, psi_ba, matID, gear_type, z1_chain)
    """

    def __init__(self, alpha: float = ALPHA, gamma: float = GAMMA,
                 epsilon: float = EPSILON_START):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.env = MechEnvironment()

        # Q-Table: dict[state_key][action_key] = float
        self.q_table: dict[str, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

        # Pre-compute all action tuples and keys
        self.all_action_keys: list[str] = []
        self.all_action_tuples: list[tuple] = []
        for ud in UD_VALUES:
            for psi in PSI_BA_VALUES:
                for mat in MAT_IDS:
                    for gt in GEAR_TYPES:
                        for z1c in Z1_CHAIN_VALUES:
                            key = action_to_key(ud, psi, mat, gt, z1c)
                            self.all_action_keys.append(key)
                            self.all_action_tuples.append(
                                (ud, psi, mat, gt, z1c)
                            )

        # Pre-compute all state tuples
        self.all_state_keys: list[str] = []
        self.all_state_tuples: list[tuple] = []
        for P in P_YC_BINS:
            for n in N_YC_BINS:
                for u in U_TOTAL_BINS:
                    for Lh in LH_BINS:
                        for load in LOAD_TYPES:
                            key = state_to_key(P, n, u, Lh, load)
                            self.all_state_keys.append(key)
                            self.all_state_tuples.append(
                                (P, n, u, Lh, load)
                            )

        assert len(self.all_action_keys) == TOTAL_ACTIONS, \
            f"Actions: {len(self.all_action_keys)} != {TOTAL_ACTIONS}"
        assert len(self.all_state_keys) == TOTAL_STATES, \
            f"States: {len(self.all_state_keys)} != {TOTAL_STATES}"

        # ── Tracking Metrics ──
        self.episode_count = 0
        self.gate_counts = {0: 0, 1: 0, 2: 0, 3: 0}  # mỗi cửa ải
        self.total_reward = 0.0
        self.reward_history: list[float] = []  # raw reward mỗi episode
        self._policy_snapshot: dict[str, str] = {}  # last greedy policy

    def _random_state(self) -> tuple[tuple, str]:
        """Random state tuple + key."""
        idx = random.randint(0, TOTAL_STATES - 1)
        return self.all_state_tuples[idx], self.all_state_keys[idx]

    def _get_action_epsilon_greedy(self, state_key: str) -> tuple[int, str, tuple]:
        """ε-greedy action selection."""
        if random.random() < self.epsilon:
            idx = random.randint(0, TOTAL_ACTIONS - 1)
        else:
            q_row = self.q_table[state_key]
            if not q_row:
                idx = random.randint(0, TOTAL_ACTIONS - 1)
            else:
                best_key = max(q_row, key=q_row.get)
                try:
                    idx = self.all_action_keys.index(best_key)
                except ValueError:
                    idx = random.randint(0, TOTAL_ACTIONS - 1)

        return idx, self.all_action_keys[idx], self.all_action_tuples[idx]

    def train_step(self) -> tuple[float, dict]:
        """
        1 vòng lặp Bellman update.
        
        Returns:
            (reward, info_dict)
        """
        # 1. Random state
        state_tuple, state_key = self._random_state()

        # 2. ε-greedy action
        _, action_key, action_tuple = self._get_action_epsilon_greedy(state_key)

        # 3. Environment step
        reward, info = self.env.step(state_tuple, action_tuple)

        # 4. Bellman update: Q(S,A) ← Q(S,A) + α × [R - Q(S,A)]
        old_q = self.q_table[state_key][action_key]
        new_q = old_q + self.alpha * (reward - old_q)
        self.q_table[state_key][action_key] = new_q

        # 5. Tracking
        self.episode_count += 1
        self.total_reward += reward
        self.reward_history.append(reward)

        gate = info.get("gate", 0)
        self.gate_counts[gate] = self.gate_counts.get(gate, 0) + 1

        return reward, info

    def decay_epsilon_linear(self, epoch: int, total_epochs: int):
        """ε giảm tuyến tính: 1.0 → 0.01."""
        self.epsilon = max(
            EPSILON_END,
            EPSILON_START - (EPSILON_START - EPSILON_END) * epoch / total_epochs
        )

    # ══════════════════════════════════════════════════════════════════
    # EVALUATION METRICS (Đánh giá mô hình Q-Learning)
    # ══════════════════════════════════════════════════════════════════

    def evaluate_policy(self) -> dict:
        """
        Đánh giá greedy policy (ε=0) trên TOÀN BỘ state space.
        
        Metrics trả về:
        1. avg_reward_greedy: Reward trung bình khi chỉ exploit
        2. pass_rate: % states qua cửa 3 (an toàn)
        3. gate_distribution: % mỗi cửa ải
        4. avg_S_H: Trung bình S_H (utilization ratio) — gần 0.95 = tối ưu
        5. avg_volume: Thể tích trung bình (nhỏ = tốt)
        6. sweet_spot_rate: % states có 0.90 ≤ S_H ≤ 0.98
        7. policy_stability: % states mà best action KHÔNG đổi so với lần eval trước
        8. coverage: % states có ít nhất 1 action trong Q-Table
        """
        total_reward = 0
        gate_dist = {1: 0, 2: 0, 3: 0}
        S_H_values = []
        volumes = []
        sweet_count = 0
        new_policy = {}
        states_with_q = 0

        for state_tuple, state_key in zip(self.all_state_tuples, self.all_state_keys):
            q_row = self.q_table[state_key]
            if not q_row:
                gate_dist[2] = gate_dist.get(2, 0) + 1  # chưa train → coi như fail
                continue

            states_with_q += 1
            best_action_key = max(q_row, key=q_row.get)
            new_policy[state_key] = best_action_key

            # Chạy environment với best action
            action = key_to_action(best_action_key)
            action_tuple = (
                action["optimal_ud"], action["optimal_psi_ba"],
                action["matID"], action["gear_type"], action["z1_chain"],
            )
            reward, info = self.env.step(state_tuple, action_tuple)
            total_reward += reward

            gate = info.get("gate", 0)
            gate_dist[gate] = gate_dist.get(gate, 0) + 1

            if gate == 3:
                S_H = info.get("S_H", 0)
                S_H_values.append(S_H)
                volumes.append(info.get("volume", 0))
                if 0.90 <= S_H <= 0.98:
                    sweet_count += 1

        # Policy stability
        if self._policy_snapshot:
            unchanged = sum(
                1 for k in new_policy
                if self._policy_snapshot.get(k) == new_policy[k]
            )
            stability = unchanged / len(new_policy) if new_policy else 0
        else:
            stability = 0.0

        self._policy_snapshot = new_policy.copy()

        n_evaluated = states_with_q or 1
        gate3_count = gate_dist.get(3, 0)

        return {
            "avg_reward_greedy": total_reward / n_evaluated,
            "pass_rate": gate3_count / TOTAL_STATES,
            "gate_distribution": {
                f"gate_{k}": v / TOTAL_STATES
                for k, v in sorted(gate_dist.items())
            },
            "avg_S_H": sum(S_H_values) / len(S_H_values) if S_H_values else 0,
            "avg_volume": sum(volumes) / len(volumes) if volumes else 0,
            "sweet_spot_rate": sweet_count / gate3_count if gate3_count > 0 else 0,
            "policy_stability": stability,
            "coverage": states_with_q / TOTAL_STATES,
        }

    def get_q_value_stats(self) -> dict:
        """Thống kê Q-values: mean, max, std — cho biết mức hội tụ."""
        all_q = []
        max_q_per_state = []
        for state_key in self.all_state_keys:
            q_row = self.q_table[state_key]
            if q_row:
                vals = list(q_row.values())
                all_q.extend(vals)
                max_q_per_state.append(max(vals))

        if not all_q:
            return {"mean_q": 0, "max_q": 0, "std_q": 0, "mean_max_q": 0}

        mean_q = sum(all_q) / len(all_q)
        max_q = max(all_q)
        variance = sum((x - mean_q) ** 2 for x in all_q) / len(all_q)
        std_q = math.sqrt(variance)
        mean_max_q = sum(max_q_per_state) / len(max_q_per_state) if max_q_per_state else 0

        return {
            "mean_q": round(mean_q, 2),
            "max_q": round(max_q, 2),
            "std_q": round(std_q, 2),
            "mean_max_q": round(mean_max_q, 2),
            "total_entries": len(all_q),
        }

    def get_best_action(self, P: float, n: float, u_total: float,
                        L_h: float, load: int) -> dict:
        """Tra Q-Table → best action (production deployment)."""
        state_key = state_to_key(P, n, u_total, L_h, load)
        q_row = self.q_table[state_key]
        if not q_row:
            return {"error": "No data for this state"}
        best_key = max(q_row, key=q_row.get)
        result = key_to_action(best_key)
        result["q_value"] = q_row[best_key]
        return result

    def export_qtable(self, filepath: str = None) -> dict:
        """Export best action cho mọi state → JSON."""
        if filepath is None:
            filepath = str(OUTPUT_DIR / "q_table.json")

        export = {}
        for state_tuple, state_key in zip(self.all_state_tuples, self.all_state_keys):
            q_row = self.q_table[state_key]
            if q_row:
                best_key = max(q_row, key=q_row.get)
                action = key_to_action(best_key)
                action["q_value"] = round(q_row[best_key], 2)
                export[state_key] = {
                    "state": {
                        "P_yc": state_tuple[0],
                        "n_yc": state_tuple[1],
                        "u_total": state_tuple[2],
                        "L_h": state_tuple[3],
                        "load_type": state_tuple[4],
                    },
                    "action": action,
                }
            else:
                export[state_key] = {"error": "untrained"}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)

        trained = sum(1 for v in export.values() if "error" not in v)
        try:
            print(f"  [Export] {trained}/{TOTAL_STATES} states -> {filepath}")
        except UnicodeEncodeError:
            print(f"  [Export] {trained}/{TOTAL_STATES} states -> (filepath contains unicode)")
        return export
