"""
MechDrive AI — Train Gear Agent
==================================
Script chạy train Q-Learning cho bộ truyền bánh răng.

Usage:
    python train_gear.py [--epochs N] [--quiet]
"""

import sys
import os
import time
import argparse

# Ensure package imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import EPOCHS_GEAR, P_BUCKETS, N_BUCKETS, LOAD_TYPES
from agents.gear_agent import GearAgent


def main():
    parser = argparse.ArgumentParser(description="Train Gear Q-Learning Agent")
    parser.add_argument("--epochs", type=int, default=EPOCHS_GEAR, help="Number of training epochs")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-epoch output")
    args = parser.parse_args()

    print("=" * 70)
    print("  MechDrive AI — GEAR AGENT TRAINING")
    print("=" * 70)
    print(f"  Epochs:       {args.epochs:,}")
    print(f"  Action space: {len(GearAgent().all_actions):,} actions")
    print(f"  State space:  {len(P_BUCKETS) * len(N_BUCKETS) * len(LOAD_TYPES)} states")
    print("=" * 70)

    agent = GearAgent()
    start = time.time()

    # Rolling average
    window = 1000
    reward_buffer = []
    reward_curve = []

    for epoch in range(1, args.epochs + 1):
        reward = agent.train_step()
        reward_buffer.append(reward)

        if len(reward_buffer) > window:
            reward_buffer.pop(0)

        if epoch % window == 0:
            avg_reward = sum(reward_buffer) / len(reward_buffer)
            reward_curve.append(avg_reward)
            stats = agent.get_stats()

            if not args.quiet:
                elapsed = time.time() - start
                eps_per_sec = epoch / elapsed if elapsed > 0 else 0
                print(
                    f"  [{epoch:>8,}/{args.epochs:,}]  "
                    f"ε={agent.epsilon:.4f}  "
                    f"avg_R={avg_reward:>8.1f}  "
                    f"pass={stats['pass_rate']:.1%}  "
                    f"speed={eps_per_sec:.0f} ep/s"
                )

    elapsed = time.time() - start
    print()
    print("=" * 70)
    print("  TRAINING COMPLETE")
    print("=" * 70)

    stats = agent.get_stats()
    print(f"  Total episodes:  {stats['total_episodes']:,}")
    print(f"  Pass rate:       {stats['pass_rate']:.1%}")
    print(f"  Avg reward:      {stats['avg_reward']:.2f}")
    print(f"  Final ε:         {stats['epsilon']:.6f}")
    print(f"  Q-Table states:  {stats['q_table_states']}")
    print(f"  Time elapsed:    {elapsed:.1f}s")
    print()

    # Export Q-Table
    best = agent.export_best_actions()
    untrained = sum(1 for v in best.values() if "error" in v)
    print(f"  Untrained states: {untrained}/{len(best)}")

    # Show some sample results
    print()
    print("  ── Sample Best Actions ──")
    samples = [
        (4.5, 50, 1, "4.5kW, 50rpm, Va đập nhẹ"),
        (5.5, 50, 1, "5.5kW, 50rpm, Va đập nhẹ"),
        (3.0, 100, 0, "3.0kW, 100rpm, Tĩnh"),
        (7.0, 75, 2, "7.0kW, 75rpm, Va đập mạnh"),
        (10.0, 35, 1, "10kW, 35rpm, Va đập nhẹ"),
    ]
    for P, n, load, desc in samples:
        result = agent.get_best_action(P, n, load)
        if "error" not in result:
            print(
                f"  {desc:40s} → "
                f"gear={result['gear_type']}, "
                f"u_d={result['optimal_ud']}, "
                f"ψ_ba={result['optimal_psi_ba']}, "
                f"z₁={result['optimal_zg1']}, "
                f"mat={result['matID']}, "
                f"Q={result['q_value']:.0f}"
            )
        else:
            print(f"  {desc:40s} → {result}")

    # Save reward curve
    import json
    curve_path = os.path.join(os.path.dirname(__file__), "output", "gear_reward_curve.json")
    with open(curve_path, "w") as f:
        json.dump(reward_curve, f)
    print(f"\n  Reward curve saved → {curve_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
