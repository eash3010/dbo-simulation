import numpy as np
import sys
from matplotlib import pyplot as plt
import matplotlib
from util import read_cloud_trace, data_generation, generate_random_trace
from traces.trace_indices import rand_idx1
from algorithms.dbo import DBO
from algorithms.cloudex import Cloudex
from algorithms.max_rtt import MaxRTT

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

cloud_trace = read_cloud_trace("traces/direct.zip")
rtt_arrs = data_generation(cloud_trace)
output_file = open("traces/simulation.dat", "a")

##   Use only a section of trace from MP1.
#### Use trace starting at index `trace_dd_idx`. This value was chosen randomly.
#### Fixed to this value to reproduce the figures.
mp1_rtt_trace = np.array(rtt_arrs[0])
trace_dd_idx = 53927275
latency_trace = mp1_rtt_trace[trace_dd_idx-150000:trace_dd_idx+1850000]

## Plot the network trace used.
fig, ax = plt.subplots(figsize=(8, 2.2))
plt.plot(np.arange(0, latency_trace.shape[0], 1)*0.001,latency_trace)
plt.xlabel("Time (ms)", fontsize=16)
plt.ylabel(r"Latency $(\mu s)$", fontsize=15)
plt.ylim(bottom=0, top=600)
plt.tight_layout()
plt.show()
# fig.savefig("figures/network_rtt_trace.pdf", bbox_inches='tight', dpi=450)
fig.savefig("figures/network_rtt_trace.png", bbox_inches='tight', dpi=450)


RT = 4
DELTA = 20
BATCH_SIZE = 25
g_step = 1
time_range = 1000000
g_time = []
for i in range(int(time_range/g_step)):
	g_time.append(i*g_step)

dbo_obj = DBO(DELTA, BATCH_SIZE, 0)
max_rtt_obj = MaxRTT()

def print_stats(sim_obj, output_file_hndlr=sys.stdout, delta=DELTA):
	print("{algorithm},{num_p},{win_ratio},{lrtf_ratio},{mean_l},{p99_l},{max_l}".format(
		algorithm=sim_obj.get_title(),
		num_p=number_participant,
		win_ratio=sim_obj.get_win_fraction(),
		lrtf_ratio=sim_obj.get_lrtf_fariness_ratio(delta),
		mean_l=sim_obj.get_mean_latency(),
		p99_l=sim_obj.get_99p_latency(),
		max_l=sim_obj.get_max_latency()),
		flush=True, file=output_file_hndlr)


for number_participant in range(10, 100, 10):
	fw_owd_arr = []
	rv_owd_arr = []
	response_time_arr = []
	for i in range(number_participant):
		response_time_arr.append(int(RT)+(number_participant-i-1)*(15.0/number_participant))
		temp_rtt_trace = generate_random_trace(latency_trace, rand_idx1[i], int(time_range*2))
		fw_owd_arr.append([x/2 for x in temp_rtt_trace])
		rv_owd_arr.append([x/2 for x in temp_rtt_trace])

	print("Running DBO for %d MPs" % number_participant)
	dbo_obj.set_simulation_environment(g_time, time_range, number_participant, fw_owd_arr, rv_owd_arr, response_time_arr, g_step)
	dbo_obj.run_simulation()
	print_stats(dbo_obj)
	print_stats(dbo_obj, output_file)

	print("Running MaxRTT for %d MPs" % number_participant)
	max_rtt_obj.set_simulation_environment(g_time, time_range, number_participant, fw_owd_arr, rv_owd_arr, response_time_arr, g_step)
	max_rtt_obj.run_simulation()
	print_stats(max_rtt_obj)
	print_stats(max_rtt_obj, output_file)

for number_participant in [10, 60]:
	fw_owd_arr = []
	rv_owd_arr = []
	response_time_arr = []
	for i in range(number_participant):
		response_time_arr.append(int(RT)+(number_participant-i-1)*(15.0/number_participant))
		temp_rtt_trace = generate_random_trace(latency_trace, rand_idx1[i], int(time_range*2))
		fw_owd_arr.append([x/2 for x in temp_rtt_trace])
		rv_owd_arr.append([x/2 for x in temp_rtt_trace])

	for dd in sorted(list(range(10, 360, 10))+[15]):
		print("Running Cloudex for %d MPs, %d" % (number_participant, dd))
		cloudex_obj = Cloudex(dd, dd)
		cloudex_obj.set_simulation_environment(g_time, time_range, number_participant, fw_owd_arr, rv_owd_arr, response_time_arr, g_step)
		cloudex_obj.run_simulation()
		print_stats(cloudex_obj)
		print_stats(cloudex_obj, output_file)
