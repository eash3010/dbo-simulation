from .algorithm import Algorithm

class DBO(Algorithm):
	"""
	DBO class implements the pacing and the ordering functions for the DBO algorithms from the
	paper. The data points generated at the CES are delivered to the RB. RB paces and batches
	the data and delivers it accordingly to the MPs. The RBs also send ACKs to the CES. The MPs
	respond with a trade for each data point which is submitted to the RB. RBs timestamp and
	forward trades to the OB which orders them and asks CES to execute them accordingly.
	"""
	def __init__(self, delta=0, batch_size=0, inter_batch_time=0):
		self.delta = delta
		self.batch_size = batch_size
		self.inter_batch_time = inter_batch_time
		super().__init__()

	def get_title(self):
		return "DBO({delta}|{bs}|{ibt})".format(delta = self.delta, bs = self.batch_size, ibt = self.inter_batch_time)

	def get_d_time(self, g_time, r_time):
		"""
		Calculate the times when data points, received from the CES at RB, are sent to the MP.
		It assumes that the MP is very close to the RB and hence the transmission time is
		assumed 0 for simulation purposes. The results would not change if we assume some small
		bounded delay here as shown in Theorem 4.

		For DBO, the data points received at the RB are buffered and batched based on `batch_size`.
		The batches are delivered with inter-batch time as >=`delta`. See LRTF and Section 5 in the
		paper.

		Overriding the method from the super class (Algorithm).

		Args:
			g_time (list(float)): Real times when CES generates data points.
			r_time (list(float)): Real times when RB receive various data points from the CES.

		Returns:
			list(float): Real times when RB sends data points to the MP.
		"""
		answer = []

		last_batch_number = int(g_time[0]/self.batch_size)
		last_batch_delivery_time = -100
		last_point_delivery_time = -100
		count_points_this_batch = 0
		for i in range(len(g_time)):
			# Batch the data based on batch_size
			curr_batch_number = int(g_time[i]/self.batch_size)
			if last_batch_number == curr_batch_number:
				count_points_this_batch += 1
				last_point_delivery_time = r_time[i]
			else:
				# RB delivers the batch to MP when all data points in a batch are received at the RB
				# or the time since last batch was delivered is delta, whichever is later.
				start_time_batch = max(last_point_delivery_time, last_batch_delivery_time + self.delta)
				for j in range(count_points_this_batch):
					answer.append(start_time_batch+j*self.inter_batch_time)
				count_points_this_batch = 1
				last_batch_delivery_time = start_time_batch
				last_batch_number = curr_batch_number
				last_point_delivery_time = r_time[i]

		# Deliver last batch of data points
		start_time_batch = max(last_point_delivery_time, last_batch_delivery_time + self.delta)
		for j in range(count_points_this_batch):
			answer.append(start_time_batch + j*self.inter_batch_time)
		count_points_this_batch = 1
		last_batch_delivery_time = start_time_batch
		last_batch_number = curr_batch_number
		last_point_delivery_time = r_time[i]

		assert(len(g_time) == len(answer))
		return answer

	def get_ordering(self, d_time, submission_time, time_range):
		"""
		Generate a total ordering of trades in which they can be executed.

		For DBO, the trade is ordered based on the delivery clock time. The delivery clock timestamp
		can be calculated using the delivery time (`d_time`) and the submission time (`submission_time`).
		The ordering here for delivery clock (x,t) is defined as (x*time_range + t). This enforces the
		lexicographic sorting for the tuple (x,t).

		The last few data points are removed to not go beyond the time_range.

		Overriding the method from the super class (Algorithm).

		Args:
			d_time (list(float)): Real times when RB sends data points to the MP.
			submission_time (list(float)): Real times when trade is submitted to the RB from the MP.
			time_range (float): The time horizon being simulated.

		Returns:
			list(float): A total ordering of trades.
		"""
		answer = []
		d_time_ind = 0
		for i in range(len(submission_time)):
			while submission_time[i] >= d_time[d_time_ind] and d_time_ind < len(d_time) - 1:
				d_time_ind += 1
			if submission_time[i] < time_range - 2000:
				assert(submission_time[i] >= d_time[d_time_ind-1]), (d_time_ind, submission_time[i], submission_time[i-1], d_time[d_time_ind-2], d_time[d_time_ind-1], d_time[d_time_ind])
				assert(submission_time[i] < d_time[d_time_ind])
			# Delivery clock (x,t): x is (d_time_ind-1); t is (submission_time of trade - d_time of prev data point);
			answer.append((d_time_ind - 1) * time_range + submission_time[i]-d_time[d_time_ind-1])
		return answer

	def get_execution_time(self, ordering, ack_time_arr, time_range):
		"""
		Get the execution time of trades from a single MP.

		For DBO, the trades are executed based on the delivery clock timestamps and when
		the ACKs are received by the CES. Before a trade is executed, CES ensures that
		delivery clocks on all RBs has reached the DC timestamp of the trade at least. This
		is ensured using ACKs from all RBs.

		Overriding the method from the super class (Algorithm).

		Args:
			ordering (list(float)): A total ordering of trades.
			ack_time_arr (list(float)): Real times when acks are received from all MPs.
			time_range (float): The time horizon being simulated.

		Returns:
			list(float): Real times of execution of trades from a single MP at the CES.
		"""
		answer = []
		for i in range(len(ordering)):
			x = int(ordering[i]/time_range)
			max_s  = -1
			for j in range(len(ack_time_arr)):
				max_s = max(max_s, ack_time_arr[j][x+1])
			answer.append(max_s)
		return answer

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
			self.ordering_arr.append(self.get_ordering(self.d_time_arr[i], self.submission_time_arr[i], self.time_range))
			# After each data point is delivered to the MP`i`, RB`i` sends an ACK to the CES.
			# Calculate the times when the ACK reaches the CES.
			self.ack_time_arr.append(self.get_receive_at_ob(self.d_time_arr[i], self.rv_owd_arr[i]))

		for i in range(self.number_participants):
			# Calculate the execution time of trades from RB`i` at the CES
			self.execution_time_arr.append(self.get_execution_time(self.ordering_arr[i], self.ack_time_arr, self.time_range))
			# Calculate the latency for each trade (ignore last 25/g_step points to ensure it is within `time_range`)
			self.latency_arr.append(self.get_e2e_latency(
				self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])
