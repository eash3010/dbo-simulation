import random
import numpy as np
import pandas

## Generate a trace of one way delays for `time_range` horizon with constant
## transmission time for all time.
def constant_delay(latency, time_range):
	answer = []
	for i in range(time_range):
		answer.append(latency)
	return answer

## Generate a trace of one way delays for `time_range` horizon with variale
## transmission time for all time. This generates a random walk with spikes.
def variable_delay(min_latency, max_latency, time_range, nonce):
	random.seed(nonce)
	answer = []
	answer.append(min_latency)
	for i in range(time_range - 1):
		current = answer[len(answer) - 1]
		temp = random.uniform(0,1)
		if temp < 0.8:
			current -= 0.95
		elif temp < 0.95:
			current += 0
		elif temp <0.9998:
			current += 1
		else:
			current += random.randint(0,200)
		if current < min_latency:
			current = min_latency
		if current > max_latency:
			current = max_latency
		answer.append(current)
	return answer

## Read the cloud trace from the `trace_filename`. Also calculate the end-to-end
## latency (e2e), receive latency (receive_e2e: e2e latency minus any buffering
## delay at the OB), delay at the OB and network RTT.
def read_cloud_trace(trace_filename="traces/direct.zip"):
	cloud_trace = pandas.read_csv(trace_filename)
	cloud_trace['e2e'] = (cloud_trace['execution_time'] - cloud_trace['generation_time'] - cloud_trace['response_time'])
	cloud_trace['receive_e2e'] = (cloud_trace['ces_recv_time'] - cloud_trace['generation_time'] - cloud_trace['response_time'])
	cloud_trace['ob_delay'] = cloud_trace['execution_time']-cloud_trace['ces_recv_time']
	cloud_trace['rtt'] = cloud_trace['e2e']-cloud_trace['pacing_delay']-cloud_trace['ob_delay']
	cloud_trace = cloud_trace.sort_values(by='generation_time')
	return cloud_trace

def generate_random_trace(trace_, rand_x_, time_range_):
	if rand_x_+time_range_<trace_.shape[0]:
		ret = trace_[rand_x_:rand_x_+time_range_]
	else:
		ret = np.concatenate([trace_[rand_x_:], trace_[:time_range_-(trace_.shape[0]-rand_x_)]])
	return ret


def data_generation(cloud_trace):
	rtt_arrs = []
	## Use `np.sort(cloud_trace.mp_id.unique())` for traces from all MPs
	# for i in np.sort(cloud_trace.mp_id.unique()):
	for i in [1]:
		print("Generating RTTs from trace of MP:", i)
		temp = cloud_trace[cloud_trace['mp_id']==i]
		x = temp['generation_time'].to_numpy()
		y = temp['rtt'].to_numpy()
		x = x - x[0]
		st = 0
		old_time_step = 0
		rtt_arr = []
		while True:
			if (st+1 >= len(x)):
				break
			time_step = old_time_step + 1
			while st+1<len(x) and time_step > x[st+1]:
				st = st+1
			if st+1>=len(x):
				break
			rtt = y[st]+(y[st+1]-y[st])*(time_step-x[st])/float(x[st+1]-x[st])
			if rtt<0:
				print(x[st], x[st+1], y[st], y[st+1], time_step)
			rtt_arr.append(rtt)
			old_time_step = time_step
		rtt_arrs.append(rtt_arr)
	return rtt_arrs