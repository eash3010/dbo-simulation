import numpy as np
import argparse
from util import read_cloud_trace, data_generation, generate_random_trace
from traces.trace_indices import rand_idx1
from algorithms.dbo import DBO
from algorithms.cloudex import Cloudex
from algorithms.max_rtt import MaxRTT
from algorithms.direct import DirectDelivery

parser = argparse.ArgumentParser(description='Run simulation.')
parser.add_argument('--algo', '-a', type=str, default="dbo", choices=["max-rtt", "dbo", "cloudex", "direct"], help='Algorithm to run (max-rtt/dbo/cloudex/direct)')
parser.add_argument('--num_p', '-n', type=int, default=10, help='Number of participants')
parser.add_argument('--delta', '-d', type=int, default=10, help='Delta for DBO (in us)')
parser.add_argument('--batch_size', '-b', type=int, default=25, help='Batch size for DBO (in us)')
parser.add_argument('--dd', '-dd', type=int, default=15, help='Delay threshold for Cloudex (in us)')
parser.add_argument('--trace', '-t', type=str, default="traces/direct.zip", help='Cloud trace file to use')

## Define maximum and minimum response times for MPs
## The response times are chosen such that the MPs are sorted in increasing order of response times.
MAX_RT = 19
MIN_RT = 4

g_step = 1
time_range = 1000000
g_time = []
for i in range(int(time_range/g_step)):
	g_time.append(i*g_step)

if __name__ == "__main__":
	args = parser.parse_args()

	print("Reading cloud trace file...")
	cloud_trace = read_cloud_trace(args.trace)
	rtt_arrs = data_generation(cloud_trace)

	##   Use only a section of trace from MP1.
	#### Use trace starting at index `trace_dd_idx`. This value was chosen randomly.
	#### Fixed to this value to reproduce the results.
	mp1_rtt_trace = np.array(rtt_arrs[0])
	trace_dd_idx = 53927275
	latency_trace = mp1_rtt_trace[trace_dd_idx-150000:trace_dd_idx+1850000]

	fw_owd_arr = []
	rv_owd_arr = []
	response_time_arr = []
	for i in range(args.num_p):
		response_time_arr.append(int(MIN_RT)+(args.num_p-i-1)*((MAX_RT-MIN_RT)/args.num_p))
		temp_rtt_trace = generate_random_trace(latency_trace, rand_idx1[i], int(time_range*2))
		fw_owd_arr.append([x/2 for x in temp_rtt_trace])
		rv_owd_arr.append([x/2 for x in temp_rtt_trace])

	sim_obj = None
	if args.algo == "dbo":
		sim_obj = DBO(args.delta, args.batch_size, 0)
	elif args.algo == "cloudex":
		sim_obj = Cloudex(args.dd, args.dd)
	elif args.algo == "max-rtt":
		sim_obj = MaxRTT()
	elif args.algo == "direct":
		sim_obj = DirectDelivery()

	print("Running %s for %d MPs" % (sim_obj.get_title(), args.num_p))
	print()
	sim_obj.set_simulation_environment(g_time, time_range, args.num_p, fw_owd_arr, rv_owd_arr, response_time_arr, g_step)
	sim_obj.run_simulation()
	print("Response Time Fairness ratio: %f" % sim_obj.get_win_fraction())
	print("LRTF fairness ratio (delta=%f): %f" % (args.delta, sim_obj.get_lrtf_fariness_ratio(args.delta)))
	print("Mean latency: %f us" % sim_obj.get_mean_latency())
	print("99th percentile latency: %f us" % sim_obj.get_99p_latency())
