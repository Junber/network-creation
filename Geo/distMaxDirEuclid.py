from geoBase import solve

distances = {
	'ab': 2,
	'bc': 1.2,
	'yz': 0.8,
	'ay': 2.2,
	'by': 2.2,
	'bz': 2.6,
	'cz': 3,
}

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (1+distances['bc'], 0),
	'y': (0.5, 1),
	'z': (1.5, 1),
}

solve(vertices, distances, ['b', 'c'])