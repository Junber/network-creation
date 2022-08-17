import itertools
import pygeosolve

epsilon = 0.00001

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (2, 0),
	'd': (0.5, -1),
	'y': (0.5, 1),
	'z': (1.5, 1),
}

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

problem = pygeosolve.Problem()

for name, pos in vertices.items():
	problem.add_point(name, pos[0]*distances['bc'], pos[1]*distances['bc'],)

for name1, name2 in itertools.combinations(vertices.keys(), 2):
	problem.add_line(name1 + name2, problem[name1], problem[name2])


problem.constrain_position('b')
problem.constrain_position('c')

for name, distance in distances.items():
	problem.constrain_line_length(name, distance)


result = problem.solve()
#problem.plot()
print("Success:", result.success)
if result.success:
	multiplier = 10
	positions = {vertex : (problem[vertex].x * multiplier, problem[vertex].y * multiplier) for vertex in vertices.keys()}
	print(positions)
	print(list(positions.values()))

	for name1, name2 in itertools.combinations(vertices.keys(), 2):
		edge = name1+name2
		if edge not in distances:
			print(f'{edge}: {problem[edge].length():.4f}')
		else:
			pass
			#print(f'{edge}: {problem[edge].length():.4f} should be {distances[edge]}')