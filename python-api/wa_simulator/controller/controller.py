# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod # Abstract Base Class

class WAVehicleInputs:
	"""Object used to hold the inputs to the vehicle model

	The value ranges for the vehicle inputs may vary depending on the
	used vehicle model (i.e. radians vs percentages). This class is not reponsible for 
	maintaining such properties, simply should be used for passing values around.

	Args:
		steering (double, optional): steering input. Defaults to 0.0.
		throttle (double, optional): throttle input. Defaults to 0.0.
		braking (double, optional): braking input. Defaults to 0.0.
	"""
	
	def __init__(self, steering=0.0, throttle=0.0, braking=0.0):
		self.steering = steering
		self.throttle = throttle
		self.braking = braking

class WAController(ABC):
	"""Base class for a controller

	Controllers are responsible for outputing a steering, throttle and braking value.
	This is done because in real life, those are the inputs our cars will have. The 
	derived controller's (i.e. the new class that inherits from this class)
	responsibility is to take inputs from the simulation and return these values
	through the GetInputs method.

	Attributes:
		inputs (WAVehicleInputs): Inputs to the vehicle model
	"""

	def __init__(self):
		self.inputs = WAVehicleInputs()

	@abstractmethod
	def Advance(self, step):
		"""Advance the controller by the specified step

		Args:
			step (double): the time step at which the controller should be advanced
		"""
		pass

	@abstractmethod
	def Synchronize(self, time):
		"""Synchronize the controller at the specified time

		Function is primarily as a semantic separation between different functionality.
		Most of the time, all controller logic can be placed in the Advance method. ROS would
		be a good example of an element that would publish in the Synchronize method and have
		other logic in the Advance method.

		Args:
			time (double): the time at which the controller should synchronize all depends to
		"""
		pass

	def GetInputs(self):
		"""Get the vehicle inputs

		Returns:
			The input class
		"""
		return self.inputs