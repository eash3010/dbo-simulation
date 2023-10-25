from .algorithm import Algorithm

class DirectDelivery(Algorithm):
	"""
	DirectDelivery implements the direct delivery of data with no buffering delays at RBs and OB.
	"""
	def __init__(self):
		super().__init__()

	def get_title(self):
		return "DirectDelivery"

	def get_d_time(self, r_time):
		"""
		Calculate the times when data points, received from the CES at RB, are sent to the MP.
		It assumes that the MP is very close to the RB and hence the transmission time is
		assumed 0 for simulation purposes. The results would not change if we assume some small
		bounded delay here as shown in Theorem 4.

		For Direct Delivery, the data is directly sent from the RB to the MP as soon as it is
		received at the RB.

		Overriding the method from the super class (Algorithm).

		Args:
			r_time (list(float)): Real times when RB receive various data points from the CES.

		Returns:
			list(float): Real times when RB sends data points to the MP.
		"""
		return r_time

	def get_ordering(self, receive_at_ob):
		"""
		Generate a total ordering of trades in which they can be executed.

		For Direct Delivery, the trade is ordered based on the order in which it is received. It is
		the same as timestamps when trades are received at the OB.

		Overriding the method from the super class (Algorithm).

		Args:
			receive_at_ob (list(float)): Real times when trades are received by the OB.

		Returns:
			list(float): A total ordering of trades.
		"""
		return receive_at_ob

	def get_execution_time(self, receive_at_ob):
		"""
		Get the execution time of trades from a single MP.

		For Direct Delivery, the trades are executed as they are received, without any buffering/delay. It is
		the same as timestamps when trades are received at the OB.

		Overriding the method from the super class (Algorithm).

		Args:
			receive_at_ob (list(float)): Real times when trades are received by the OB.

		Returns:
			list(float): Real times of execution of trades from a single MP at the CES.
		"""
		return receive_at_ob

	def run_simulation(self):
		## The environment should be set before calling this function.
		for i in range(self.number_participants):
			# Calculate the times when the RB`i` receives the data points from the CES using the one way delays.
			self.r_time_arr.append(self.get_r_time(self.g_time, self.fw_owd_arr[i]))
			# Calculate when the data point is delivered by the RB`i` to the MP`i`.
			self.d_time_arr.append(self.get_d_time(self.r_time_arr[i]))
			# Calculate when trades are generated by MP`i` in response to the data points received and sent to the RB`i`.
			self.submission_time_arr.append(self.get_submission_time(self.d_time_arr[i], self.response_times[i]))
			# Calculate when trades are received at the OB from RB`i`.
			self.receive_at_ob_arr.append(self.get_receive_at_ob(self.submission_time_arr[i], self.rv_owd_arr[i]))
			# Calculate the order of trades from RB`i` at the CES.
			self.ordering_arr.append(self.get_ordering(self.receive_at_ob_arr[i]))
			# Calculate the execution time of trades from RB`i` at the CES
			self.execution_time_arr.append(self.get_execution_time(self.receive_at_ob_arr[i]))
			# Calculate the latency for each trade (ignore last 25/g_step points to ensure it is within `time_range`)
			self.latency_arr.append(self.get_e2e_latency(
				self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])