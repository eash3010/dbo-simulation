from dbo import DBO

class MaxRTT(DBO):
	def __init__(self):
		super().__init__()

	def get_title(self):
		return "MaxRTT"

	def get_d_time(self, g_time, r_time):
		return r_time
