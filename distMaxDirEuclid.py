import itertools
import pygeosolve

epsilon = 0.00001

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
print(list(positions.values()))

for name1, name2 in itertools.combinations(vertices.keys(), 2):
	edge = name1+name2
	if edge not in distances:
		print(f'{edge}: {problem[edge].length():.2f}')