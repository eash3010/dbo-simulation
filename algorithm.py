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
	"""
	def __init__(self):
		self.reset_variables()

	def reset_variables(self):
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
		raise NotImplementedError

	def get_r_time(self, g_time, delay):
		"""
		Calculates the time when the RB receives the data from the CES.

		Args:
			g_time (array(float)): Timestamps of the market data generated at the CES.
			delay (array(float)): One way delay from CES to RB at all times of horizon, `time_range`.

		Returns:
			array(float): Real Time when RB receives the data points from CES.
		"""
		answer = []
		for i in range(len(g_time)):
			answer.append(g_time[i] + delay[int(g_time[i])])
		assert(all(answer[i] <= answer[i+1] for i in range(len(answer) - 1)))
		return answer

	def get_d_time(self, **kwargs):
		"""
  		Define the delivery algorithm here. This will depend on the alhgorithm (class) and the
		hyperparameters.

		Returns:
			array(float): Real timestamp when RB sends data to the MP.
		"""
		raise NotImplementedError

	def get_submission_time(self, d_time, response_time):
		"""
		Calculate the submission times of trades for each data point. Assumes exactly one trade is
  		generated after exactly `response_time` has passed since the data point is received by the MP.

		Args:
			d_time (array(float)): Real timestamp when MP receives data from RB.
			response_time (float): Time taken by MP to respond to the data point with a trade.

		Returns:
			array(float): Real time when trade is submitted to the RB from the MP.
		"""
		answer = []
		for i in range(len(d_time)):
			answer.append(d_time[i] + response_time)
		return answer

	def get_receive_at_ob(self, submission_time, rv_owd):
		answer = []
		for i in range(len(submission_time)):
			answer.append(submission_time[i]+rv_owd[int(submission_time[i])])
		return answer

	def get_ordering(self):
		raise NotImplementedError

	def win_prob_2_before_1(self, ordering_1, ordering_2):
		answer = 0
		for i in range(len(ordering_1)):
			if ordering_2[i] < ordering_1[i]:
				answer += 1
		answer /= (1.0*len(ordering_1))
		return answer

	def get_execution_time(self):
		raise NotImplementedError

	def get_e2e_latency(self, g_time, execution_time, response_time):
		answer = []
		for i in range(len(g_time)):
			latency = execution_time[i] - g_time[i] - response_time
			answer.append(latency)
		return answer

	def set_simulation_environment(self, g_time, time_range, number_participants, fw_owd_arr, rv_owd_arr, response_times, g_step=1):
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
		raise NotImplementedError

	def get_win_fraction(self):
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
		return np.mean(np.array(self.latency_arr))

	def get_99p_latency(self):
		return np.percentile(np.array(self.latency_arr).flatten(), 99)

	def get_max_latency(self):
		return np.max(np.array(self.latency_arr))
