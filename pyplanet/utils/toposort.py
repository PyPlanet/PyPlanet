def toposort(graph):
	"""Perform a topological sort on a graph
	This returns an ordering of the nodes in the graph that places all
	dependencies before the nodes that require them.
	Args:
		graph: an adjacency dict {node1: [dep1, dep2], node2: [dep1, dep3]}
	Returns:
		A list of ordered nodes
	"""
	result = []
	used = set()

	def use(v, top):
		if v in used:
			return

		for parent in graph.get(v, []):
			if parent is top:
				raise ValueError("graph is cyclical through", parent)

			use(parent, v)

		used.add(v)
		result.append(v)

	for v in graph:
		use(v, v)

	return result
