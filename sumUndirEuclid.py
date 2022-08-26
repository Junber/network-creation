import itertools
from re import X
import pygeosolve

epsilon = 0

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (2, 0),
	'y': (0.5, 2),
	'z': (1.5, 2),

	'w': (0.5,2.5),
	'x': (1.5,2.5),
}

distances = {
	'ab': 1.14,
	'bc': 1,
	'yz': 1-2*epsilon,
	'ay': 1.96,
	'by': 2-epsilon,
	'bz': 2,
	'cz': 2+epsilon,

	'yw' : 0.4,
	'zw' : 1.2,
	'yx' : 1.2,
	'zx' : 0.4,
}

while True:
	problem = pygeosolve.Problem()

	for name, pos in vertices.items():
		problem.add_point(name, pos[0], pos[1])

	for name1, name2 in itertools.combinations(vertices.keys(), 2):
		problem.add_line(name1 + name2, problem[name1], problem[name2])


	problem.constrain_position('b')
	problem.constrain_position('c')

	for name, distance in distances.items():
		problem.constrain_line_length(name, distance)


	result = problem.solve()

	if problem["aw"].length() < problem["ay"].length() or problem["ax"].length() < problem["az"].length():
		print("Retrying...")
		continue
	#problem.plot()
	print("Success:", result.success)
	multiplier = 1
	positions = {vertex : (problem[vertex].x * multiplier, problem[vertex].y * multiplier) for vertex in vertices.keys()}
	print(positions)
	print(positions.values())

	for name1, name2 in itertools.combinations(vertices.keys(), 2):
		edge = name1+name2
		if edge not in distances:
			print(f'{edge}: {problem[edge].length():.4f}')
	
	maxi = 0
	for v1 in 'abc':
		for v2 in 'wx':
			x = (0.6 * problem[v1+v2].length()) / (min(problem[v1+'y'].length() + problem['y'+v2].length(), problem[v1+'z'].length() + problem['z'+v2].length()) / problem[v1+v2].length() - 1)
			print(v1, v2, x)
			maxi = max(maxi,x)
	print("Max:", maxi)
	break