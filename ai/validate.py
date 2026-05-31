"""
MechDrive AI — Validate Q-Table
===================================
Kiem tra Q-Table da train: tat ca best action phai qua 3 cua ai.
Danh gia chat luong toi uu hoa, khong chi pass/fail.

Usage:
    python validate.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    P_YC_BINS, N_YC_BINS, U_TOTAL_BINS, LH_BINS, LOAD_TYPES,
    TOTAL_STATES, OUTPUT_DIR, state_to_key, key_to_action,
)
from environment.mech_env import MechEnvironment


def validate():
    filepath = str(OUTPUT_DIR / "q_table.json")
    if not os.path.exists(filepath):
        print("[ERROR] q_table.json not found. Run train.py first.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        qtable = json.load(f)

    env = MechEnvironment()

    total = 0
    gate_counts = {1: 0, 2: 0, 3: 0}
    untrained = 0
    S_H_values = []
    S_F_values = []
    volumes = []
    rewards = []
    sweet_count = 0
    over_count = 0

    for P in P_YC_BINS:
        for n in N_YC_BINS:
            for u in U_TOTAL_BINS:
                for Lh in LH_BINS:
                    for load in LOAD_TYPES:
                        key = state_to_key(P, n, u, Lh, load)
                        entry = qtable.get(key)
                        if entry is None or "error" in entry:
                            untrained += 1
                            continue

                        total += 1
                        action = entry["action"]
                        action_tuple = (
                            action["optimal_ud"],
                            action["optimal_psi_ba"],
                            action["matID"],
                            action["gear_type"],
                            action["z1_chain"],
                        )
                        state_tuple = (P, n, u, Lh, load)
                        reward, info = env.step(state_tuple, action_tuple)
                        rewards.append(reward)

                        gate = info.get("gate", 0)
                        gate_counts[gate] = gate_counts.get(gate, 0) + 1

                        if gate == 3:
                            S_H = info.get("S_H", 0)
                            S_F = info.get("S_F", 0)
                            S_H_values.append(S_H)
                            S_F_values.append(S_F)
                            volumes.append(info.get("volume", 0))
                            if 0.90 <= S_H <= 0.98:
                                sweet_count += 1
                            if S_H < 0.80:
                                over_count += 1

    # ── Report ──
    gate3 = gate_counts.get(3, 0)
    print()
    print("=" * 70)
    print("  Q-TABLE VALIDATION REPORT")
    print("=" * 70)
    print(f"  Total states tested:     {total}")
    print(f"  Untrained states:        {untrained}")
    print()
    print("  --- GATE BREAKDOWN ---")
    print(f"  Gate 1 (Undercut):       {gate_counts.get(1, 0):>6} ({gate_counts.get(1,0)/total:.1%})" if total > 0 else "")
    print(f"  Gate 2 (Strength fail):  {gate_counts.get(2, 0):>6} ({gate_counts.get(2,0)/total:.1%})" if total > 0 else "")
    print(f"  Gate 3 (SAFE = PASS):    {gate3:>6} ({gate3/total:.1%})" if total > 0 else "")
    print()
    print("  --- OPTIMIZATION QUALITY (Gate 3 only) ---")
    if gate3 > 0:
        avg_SH = sum(S_H_values) / len(S_H_values)
        avg_SF = sum(S_F_values) / len(S_F_values)
        avg_vol = sum(volumes) / len(volumes)
        min_vol = min(volumes)
        max_vol = max(volumes)
        avg_rew = sum(rewards) / len(rewards) if rewards else 0

        print(f"  Avg S_H (utilization):   {avg_SH:.4f}  (ideal: 0.90-0.98)")
        print(f"  Avg S_F (utilization):   {avg_SF:.4f}")
        print(f"  Sweet Spot Rate:         {sweet_count/gate3:.1%}  (0.90 <= S_H <= 0.98)")
        print(f"  Over-design Rate:        {over_count/gate3:.1%}  (S_H < 0.80)")
        print(f"  Avg Volume (mm3):        {avg_vol:,.0f}")
        print(f"  Min / Max Volume:        {min_vol:,.0f} / {max_vol:,.0f}")
        print(f"  Avg Reward (all):        {avg_rew:.2f}")

        # S_H distribution
        ranges = [(0, 0.5), (0.5, 0.7), (0.7, 0.8), (0.8, 0.9),
                  (0.9, 0.95), (0.95, 0.98), (0.98, 1.0)]
        print()
        print("  --- S_H DISTRIBUTION ---")
        for lo, hi in ranges:
            cnt = sum(1 for s in S_H_values if lo <= s < hi)
            bar = "#" * int(cnt / gate3 * 50) if gate3 > 0 else ""
            print(f"  [{lo:.2f}, {hi:.2f}): {cnt:>5} ({cnt/gate3:5.1%}) {bar}")
    else:
        print("  No states passed gate 3!")

    print()
    print("=" * 70)

    return gate3, total, untrained


def sanity_check():
    """Kiem tra formulas co chay duoc khong."""
    from environment.formulas import gear_design

    print()
    print("=" * 70)
    print("  SANITY CHECK - Vi du thu cong")
    print("=" * 70)

    result = gear_design(
        P_yc=5.5, n_yc=50, u_total=10, L_h=10000,
        load_type=1, u_d=3.15, psi_ba=0.315,
        matID="7", gear_type="rang_nghieng",
    )
    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return

    print(f"  T1 = {result['T1']:.1f} N.mm")
    print(f"  a_w = {result['a_w']} mm (calc: {result['a_w_calc']:.1f})")
    print(f"  m = {result['m']} mm")
    print(f"  z1 = {result['z1']}, z2 = {result['z2']}")
    print(f"  b_w = {result['b_w']:.1f} mm")
    print(f"  v = {result['v']:.2f} m/s")
    print(f"  K_Hv = {result['K_Hv']:.4f}")
    print(f"  sigma_H = {result['sigma_H']:.1f} / [{result['sigma_H_allow']:.1f}]  S_H = {result['S_H']:.4f}")
    print(f"  sigma_F = {result['sigma_F']:.1f} / [{result['sigma_F_allow']:.1f}]  S_F = {result['S_F']:.4f}")
    print(f"  pass_undercut = {result['pass_undercut']} (z1={result['z1']} >= z_min={result['z_min']:.1f})")
    print(f"  pass_H = {result['pass_H']}, pass_F = {result['pass_F']}")
    print(f"  K_HL = {result['K_HL']:.4f}, K_FL = {result['K_FL']:.4f}")


if __name__ == "__main__":
    sanity_check()
    validate()
    print("\n  Done.")
