from geoBase import solve

distances = {
	'ab': 42,
	'bc': 79,
	'yz': 42,
	'ay': 42,
	'by': 42,
	'bz': 81,
	'cz': 80,
	'bd': 42,
	'dz': 100,
}

vertices = {
	'a': (0, 0),
	'b': (80, 0),
	'c': (80 + distances['bc'], 0),
	'd': (40, -80),
	'y': (40, 80),
	'z': (120, 80),
}

solve(vertices, distances, ['b', 'c'])