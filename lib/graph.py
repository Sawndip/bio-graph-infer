

class Graph:
	'''
		A graph object consists of the set of interactions between nodes, 
		with a set of corresponding factor objects.

	'''


	def __init__(self, file):

		self.graph = self.parseGraph(file)

	def parseGraph(file):
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
	
