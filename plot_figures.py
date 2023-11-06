from matplotlib import pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

participants = list(range(10, 100, 10))

f = open("traces/simulation.dat", "r")

fairness = {}
latency = {}
tail_latency = {}

for line in f:
	l = line.strip().split(",")
	d_type = l[0].split('(')[0]
	n_participants = int(l[1])
	if d_type not in fairness:
		fairness[d_type] = {}
		latency[d_type] = {}
		tail_latency[d_type] = {}
	if n_participants not in fairness[d_type]:
		fairness[d_type][n_participants] = []
		latency[d_type][n_participants] = []
		tail_latency[d_type][n_participants] = []
	fairness[d_type][n_participants].append(float(l[2]))
	latency[d_type][n_participants].append(float(l[4]))
	tail_latency[d_type][n_participants].append(float(l[5]))

plt.figure(figsize=(4,3))
plt.plot(participants, [latency["DBO"][x] for x in participants],color='C0', label="DBO", marker='D', markersize=5)
plt.plot(participants, [latency["MaxRTT"][x] for x in participants] ,color='C2', label="Max-RTT", marker='^', markersize=5)
plt.ylim(bottom=0)
plt.xticks(range(10,100,20))
plt.xlabel("# Participants", fontsize =14)
plt.ylabel(r"Latency $(\mu s)$", fontsize=14)
plt.legend(prop={'size': 14})
# plt.legend(bbox_to_anchor=(-0.1, 1.02, 1.1, 1.02), loc=4, ncol=2, mode="expand", borderaxespad=0., prop={'size': 14}, frameon=False)
plt.tight_layout()
plt.title("Mean latency")
# plt.savefig("figures/avg_latency.pdf", bbox_inches='tight', dpi=450)
plt.savefig("figures/avg_latency_scaling.png", bbox_inches='tight', dpi=450)


plt.figure(figsize=(4,3))
plt.plot(participants, [tail_latency["DBO"][x] for x in participants], color='C0', marker='D', markersize=5, label="DBO")
plt.plot(participants, [tail_latency["MaxRTT"][x] for x in participants], color='C2', marker='^', label="Max-RTT", markersize=5)
# plt.legend(bbox_to_anchor=(-0.1, 1.02, 1.1, 1.02), loc=3, ncol=2, mode="expand", borderaxespad=0., prop={'size': 14}, frameon=False)
plt.legend(prop={'size': 14})
plt.ylim(bottom=0)
plt.xticks(range(10,100,20))
plt.xlabel("# Participants", fontsize =14)
plt.ylabel(r"Latency $(\mu s)$", fontsize=14)
plt.tight_layout()
plt.title("Tail latency")
# plt.savefig("figures/tail_latency_scaling.pdf", bbox_inches='tight', dpi=450)
plt.savefig("figures/tail_latency_scaling.png", bbox_inches='tight', dpi=450)


plt.figure(figsize=(4,3))
plt.ylabel("Fairness", fontsize =14)
plt.xlabel(r"Latency $(\mu s)$", fontsize =14)

st_idx = 1
en_idx = 30

plt.plot(latency["Cloudex"][10][st_idx:en_idx], fairness["Cloudex"][10][st_idx:en_idx], label="CloudEx, 10 MPs", marker='o', linestyle='--', linewidth=2, markersize=6, zorder=1)
plt.plot(latency["Cloudex"][60][st_idx:en_idx], fairness["Cloudex"][60][st_idx:en_idx], label="CloudEx, 60 MPs", marker='o', linestyle='--', linewidth=2, markersize=6, zorder=1)
plt.scatter(latency["DBO"][10], fairness["DBO"][10], label="DBO, 10 MPs", marker='d', s=100, c="red", zorder=2)
plt.scatter(latency["DBO"][60], fairness["DBO"][60], label="DBO, 60 MPs", marker='d', s=100, c="green", zorder=2)
plt.legend(prop={'size': 14})
plt.xlim(left=0)
plt.tight_layout()
plt.title("Mean latency vs Fairness")
# plt.savefig("figures/latency_v_fairness.pdf", bbox_inches='tight', dpi=450)
plt.savefig("figures/latency_v_fairness.png", bbox_inches='tight', dpi=450)


plt.figure(figsize=(4,3))
plt.ylabel("Fairness", fontsize =14)
plt.xlabel(r"Tail Latency p99 $(\mu s)$", fontsize =14)
plt.plot(tail_latency["Cloudex"][10][st_idx:en_idx], fairness["Cloudex"][10][st_idx:en_idx], label="CloudEx, 10 MPs", marker='o', linestyle='--', linewidth=2, markersize=6, zorder=1)
plt.plot(tail_latency["Cloudex"][60][st_idx:en_idx], fairness["Cloudex"][60][st_idx:en_idx], label="CloudEx, 60 MPs", marker='o', linestyle='--', linewidth=2, markersize=6, zorder=1)
plt.scatter(tail_latency["DBO"][10], fairness["DBO"][10], label="DBO, 10 MPs", marker='d', s=100, c="red", zorder=2)
plt.scatter(tail_latency["DBO"][60], fairness["DBO"][60], label="DBO, 60 MPs", marker='d', s=100, c="green", zorder=2)
plt.xlim(left=0)
plt.legend(prop={'size': 14})
plt.tight_layout()
plt.title("Tail latency vs Fairness")
# plt.savefig("figures/tail_latency_v_fairness.pdf", bbox_inches='tight', dpi=450)
plt.savefig("figures/tail_latency_v_fairness.png", bbox_inches='tight', dpi=450)
