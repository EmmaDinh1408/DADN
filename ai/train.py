"""
MechDrive AI — Training Script
==================================
Train Q-Learning Agent 1 trieu vong lap.
Danh gia mo hinh bang 8 chi so chinh thuc.

Usage:
    python train.py [--epochs N] [--eval-every N]
"""

import sys
import os
import time
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    EPOCHS, EVAL_EVERY, LOG_EVERY,
    TOTAL_STATES, TOTAL_ACTIONS, OUTPUT_DIR,
)
from agents.ql_agent import QLAgent


def main():
    parser = argparse.ArgumentParser(description="Train MechDrive Q-Learning")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--eval-every", type=int, default=EVAL_EVERY)
    parser.add_argument("--log-every", type=int, default=LOG_EVERY)
    args = parser.parse_args()

    print("=" * 78)
    print("  MechDrive AI - Q-LEARNING TRAINING")
    print("  Ban Dac Ta Chinh Thuc - 1 Agent, 5 State, 5 Action")
    print("=" * 78)
    print(f"  States:      {TOTAL_STATES:,}")
    print(f"  Actions:     {TOTAL_ACTIONS:,}")
    print(f"  Q-Table:     {TOTAL_STATES * TOTAL_ACTIONS:,} cells")
    print(f"  Epochs:      {args.epochs:,}")
    print(f"  Eval every:  {args.eval_every:,}")
    print("=" * 78)

    agent = QLAgent()
    start = time.time()

    # Rolling window for progress logging
    window = args.log_every
    reward_buffer = []

    # Evaluation history
    eval_log = []

    for epoch in range(1, args.epochs + 1):
        reward, info = agent.train_step()
        reward_buffer.append(reward)
        if len(reward_buffer) > window:
            reward_buffer.pop(0)

        # Linear epsilon decay
        agent.decay_epsilon_linear(epoch, args.epochs)

        # ── Progress Log ──
        if epoch % args.log_every == 0:
            avg_r = sum(reward_buffer) / len(reward_buffer)
            elapsed = time.time() - start
            speed = epoch / elapsed if elapsed > 0 else 0
            g3 = agent.gate_counts.get(3, 0)
            total = agent.episode_count
            print(
                f"  [{epoch:>10,}/{args.epochs:,}]  "
                f"eps={agent.epsilon:.3f}  "
                f"avg_R={avg_r:>8.1f}  "
                f"gate3={g3/total:.1%}  "
                f"speed={speed:.0f}/s"
            )

        # ── Full Evaluation Checkpoint ──
        if epoch % args.eval_every == 0:
            metrics = agent.evaluate_policy()
            q_stats = agent.get_q_value_stats()

            eval_entry = {
                "epoch": epoch,
                "epsilon": round(agent.epsilon, 4),
                **metrics,
                **q_stats,
            }
            eval_log.append(eval_entry)

            print()
            print(f"  ====== EVAL @ epoch {epoch:,} ======")
            print(f"  | Greedy avg reward:   {metrics['avg_reward_greedy']:>10.2f}")
            print(f"  | Pass rate (gate 3):  {metrics['pass_rate']:>10.1%}")
            print(f"  | Avg S_H (util.):     {metrics['avg_S_H']:>10.3f}   (ideal: 0.90-0.98)")
            print(f"  | Sweet spot rate:     {metrics['sweet_spot_rate']:>10.1%}   (0.90<=S_H<=0.98)")
            print(f"  | Policy stability:    {metrics['policy_stability']:>10.1%}")
            print(f"  | Coverage:            {metrics['coverage']:>10.1%}")
            print(f"  | Mean max Q:          {q_stats['mean_max_q']:>10.2f}")
            print(f"  | Q std:               {q_stats['std_q']:>10.2f}")
            print(f"  | Gate dist:           {metrics['gate_distribution']}")
            print(f"  ================================")
            print()

    # ── Final Summary ──
    elapsed = time.time() - start
    final_metrics = agent.evaluate_policy()
    final_q = agent.get_q_value_stats()

    print()
    print("=" * 78)
    print("  TRAINING COMPLETE")
    print("=" * 78)
    print(f"  Time:        {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Speed:       {args.epochs/elapsed:.0f} ep/s")
    print(f"  Final eps:   {agent.epsilon:.6f}")
    print()
    print("  --- EVALUATION METRICS ---")
    print(f"  1. Avg Reward (greedy):  {final_metrics['avg_reward_greedy']:.2f}")
    print(f"  2. Pass Rate:            {final_metrics['pass_rate']:.1%}")
    print(f"  3. Avg S_H utilization:  {final_metrics['avg_S_H']:.4f}")
    print(f"  4. Sweet Spot Rate:      {final_metrics['sweet_spot_rate']:.1%}")
    print(f"  5. Policy Stability:     {final_metrics['policy_stability']:.1%}")
    print(f"  6. Coverage:             {final_metrics['coverage']:.1%}")
    print(f"  7. Mean Max Q-value:     {final_q['mean_max_q']:.2f}")
    print(f"  8. Q-value Std Dev:      {final_q['std_q']:.2f}")
    print(f"  9. Gate Distribution:    {final_metrics['gate_distribution']}")
    print()

    # Gate breakdown
    total_eps = agent.episode_count
    print("  --- GATE BREAKDOWN (Training) ---")
    for g in sorted(agent.gate_counts.keys()):
        cnt = agent.gate_counts[g]
        pct = cnt / total_eps if total_eps > 0 else 0
        labels = {0: "Pre-validation fail", 1: "Undercut (z<z_min)",
                  2: "Strength fail", 3: "Safe zone (optimizing)"}
        print(f"  Gate {g} ({labels.get(g, '?'):25s}): {cnt:>10,} ({pct:.1%})")

    # Export
    print()
    agent.export_qtable()

    # Save eval log
    eval_path = str(OUTPUT_DIR / "eval_log.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_log, f, indent=2)
    try:
        print(f"  [Export] Eval log -> {eval_path}")
    except UnicodeEncodeError:
        print(f"  [Export] Eval log -> (path contains unicode)")

    # Save reward curve (sampled)
    curve = []
    step = max(1, len(agent.reward_history) // 1000)
    for i in range(0, len(agent.reward_history), step):
        chunk = agent.reward_history[i:i+step]
        curve.append(sum(chunk) / len(chunk))
    curve_path = str(OUTPUT_DIR / "reward_curve.json")
    with open(curve_path, "w") as f:
        json.dump(curve, f)
    try:
        print(f"  [Export] Reward curve -> {curve_path}")
    except UnicodeEncodeError:
        print(f"  [Export] Reward curve -> (path contains unicode)")

    # Sample best actions
    print()
    print("  --- SAMPLE BEST ACTIONS ---")
    samples = [
        (5, 50, 10, 10000, 1, "P=5kW n=50 u=10 Lh=10k VDN"),
        (7, 100, 12.5, 15000, 1, "P=7kW n=100 u=12.5 Lh=15k VDN"),
        (3, 75, 8, 10000, 0, "P=3kW n=75 u=8 Lh=10k Tinh"),
        (10, 150, 15, 20000, 2, "P=10kW n=150 u=15 Lh=20k VDM"),
        (15, 200, 20, 5000, 1, "P=15kW n=200 u=20 Lh=5k VDN"),
    ]
    for P, n, u, Lh, load, desc in samples:
        r = agent.get_best_action(P, n, u, Lh, load)
        if "error" not in r:
            print(
                f"  {desc:45s} -> "
                f"ud={r['optimal_ud']}, psi={r['optimal_psi_ba']}, "
                f"mat={r['matID']}, gear={r['gear_type']}, "
                f"z1c={r['z1_chain']}, Q={r['q_value']:.0f}"
            )
        else:
            print(f"  {desc:45s} -> {r}")

    print()
    print("=" * 78)


if __name__ == "__main__":
    main()
