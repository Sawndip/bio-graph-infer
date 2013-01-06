import random
from factor import *

class Graph:
	'''
		A graph object consists of the set of interactions between nodes, 
		with a set of corresponding factor objects.

	'''


	def __init__(self, file):

		self.graph = self.parseGraph(file)

	def parseGraph(self, file):
		'''
			Store an index of (source, target) tuples to the (interaction, inference)
			type. 
		'''
		fh = None
		try:
			fh = open(file, 'r')
		except:
			raise Exception("Error: cannot open network file"+file)

		net = {}
		lineno = 1
		for line in fh:
	
			parts = line.rstrip().split("\t")
			if len(parts) != 4:
				raise Exception("Error: cannot parse network at line "+str(lineno))

			source = parts[0]
			target = parts[1]
			interaction = parts[2]
			inference = parts[3]
	
			net[(source, target)] = (interaction, inference)

		fh.close()
	
		return net
	
	def buildFactors(self):

		self.factorIndex = {}
		self.factors = {}
		factorID = 1
		for (source, target) in self.graph:
			f = UNIFORM_Factor(factorID, ((source, 3), (target, 3)))
			self.factorIndex[factorID] = (source, target)
			self.factors[factorID] = f
			factorID += 1

	def printFactors(self, file):

		fh = None
		try:
			fh = open(file, 'w')
		except:
			raise Exception("Error: cannot open factor file for writing"+file)

		fh.write(str(len(self.factors))+"\n\n")
		for fi in self.factors:
			self.factors[fi].printFactor(fh)

		fh.close()

