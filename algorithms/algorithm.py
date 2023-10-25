import pylab as pl
import math
import numpy as np
import sys
import os
import matplotlib
from matplotlib import pyplot as plt
import subprocess
import matplotlib.ticker as mticker
from matplotlib.ticker import ScalarFormatter
from statistics import median, mean
# from abc import ABC, abstractmethod

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


class Algorithm():
	"""
	Define a super class of algorithms used in simulation.

	This class can be extended to simulate various algorithms for data delivery and
	ordering of trades. The data points are generated at the CES and are sent to all
	the RBs. RBs deliver it to the MPs based oon algorithms which can be modified. The
	MPs respond with a trade for each data point which is submitted to the RB. RBs forward
	these trades to the OB which orders them and asks CES to execute them accordingly.
	The RBs may timestamp the trades which can be used to modify the OB's ordering
	algorithm.
	"""
	def __init__(self):
		self.reset_variables()

	def reset_variables(self):
		"""
		Re-initiallize all class variables and reset environment.
		"""
		self.r_time_arr = []
		self.d_time_arr = []
		self.submission_time_arr = []
		self.receive_at_ob_arr = []
		self.ordering_arr = []
		self.execution_time_arr = []
		self.latency_arr = []
		self.ack_time_arr = []
		self.g_time = []
		self.time_range = []
		self.number_participants = []
		self.g_step = []
		self.fw_owd_arr = []
		self.rv_owd_arr = []
		self.response_times = []

	def get_title(self):
		"""
		Get the title/name of the algorithm used.

		Returns:
			string: Title of the algorithm.
		"""
		raise NotImplementedError

	def get_r_time(self, g_time, fwd_ow_delay):
		"""
		Calculates the time when the RB receives the data from the CES.

		Args:
			g_time (list(float)): Real times when CES generates data points.
			fwd_ow_delay (list(float)): One way delay from CES to RB at all times of horizon, `time_range`.

		Returns:
			list(float): Real times when RB receive various data points from the CES.
		"""
		answer = []
		for i in range(len(g_time)):
			answer.append(g_time[i] + fwd_ow_delay[int(g_time[i])])
		assert(all(answer[i] <= answer[i+1] for i in range(len(answer) - 1)))
		return answer

	def get_d_time(self, **kwargs):
		"""
		Calculate the times when data points, received from the CES at RB, are sent to the MP.
		It assumes that the MP is very close to the RB and hence the transmission time is
		assumed 0 for simulation purposes. The results would not change if we assume some small
		bounded delay here as shown in Theorem 4.

		Define the delivery algorithm here. This will depend on the alhgorithm (class) and the
		hyperparameters.

		Returns:
			list(float): Real times when RB sends data points to the MP.
		"""
		raise NotImplementedError

	def get_submission_time(self, d_time, response_time):
		"""
		Calculate the submission times of trades for each data point. Assumes exactly one trade is
  		generated after exactly `response_time` has passed since the data point is received by the MP.

		Args:
			d_time (list(float)): Real times when CES generates data points.
			response_time (float): Time taken by MP to respond to the data point with a trade.

		Returns:
			list(float): Real times when trade is submitted to the RB from the MP.
		"""
		answer = []
		for i in range(len(d_time)):
			answer.append(d_time[i] + response_time)
		return answer

	def get_receive_at_ob(self, submission_time, rv_owd):
		"""
		Calculate the time when trades generated by an MP reach the CES.

		Args:
			submission_time (list(float)): Real times when trade is submitted to the RB from the MP.
			rv_owd (list(float)): One way delay from RB to CES at all times on the horizon, `time_range`.

		Returns:
			list(float): Real times when trades are received by the OB.
		"""
		answer = []
		for i in range(len(submission_time)):
			answer.append(submission_time[i]+rv_owd[int(submission_time[i])])
		return answer

	def get_ordering(self):
		"""
		Generate a total ordering of trades in which they can be executed. The total order is defined
		on an independent real number line.

		Returns:
			list(float): A total ordering of trades.
		"""
		raise NotImplementedError

	def win_prob_2_before_1(self, ordering_1, ordering_2):
		"""
		Get the win ratio between trades following `ordering_` and `ordering_2`.

		Args:
			ordering_1 (list(float)): ordering of trades on an MP.
			ordering_2 (list(float)): ordering of trades on another MP.

		Returns:
			float: ratio of trades following ordering_2 which are ordered ahead of trades following `ordering_1`.
		"""
		answer = 0
		for i in range(len(ordering_1)):
			if ordering_2[i] < ordering_1[i]:
				answer += 1
		answer /= (1.0*len(ordering_1))
		return answer

	def get_execution_time(self):
		"""
		Get the execution time of trades from a single MP.

		Returns:
			list(float): Real times of execution of trades from a single MP at the CES.
		"""
		raise NotImplementedError

	def get_e2e_latency(self, g_time, execution_time, response_time):
		"""
		Get the end-to-end latency of a trade. This is calculated as the time measured from
		generation of a data point at the CES to execution of trade generated by MP in
		response to the data point minus the response time at the MP.

		Args:
			g_time (list(float)): Real times when CES generates data points.
			execution_time (list(float)): Real times of execution of trades from a single MP at the CES.
			response_time (float): Time taken by MP to respond to the data point with a trade.

		Returns:
			list(float): The end-to-end latency for all trades from a single MP.
		"""
		answer = []
		for i in range(len(g_time)):
			latency = execution_time[i] - g_time[i] - response_time
			answer.append(latency)
		return answer

	def set_simulation_environment(self, g_time, time_range, number_participants, fw_owd_arr, rv_owd_arr, response_times, g_step=1):
		"""
		Set the simulation environment. This function resets the environment variables before the simulation
		and sets the rest of the variables to appropriate values.

		Args:
			g_time (list(float)): Real times when CES generates data points.
			time_range (int): The time horizon being simulated.
			number_participants (int): Number of MPs.
			fw_owd_arr (list(float)): One way delay from CES to RB at all times of horizon, `time_range`.
			rv_owd_arr (list(float)): One way delay from RB to CES at all times on the horizon, `time_range`.
			response_times (list(float)): Response times of the various MPs. `len(response_times)=number_participants`
			g_step (int, optional): The frequency at which data is generated at the CES. Defaults to 1.
		"""
		## reinitialize all state variables
		self.reset_variables()
		self.g_time = g_time
		self.time_range = time_range
		self.number_participants = number_participants
		self.g_step = g_step
		self.fw_owd_arr = fw_owd_arr
		self.rv_owd_arr = rv_owd_arr
		self.response_times = response_times

	def run_simulation(self):
		"""
		Run the simulation and calculate the exectution times and latencies for all trades.
		"""
		raise NotImplementedError

	def get_win_fraction(self):
		"""
		Calculate the fairness ratio as ratio of the number of competing trade pairs that were
		ordered correctly (based on Response time Fairness) to the total number of competing trade
		sets for all unique pairs of market participants.

		Returns:
			float: Win fraction (fairness) between all participants for all trades.
		"""
		win_fraction = 0
		total = 0
		for i in range(self.number_participants):
			for j in range(self.number_participants):
				if i>=j:
					continue
				total += 1.0
				if self.response_times[i] > self.response_times[j]:
					win_fraction += self.win_prob_2_before_1(self.ordering_arr[i], self.ordering_arr[j])
				else:
					win_fraction += self.win_prob_2_before_1(self.ordering_arr[j], self.ordering_arr[i])
		return win_fraction/total

	def get_mean_latency(self):
		"""
		Get mean end-to-end latency of the trades.
		"""
		return np.mean(np.array(self.latency_arr))

	def get_99p_latency(self):
		"""
		Get 99 percentile end-to-end latency of the trades.
		"""
		return np.percentile(np.array(self.latency_arr).flatten(), 99)

	def get_max_latency(self):
		"""
		Get maximum end-to-end latency of the trades.
		"""
		return np.max(np.array(self.latency_arr))
