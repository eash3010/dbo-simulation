from .dbo import DBO

class MaxRTT(DBO):
	"""
	MaxRTT calculates the bounds on end-to-end latency to achieve Response Time Fairness.
	To minimize delay, there is no buffering at the RBs. At the CES, the ordering algorithm
	is the same as DBO for simulation pursposes as both require to wait till ACKs/trades from
	all MPs are received at the CES (see Section 4.2.1).
	"""
	def __init__(self):
		super().__init__()

	def get_title(self):
		return "MaxRTT"

	def get_d_time(self, g_time, r_time):
		return r_time
