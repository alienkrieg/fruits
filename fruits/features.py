import numpy as np
from copy import copy
import collections

class FeatureFilter:
	"""Class FeatureFilter
	
	A FeatureFilter object is used to extract a single number out of an
	multidimensional numpy array.
	"""
	def __init__(self, name:str=""):
		self._name = name
		self._args = ()
		self._kwargs = {}
		self._func = None

	def set_function(self, f):
		if not callable(f):
			raise TypeError("Cannot set non-callable object as function")
		self._func = f

	@property
	def name(self) -> str:
		return self._name

	@name.setter
	def name(self, name:str):
		self._name = name

	def __repr__(self) -> str:
		out = "FeatureFilter('"+self._name+"'"
		if self._args:
			out += ",".join(self._args)
		if self._kwargs:
			out += ","+",".join([str(x)+"="+str(self._kwargs[x]) 
								 for x in self._kwargs])
		out += ")"
		return out
	
	def __call__(self, *args, **kwargs):
		if args:
			if (not isinstance(args, collections.Iterable) or
				isinstance(args, str)):
				self._args = list(args)
			else:
				self._args = args
		self._kwargs = kwargs
		return copy(self)

	def __copy__(self):
		ff = FeatureFilter(self.name)
		ff._args = self._args
		ff._kwargs = self._kwargs
		ff.set_function(self._func)
		return ff
		
	def filter(self, X:np.ndarray):
		if self._func is None:
			raise RuntimeError("No function specified")
		X = np.atleast_2d(X)
		return self._func(X, *self._args, **self._kwargs)

def _ppv(X:np.ndarray,
		 quantile:float=0.5,
		 constant:bool=False,
		 sample_size:int=0.05) -> np.ndarray:
	if constant:
		ref_value = quantile
	else:
		if not 0<quantile<1:
			raise ValueError("If 'constant' is set to False, quantile has "
							 "to be a value between 0 and 1")
		selection = np.random.choice(np.arange(len(X)),
									 size=int(sample_size*len(X)))
		ref_value = np.quantile(np.array([X[i] for i in selection]).flatten(),
								quantile)
	result = np.zeros(len(X))
	for i in range(len(X)):
		result[i] = np.sum(X[i]>=ref_value)/len(X[i])
	return result

PPV = FeatureFilter("proportion of positive values")
PPV.set_function(_ppv)

def _max(X:np.ndarray):
	return np.max(X, axis=1)

MAX = FeatureFilter("maximal value")
MAX.set_function(_max)

def _min(X:np.ndarray):
	return np.min(X, axis=1)

MIN = FeatureFilter("minimal value")
MIN.set_function(_min)