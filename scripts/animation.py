class Animation:
	def __init__(self, images, image_duration=5, loop=True):
		self.images = images
		# How many frames we want each image to show.
		self.image_duration = image_duration
		self.frame = 0
		self.loop = loop
		self.done = False
		self.max_frame = self.image_duration * len(self.images)


	def copy(self):
		return Animation(self.images, self.image_duration, self.loop)

	
	def current_frame_image(self):
		return self.images[int(self.frame / self.image_duration)]


	def update(self):
		if self.loop:
			self.frame = (self.frame + 1) % self.max_frame
		else:
			self.frame = min(self.frame + 1, self.max_frame - 1)
			if self.frame >= self.max_frame - 1:
				self.done = True
