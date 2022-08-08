import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import csv
from collections import defaultdict

columns = ['episode_reward_mean', 'episode_reward_min',
           'episode_reward_max', 'training_iteration']
res_dirs = {}
filepath = "/home/jy/ray_results/stabilizing_the_ring/" + \
	"PPO_WaveAttenuationPOEnv-v0_5cf4f8f4_2022-05-10_07-13-28o_8bn6g_/progress.csv"
rewards_data = defaultdict(list)
with open(filepath) as f:
	reader = csv.DictReader(f)
	for row in reader:
		for col in columns:
			rewards_data[col].append(float(row[col]))

plt.plot(rewards_data['training_iteration'],
		 rewards_data['episode_reward_mean'], label="ring_reward")
plt.fill_between(rewards_data['training_iteration'],
				 rewards_data['episode_reward_min'], rewards_data['episode_reward_max'], alpha=0.5)

plt.legend()
plt.xlabel("iterations")
plt.ylabel("mean reward")
plt.savefig("results.png", bbox_inches="tight")
plt.show()
