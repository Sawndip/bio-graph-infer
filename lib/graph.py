import random
from factor import *

class Graph:
	'''
		A graph object consists of the set of interactions between nodes, 
		with a set of corresponding factor objects.

	'''

	def __init__(self, file):

		self.graph = self.parseGraph(file)

	def mapNodes(self, node_list):
		var_numbers = []
		for n in node_list:
			var_numbers.append(self.nodeMap[n])
		return var_numbers

	def addObs(self, observations):
		# add the observation (Obs) object here
		self.obs = observations

	def nodeID2Name(self, id):
		return self.reverseNodeMap[id]
	
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

		# node mappings to numerical values: libDAI can only handle numbers
		# so we need to build a mapping here
		nodeIDX = 0
		# map[name] = index
		self.nodeMap = {}
		# map[index] = name
		self.reverseNodeMap = {}

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

			if source not in self.nodeMap:
				self.nodeMap[source] = nodeIDX
				self.reverseNodeMap[nodeIDX] = source
				nodeIDX += 1
			if target not in self.nodeMap:
				self.nodeMap[target] = nodeIDX
				self.reverseNodeMap[nodeIDX] = target
				nodeIDX += 1
	
			net[(self.nodeMap[source], self.nodeMap[target])] = (interaction, inference)

		fh.close()
	
		return (net)
	
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
			self.factorIndex[(source, target)] = factorID
			self.factors[factorID] = f
			factorID += 1

	def getFactor(self, tuple):
		'''
			get the factor that represents the connection between these variables
		'''
		if tuple not in self.factorIndex:
			return None

		return self.factors[self.factorIndex[tuple]]

	def getMI(self, tuple):

		factor = self.getFactor(tuple)
		if not factor:
			return None

		# only 2 variables per factor for now: use both
		return factor.computeMI((0,1))

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

	def printOBS(self, file):

		fh = None
		try:
			fh = open(file, 'w')
		except:
			raise Exception("Error: cannot open observation file for writing"+file)

		# fix the observation header to use indexed variable numbers, corresponding to
		# the factor graph derived from the pathway file
		new_header = self.mapNodes(self.obs.header)
		self.obs.setHeader(new_header)

		# print to the output file 
		self.obs.printHeader(fh)
		self.obs.printSamples(fh)
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


class Obs:

	def __init__(self, file):
		fh = None
		try:
			fh = open(file, 'r')
		except:
			raise Exception("Error: cannot open observation file "+file)

		self.valueMap = {-1:0, 0:1, 1:2} 
		self.header = None
		self.samples = []	
		for line in fh:
			parts = line.rstrip().split("\t")
			if self.header is None:
				self.header = parts
				continue

			if line.isspace():
				continue

			self.samples.append(parts)

	def setHeader(self, header):
		self.header = header

	def printHeader(self, fh):
		fh.write("\t".join([str(i) for i in self.header])+"\n\n")

	def printSamples(self, fh):
		for sample in self.samples:
			fh.write("\t".join([str(self.valueMap[int(v)]) for v in sample])+"\n")
