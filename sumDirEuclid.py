import itertools
import pygeosolve

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
#problem.plot()
print("Success:", result.success)
multiplier = 10
positions = {vertex : (problem[vertex].x * multiplier, problem[vertex].y * multiplier) for vertex in vertices.keys()}
print(positions)

for name1, name2 in itertools.combinations(vertices.keys(), 2):
	edge = name1+name2
	if edge not in distances:
		print(f'{edge}: {problem[edge].length():.2f}')