import json
data = json.load(open('output/eval_log.json'))
print(f"{'Epoch':>10} | {'AvgReward':>10} | {'PassRate':>8} | {'AvgS_H':>7} | {'Sweet%':>7} | {'Stable%':>8} | {'Cover%':>7} | {'MeanMaxQ':>9}")
print("-" * 90)
for d in data:
    print(f"{d['epoch']:>10,} | {d['avg_reward_greedy']:>10.2f} | {d['pass_rate']:>8.1%} | {d['avg_S_H']:>7.3f} | {d['sweet_spot_rate']:>7.1%} | {d['policy_stability']:>8.1%} | {d['coverage']:>7.1%} | {d['mean_max_q']:>9.2f}")
