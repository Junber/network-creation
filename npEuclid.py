import itertools
import pygeosolve

epsilon = 0.00001

vertices = {
	'u': (0, 0),
	'v': (3, 0),
	's': (1, 3),
	'x': (4, 1),
}

distances = {
	'uv': 6,
	
	'us': 9,
	'vs': 7,

	'ux': 17,
	'sx': 12,
}

problem = pygeosolve.Problem()

for name, pos in vertices.items():
	problem.add_point(name, pos[0], pos[1])

for name1, name2 in itertools.combinations(vertices.keys(), 2):
	problem.add_line(name1 + name2, problem[name1], problem[name2])


problem.constrain_position('u')
problem.constrain_position('v')

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