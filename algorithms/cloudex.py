from .algorithm import Algorithm

class Cloudex(Algorithm):
	"""
	Cloudex algorithm which assumes perfect clock synchronization and buffers data points and trades
	at RBs and OB.
	"""
	def __init__(self, d_o, d_i):
		# Cloudex threshold delay at the RB. This is the minimum time since generation after which
		# a data point may be delivered to an MP.
		self.d_o = d_o
		# Cloudex threshold delay at the OB. This is the minimum time since generation after which
		# a trade may be delivered to the CES for execution.
		self.d_i = d_i
		super().__init__()

	def get_title(self):
		return "Cloudex({d_o}|{d_i})".format(d_o = self.d_o, d_i = self.d_i)

	def get_d_time(self, g_time, r_time):
		"""
		Calculate the times when data points, received from the CES at RB, are sent to the MP.
		It assumes that the MP is very close to the RB and hence the transmission time is
		assumed 0 for simulation purposes.

		For Cloudex with perfect clock sync, the data points received at the RB are buffered and
		delivered after a minimum of `d_o` time has passed since generation time.

		Overriding the method from the super class (Algorithm).

		Args:
			g_time (list(float)): Real times when CES generates data points.
			r_time (list(float)): Real times when RB receive various data points from the CES.

		Returns:
			list(float): Real times when RB sends data points to the MP.
		"""
		answer = []
		for i in range(len(r_time)):
			curr = g_time[i] + self.d_o
			if r_time[i] > curr:
				curr = r_time[i]
			answer.append(curr)
		return answer

	def get_ordering(self, submission_time, receive_at_ob):
		"""
		Generate a total ordering of trades in which they can be executed.

		For Cloudex with perfect clock sync, the trade is ordered based on the clock sync timestamp
		after `d_i` time has passed. If the trade is delayed in network more than `d_i`, then it is
		executed as soon as it is received.

		Overriding the method from the super class (Algorithm).

		Args:
			submission_time (list(float)): Real times when trade is submitted to the RB from the MP.
			receive_at_ob (list(float)): Real times when trades are received by the OB.

		Returns:
			list(float): A total ordering of trades.
		"""
		answer = []
		for i in range(len(submission_time)):
			answer.append(max(submission_time[i] + self.d_i, receive_at_ob[i]))
		return answer

	def get_execution_time(self, ordering):
		"""
		Get the execution time of trades from a single MP.

		For Cloudex with perfect clock sync, the execution time is calculated in the same way as `ordering`
		(see `get_ordering`).

		Overriding the method from the super class (Algorithm).

		Args:
			ordering (list(float)): A total ordering of trades.

		Returns:
			list(float): Real times of execution of trades from a single MP at the CES.
		"""
		return ordering

	def run_simulation(self):
		## The environment should be set before calling this function.
		for i in range(self.number_participants):
			# Calculate the times when the RB`i` receives the data points from the CES using the one way delays.
			self.r_time_arr.append(self.get_r_time(self.g_time, self.fw_owd_arr[i]))
			# Calculate when the data point is delivered by the RB`i` to the MP`i`.
			self.d_time_arr.append(self.get_d_time(self.g_time, self.r_time_arr[i]))
			# Calculate when trades are generated by MP`i` in response to the data points received and sent to the RB`i`.
			self.submission_time_arr.append(self.get_submission_time(self.d_time_arr[i], self.response_times[i]))
			# Calculate when trades are received at the OB from RB`i`.
			self.receive_at_ob_arr.append(self.get_receive_at_ob(self.submission_time_arr[i], self.rv_owd_arr[i]))
			# Calculate the order of trades from RB`i` at the CES.
			self.ordering_arr.append(self.get_ordering(self.submission_time_arr[i], self.receive_at_ob_arr[i]))
			# Calculate the execution time of trades from RB`i` at the CES
			self.execution_time_arr.append(self.get_execution_time(self.ordering_arr[i]))
			# Calculate the latency for each trade (ignore last 25/g_step points to ensure it is within `time_range`)
			self.latency_arr.append(self.get_e2e_latency(
				self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])


