from algorithm import Algorithm

class DBO(Algorithm):
	def __init__(self, delta=0, batch_size=0, inter_batch_time=0):
		self.delta = delta
		self.batch_size = batch_size
		self.inter_batch_time = inter_batch_time
		super().__init__()

	def get_title(self):
		return "DBO({delta}|{bs}|{ibt})".format(delta = self.delta, bs = self.batch_size, ibt = self.inter_batch_time)

	def get_d_time(self, g_time, r_time):
		answer = []

		last_batch_number = int(g_time[0]/self.batch_size)
		last_batch_delivery_time = -100
		last_point_delivery_time = -100
		count_points_this_batch = 0
		for i in range(len(g_time)):
			curr_batch_number = int(g_time[i]/self.batch_size)

			if last_batch_number == curr_batch_number:
				count_points_this_batch += 1
				last_point_delivery_time = r_time[i]
			else:
				start_time_batch = max(last_point_delivery_time, last_batch_delivery_time + self.delta)
				for j in range(count_points_this_batch):
					answer.append(start_time_batch+j*self.inter_batch_time)
				count_points_this_batch = 1
				last_batch_delivery_time = start_time_batch
				last_batch_number = curr_batch_number
				last_point_delivery_time = r_time[i]

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
		answer = []
		d_time_ind = 0
		for i in range(len(submission_time)):
			while submission_time[i] >= d_time[d_time_ind] and d_time_ind < len(d_time) - 1:
				d_time_ind += 1
			if submission_time[i] < time_range - 2000:
				assert(submission_time[i] >= d_time[d_time_ind-1]), (d_time_ind, submission_time[i], submission_time[i-1], d_time[d_time_ind-2], d_time[d_time_ind-1], d_time[d_time_ind])
				assert(submission_time[i] < d_time[d_time_ind])
			answer.append((d_time_ind - 1) * time_range + submission_time[i]-d_time[d_time_ind-1])
		return answer

	def get_execution_time(self, ordering, ack_time_arr, time_range):
		answer = []
		for i in range(len(ordering)):
			x = int(ordering[i]/time_range)
			max_s  = -1
			for j in range(len(ack_time_arr)):
				max_s = max(max_s, ack_time_arr[j][x+1])
			answer.append(max_s)
		return answer

	def run_simulation(self):
		for i in range(self.number_participants):
			self.r_time_arr.append(self.get_r_time(self.g_time, self.fw_owd_arr[i]))
			self.d_time_arr.append(self.get_d_time(self.g_time, self.r_time_arr[i]))
			self.submission_time_arr.append(self.get_submission_time(self.d_time_arr[i], self.response_times[i]))
			self.receive_at_ob_arr.append(self.get_receive_at_ob(self.submission_time_arr[i], self.rv_owd_arr[i]))
			self.ordering_arr.append(self.get_ordering(self.d_time_arr[i], self.submission_time_arr[i], self.time_range))
			self.ack_time_arr.append(self.get_receive_at_ob(self.d_time_arr[i], self.rv_owd_arr[i]))

		for i in range(self.number_participants):
			self.execution_time_arr.append(self.get_execution_time(self.ordering_arr[i], self.ack_time_arr, self.time_range))
			self.latency_arr.append(self.get_e2e_latency(
              	self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])
