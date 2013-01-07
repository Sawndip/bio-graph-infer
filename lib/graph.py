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

		emSteps = set()

		# the factors in the FG file are given an index based on the order,
		# and this step will make sure the EM factor ids are in the same order
		factorID = 0
		for (source, target) in self.graph:
			iType, em = self.graph[(source, target)]
			f = None
			# choose the factors (the prior) based on observed type of interaction
			if iType == "->":
				f = AC_Factor(factorID, ((source, 3), (target, 3)))
			elif iType == "-|":
				f = IA_Factor(factorID, ((source, 3), (target, 3)))
			else:
				raise Exception("Unsupported interaction type!")

			# choose the EM operation to perform
			if em == "E":
				# learn this factor
				emStep = EMStep({
					'factor_id' : factorID,
					'depends_on' : (source, target),
					'var_dim' : 3,
					'total_dim' : 9
				})
				emSteps.add(emStep)

			
			self.emSteps = EMSet(emSteps)
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

	def printEM(self, file):
		self.emSteps.printToFile(file)

class EMStep:

	def __init__(self, opts):
		'''
			opts:
			 = {
				'factor_id' : the id of the factor in the graph
				'depends_on' : the ids of the observed variables the factor depends on
				'var_dim' : number of states for each observed variable
				'total_dim' : number of total possible states
				}
		'''

		self.factor_id = opts['factor_id']
		self.depends_on = opts['depends_on']
		self.var_dim = opts['var_dim']
		self.total_dim = opts['total_dim']


	def printEM(self, fh):

		fh.write("CondProbEstimation [target_dim="+str(self.var_dim)+",total_dim="+str(self.total_dim)+",pseudo_count=1]\n")
		# for now, allow only a single factor (no shared params)
		fh.write("1\n")
		fh.write(str(self.factor_id)+" "+" ".join([str(i) for i in self.depends_on])+"\n")


class EMSet:


	def __init__(self, emSteps):
		self.steps = emSteps

	def printToFile(self, file):
		fh = None
		try:
			fh = open(file, 'w')
		except:
			raise Exception("Error: cannot open factor file for writing"+file)

		# only a single maximization step supported for now
		fh.write("1\n\n")

		# print steps to file
		fh.write(str(len(self.steps))+"\n")
		for step in self.steps:
			step.printEM(fh)			
		fh.close()	
