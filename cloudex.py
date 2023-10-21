from algorithm import Algorithm

class Cloudex(Algorithm):
	def __init__(self, d_o, d_i):
		self.d_o = d_o
		self.d_i = d_i
		super().__init__()

	def get_title(self):
		return "Cloudex({d_o}|{d_i})".format(d_o = self.d_o, d_i = self.d_i)

	def get_d_time(self, g_time, r_time):
		answer = []
		for i in range(len(r_time)):
			curr = g_time[i] + self.d_o
			if r_time[i] > curr:
				curr = r_time[i]
			answer.append(curr)
		return answer

	def get_ordering(self, submission_time, receive_at_ob):
		answer = []
		for i in range(len(submission_time)):
			answer.append(max(submission_time[i] + self.d_i, receive_at_ob[i]))
		return answer

	def get_execution_time(self, ordering):
		return ordering

	def run_simulation(self):
		for i in range(self.number_participants):
			self.r_time_arr.append(self.get_r_time(self.g_time, self.fw_owd_arr[i]))
			self.d_time_arr.append(self.get_d_time(self.g_time, self.r_time_arr[i]))
			self.submission_time_arr.append(self.get_submission_time(self.d_time_arr[i], self.response_times[i]))
			self.receive_at_ob_arr.append(self.get_receive_at_ob(self.submission_time_arr[i], self.rv_owd_arr[i]))
			self.ordering_arr.append(self.get_ordering(self.submission_time_arr[i], self.receive_at_ob_arr[i]))
			self.execution_time_arr.append(self.get_execution_time(self.ordering_arr[i]))
			self.latency_arr.append(self.get_e2e_latency(
              	self.g_time, self.execution_time_arr[i], self.response_times[i])[:(-int((25.0/self.g_step) + 1))])


