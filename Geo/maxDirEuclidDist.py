from geoBase import solve

distances = {
	'ab': 1.6,
	'bc': 1.2,
	'yz': 1,
	'ay': 1.8,
	'by': 2.2,
	'bz': 2.4,
	'cz': 2.6,
}

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (1 + distances['bc'], 0),
	'y': (0.5, 1),
	'z': (1.5, 1),
}


solve(vertices, distances, ['b', 'c'])