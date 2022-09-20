from geoBase import solve

distances = {
	'uv': 6,
	
	'us': 9,
	'vs': 7,

	'ux': 17,
	'sx': 12,
}

vertices = {
	'u': (0, 0),
	'v': (distances['uv'], 0),
	's': (1, 3),
	'x': (4, 1),
}

solve(vertices, distances, ['u', 'v'])