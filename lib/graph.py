import random
from factor import *
import copy

class Graph:
	'''
		A graph object consists of the set of interactions between nodes, 
		with a set of corresponding factor objects.

	'''

	def __init__(self, file):

		self.graph = self.parseGraph(file)

	def mapNodes(self, node_list):
		var_numbers = []
		idx = -1
		included_index = []
		for n in node_list:

			# always update, and start at zero
			idx += 1
			# if we have an observation not in the graph...
			if n not in self.nodeMap:
				continue
			# we need to track the index of this deletion, in order to remove 
			# the data values associataed with it
		
			var_numbers.append(self.nodeMap[n])

			# these data values are included	
			included_index.append(idx)

		return (var_numbers, included_index)

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

			source = parts[0]
			target = parts[1]
			interaction = parts[2]
			inference = None
			if len(parts) == 4:
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

	def clone(self):

		graph_hash = copy.copy(self.graph)

	def permuteEdgeTypes(self):
		"""
		Perform random swaps of edge interactions
		"""
		permuted_graph = copy.copy(self)
		# swap about half the edges
		i = len(self.graph)/2
		while i > 0:
			# swap 
			sourceA, targetA = random.choice(permuted_graph.graph.keys())
			iTypeA, emA = permuted_graph.graph[(sourceA, targetA)]
			sourceB, targetB = random.choice(permuted_graph.graph.keys())
			iTypeB, emB = permuted_graph.graph[(sourceB, targetB)]
			permuted_graph.graph[(sourceA, targetA)] = (iTypeB, emB)
			permuted_graph.graph[(sourceB, targetB)] = (iTypeA, emA)

			i -= 1

		# return a new graph object		
		return permuted_graph

	def permuteEdges(self):
		"""
		Perform random swaps of edge interactions
		"""
		permuted_graph = copy.copy(self)
		# swap about half the edges
		i = len(self.graph)/2
		while i > 0:
			# swap edge targets
			sourceA, targetA = random.choice(permuted_graph.graph.keys())
			iTypeA, emA = permuted_graph.graph[(sourceA, targetA)]
			sourceB, targetB = random.choice(permuted_graph.graph.keys())
			iTypeB, emB = permuted_graph.graph[(sourceB, targetB)]

			# can't be the same random choice, obviously...
			if sourceA == sourceB or targetA == targetB:
				continue

			# add edges
			permuted_graph.graph[(sourceA, targetB)] = (iTypeA, emA)
			permuted_graph.graph[(sourceB, targetA)] = (iTypeB, emB)

			del permuted_graph.graph[(sourceA, targetA)]
			del permuted_graph.graph[(sourceB, targetB)]

			i -= 1

		# return a new graph object		
		return permuted_graph
	
	def buildFactors(self, shared):

		self.factorIndex = {}
		self.factors = {}

		emSteps = set()

		shared_steps = {}
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
			elif iType == "-||":
				f = P_Factor(factorID, ((source, 3), (target, 3)))
			elif iType == "->>":
				#f = TM_Factor(factorID, ((source, 3), (target, 3)))
				f = AC_Factor(factorID, ((source, 3), (target, 3)))
			elif iType == "-":
				f = UNIFORM_Factor(factorID, ((source, 3), (target, 3)))
			else:
				raise Exception("Unsupported interaction type!"+iType)

			# choose the EM operation to perform
			if em == "E" or shared is False:
				# learn this factor
				emStep = EMStep({
					'factor_id' : factorID,
					'depends_on' : (source, target),
					'var_dim' : 3,
					'total_dim' : 9
				})
				emSteps.add(emStep)
			elif em.startswith("S"):
				# this is a shared factor: get the UID for the shared EM params
				uid = em
				if uid not in shared_steps:
					shared_steps[uid] = []
				shared_steps[uid].append((factorID, source, target))	
			
			self.factorIndex[(source, target)] = factorID
			self.factors[factorID] = f
			factorID += 1

		for shared in shared_steps:
			SEMStep = SharedEMStep({
				'ids' : shared_steps[shared],
				'var_dim' : 3,
				'total_dim' : 9
			})
			emSteps.add(SEMStep)
		# add emSteps selected
		self.emSteps = EMSet(emSteps)

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
		new_header, retained_indexes = self.mapNodes(self.obs.header)
		self.obs.setHeader(new_header)
		self.obs.retained_indexes = retained_indexes

		# print to the output file 
		self.obs.printHeader(fh)
		self.obs.printSamples(fh)
		fh.close()

	def printEM(self, file):
		self.emSteps.printToFile(file)

	def addSampleLL(self, fh):
		self.obs.addSampleLL(fh)

	def printSampleLL(self):
		self.obs.printSampleLL()

	def meanSampleLL(self):
		return self.obs.meanLL()
	
	def getSampleLLS(self):
		return self.obs.getSampleLLS()
		
class SharedEMStep:

	def __init__(self, opts):
		'''
			opts:
			 = {
				'ids' : tuple array of (id, source_var, target_var)
				'var_dim' : number of states for each observed variable
				'total_dim' : number of total possible states
				}
		'''

		self.var_dim = opts['var_dim']
		self.total_dim = opts['total_dim']
		self.factors = opts['ids']

	def printEM(self, fh):

		fh.write("CondProbEstimation [target_dim="+str(self.var_dim)+",total_dim="+str(self.total_dim)+",pseudo_count=1]\n")
		# for now, allow only a single factor (no shared params)
		fh.write(str(len(self.factors))+"\n")
		for (fid, s_v, t_v) in self.factors:
			fh.write(str(fid)+" "+str(s_v)+" "+str(t_v)+"\n")

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
		self.samples = {}
		self.sample_order = []
		for line in fh:
			parts = line.rstrip().split("\t")
			if self.header is None:
				self.header = parts[1:]
				continue

			if line.isspace():
				continue

			# indexed by sample name: values are kept in the right order
			self.samples[parts[0]] = parts[1:]
			self.sample_order.append(parts[0])

	def addSampleLL(self, fh):
		'''
			Parse and ordered list of sample-specific log likelihood scores
		'''
		self.ssl = {}
		self.sample_labels = {}
		idx = 0
		for line in fh:
			val = None
			try: 
				desc, logZ, labelProbTable, labelStateCall = line.rstrip().split("\t")
				val = float(logZ)
				labelState = int(labelStateCall)
			except:
				continue
			self.ssl[self.sample_order[idx]] = val
			self.sample_labels[self.sample_order[idx]] = (labelState, labelProbTable)
			idx += 1

	def getSampleLLS(self):

		sample_lls = []
		for sample in self.sample_order:
			sample_lls.append(self.ssl[sample])

		return sample_lls

	def printSampleLL(self):
		'''
			Parse and ordered list of sample-specific log likelihood scores
		'''
		for sample in self.sample_order:
			print sample+"\t"+str(self.ssl[sample])+"\t"+"\t".join([str(v) for v in self.sample_labels[sample]])

	def meanLL(self):
		'''
			Parse and ordered list of sample-specific log likelihood scores
		'''
		sum = 0
		for sample in self.sample_order:

			if sample not in self.ssl:
				continue

			sum += self.ssl[sample]
		
		return sum/float(len(self.sample_order))


	def setHeader(self, header):
		self.header = header

	def printHeader(self, fh):
		fh.write("\t".join([str(i) for i in self.header])+"\n\n")

	@staticmethod
	def dataSubset(indexes, values):
		'''
			Return the indexed values that have a subscript 
		'''
		retained = []
		for i in indexes:
			retained.append(values[i])
			
		return retained

	def printSamples(self, fh):
		'''
			Print out samples in the order tracked by self.sample_order 
		'''
		for sample in self.sample_order:
			fh.write("\t".join([str(self.valueMap[int(v)]) for v in Obs.dataSubset(self.retained_indexes, self.samples[sample])])+"\n")
