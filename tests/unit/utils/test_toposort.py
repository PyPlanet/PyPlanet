from pyplanet.utils import toposort


def test_toposort():
	dep_tree = {
		'node_root': [],
		'node_1': ['node_root', 'node_3', 'node_2'],
		'node_2': ['node_root'],
		'node_3': ['node_2']
	}
	order = toposort.toposort(dep_tree)
	assert order == ['node_root', 'node_2', 'node_3', 'node_1']

	dep_tree = {
		'node_root': [],
		'node_1': ['node_root', 'node_3', 'node_2'],
		'node_2': ['node_root'],
		'node_3': ['node_2', 'node_1']
	}
	cyclical = False
	try:
		toposort.toposort(dep_tree)
	except ValueError as e:
		if 'graph is cyclical through' in str(e):
			cyclical = True

	assert cyclical is True
