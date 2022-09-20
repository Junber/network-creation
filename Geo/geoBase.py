import itertools
import pygeosolve


def solve(vertices: dict, distances: dict, pinned_vertices: list, check_function = None) -> pygeosolve.Problem:
	problem = pygeosolve.Problem()

	for name, pos in vertices.items():
		problem.add_point(name, pos[0], pos[1])

	for name1, name2 in itertools.combinations(vertices.keys(), 2):
		problem.add_line(name1 + name2, problem[name1], problem[name2])


	for vertex in pinned_vertices:
		problem.constrain_position(vertex)

	for name, distance in distances.items():
		problem.constrain_line_length(name, distance)


	result = problem.solve()
	print("Success:", result.success)
	if result.success:
		if check_function and not check_function(problem):
			print("Retrying...")
			return solve(vertices, distances, pinned_vertices, check_function)
		
		#problem.plot()
		
		multiplier = 10
		positions = {vertex : (problem[vertex].x * multiplier, problem[vertex].y * multiplier) for vertex in vertices.keys()}
		print(positions)
		print(list(positions.values()))

		for name1, name2 in itertools.combinations(vertices.keys(), 2):
			edge = name1+name2
			if edge not in distances:
				print(f'{edge}: {problem[edge].length():.2f}')

		for name1, name2 in itertools.combinations(vertices.keys(), 2):
			edge = name1+name2
			if edge in distances:
				print(f'{edge}: {problem[edge].length():.4f} should be {distances[edge]}')
	
	return problem