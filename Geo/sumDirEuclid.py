from geoBase import solve

epsilon = 0.00001

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (2, 0),
	'y': (0.5, 1),
	'z': (1.5, 1),
}

distances = {
	'ab': 1.14,
	'bc': 1,
	'yz': 1-2*epsilon,
	'ay': 1.96,
	'by': 2-epsilon,
	'bz': 2,
	'cz': 2+epsilon,
}

solve(vertices, distances, ['b', 'c'])