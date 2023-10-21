from algorithm import Algorithm

class DirectDelivery(Algorithm):
	def __init__(self):
		super().__init__()

	def get_title(self):
		return "DirectDelivery"

	def get_d_time(self, r_time):
		return r_time

	def get_ordering(self, receive_at_ob):
		return receive_at_ob

	def get_execution_time(self, receive_at_ob):
		return receive_at_ob

	def run_simulation(self):
		for i in range(self.number_participants):
			self.r_time_arr.append(self.get_r_time(self.g_time, self.fw_owd_arr[i]))
			self.d_time_arr.append(self.get_d_time(self.r_time_arr[i]))
			self.submission_time_arr.append(self.get_submission_time(self.d_time_arr[i], self.response_times[i]))
			self.receive_at_ob_arr.append(self.get_receive_at_ob(self.submission_time_arr[i], self.rv_owd_arr[i]))
			self.ordering_arr.append(self.get_ordering(self.receive_at_ob_arr[i]))
			self.execution_time_arr.append(self.get_execution_time(self.receive_at_ob_arr[i]))
			self.latency_arr.append(self.get_e2e_latency(
              	self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])