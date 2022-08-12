import itertools
from ortools.sat.python import cp_model
import networkx as nx
import matplotlib.pyplot as plt

var_upper_bound = 100000
model : cp_model.CpModel = None

def mult(*args):
	mult.counter += 1 
	var = model.NewIntVar(1, var_upper_bound * var_upper_bound, f'mult{mult.counter}')
	model.AddMultiplicationEquality(var, args)
	return var
mult.counter = 0

def name(a,b):
	if a < b:
		return str(a)+str(b)
	return str(b)+str(a)

def var_names(n):
	for v1 in range(n):
		for v2 in range(v1 + 1, n):
			yield name(v1, v2)

def draw_graph(graph, positions):
	plt.figure()
	nx.draw(graph, pos = positions, with_labels=True)
	nx.draw_networkx_edge_labels(graph, edge_labels={(u,v) : l for (u,v,l) in graph.edges.data('length')}, pos = positions, label_pos = 0.3)



def main():
	for choices in itertools.product([True, False], repeat=2):
		global model
		model = cp_model.CpModel()

		alpha_mult = 10

		n = 7
		vars = {}
		for v in var_names(n):
			vars[v] = model.NewIntVar(1, var_upper_bound, v)
		
		t = model.NewIntVar(1, var_upper_bound, 't')

		good_paths = [
			"51", "512", "563", "523", "5674",
			"651", "652", "673", "674",
			"7651", "762", "732", ""
		]

		for path in good_paths:
			length = 0
			end = path[-1]
			for i in range(len(path) - 1):
				length += vars[name(path[i], path[i+1])]

			#Stretch at most t
			model.Add(length <= mult(t,vars[name(path[0], end)]))

			#Path is greedy
			for i in range(len(path) - 2):
				print(name(path[i], end), ">", name(path[i+1], end))
				model.Add(vars[name(path[i], end)] > vars[name(path[i+1], end)])

		
		bad_paths = [
			"30146", "3576",
			"53201", "53641", "57641"
		]
		for path in bad_paths:
			length = 0
			end = path[-1]
			for i in range(len(path) - 1):
				length += vars[name(path[i], path[i+1])]

			#Stretch above t
			model.Add(length > mult(t,vars[name(path[0], end)]))

		#metric
		objective = 0
		for v1 in range(n):
			for v2 in range(v1+1, n):
				diffs = [2]
				for middle in range(n):
					if middle != v1 and middle != v2:
						diff = model.NewIntVar(1, var_upper_bound, str(v1)+str(v2)+str(middle))
						diffs.append(diff)
						objective += diff
						model.Add(vars[name(v1, v2)] + diff - 1 == vars[name(v1, middle)] + vars[name(middle, v2)])
				# min_diff = model.NewIntVar(1, var_upper_bound, str(v1)+str(v2)+"diff")
				# model.AddMinEquality(min_diff, diffs)
				# objective += min_diff


		objective *= 1000
		for v in var_names(n):
			objective += vars[v]
		model.Minimize(objective)


		# Creates a solver and solves the model.
		solver = cp_model.CpSolver()
		status = solver.Solve(model)

		if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
			print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')

			for v in var_names(n):
				print(f'{v} = {solver.Value(vars[v])}')
			print(f'\nt = {solver.Value(t)}')


			distance_mult = 1

			all_distance_graph = nx.Graph()
			metric_distance_graph = nx.Graph()
			distance_graph = nx.Graph()
			for v1 in range(n):
				for v2 in range(v1+1, n):
					trivial_edge = False
					for middle in range(n):
						if middle != v1 and middle != v2 and solver.Value(vars[name(v1, v2)]) == solver.Value(vars[name(v1, middle)]) + solver.Value(vars[name(middle, v2)]):
							trivial_edge = True
							break
					if not trivial_edge:
						metric_distance_graph.add_edge(v1, v2, length=solver.Value(vars[name(v1, v2)])//distance_mult)
					all_distance_graph.add_edge(v1, v2, length=solver.Value(vars[name(v1, v2)])//distance_mult)
			
			distance_graph.add_edge(0,1, length=solver.Value(vars["01"])//distance_mult)
			distance_graph.add_edge(0,2, length=solver.Value(vars["02"])//distance_mult)
			distance_graph.add_edge(0,3, length=solver.Value(vars["03"])//distance_mult)
			distance_graph.add_edge(1,4, length=solver.Value(vars["14"])//distance_mult)
			distance_graph.add_edge(2,3, length=solver.Value(vars["23"])//distance_mult)
			distance_graph.add_edge(3,5, length=solver.Value(vars["35"])//distance_mult)
			distance_graph.add_edge(3,6, length=solver.Value(vars["36"])//distance_mult)
			distance_graph.add_edge(4,6, length=solver.Value(vars["46"])//distance_mult)
			distance_graph.add_edge(5,6, length=solver.Value(vars["56"])//distance_mult)
			distance_graph.add_edge(5,7, length=solver.Value(vars["57"])//distance_mult)
			distance_graph.add_edge(6,7, length=solver.Value(vars["67"])//distance_mult)
			#distance_graph.add_node(8)
			#distance_graph.add_node(9)
			#distance_graph.add_node(10)

			positions = [(0,0), (1,5), (2,-1), (4,0), (5,10), (8,-1), (9,10), (10,2), (1,-5), (5,-10), (9,-10)]
			draw_graph(all_distance_graph, positions)
			#draw_graph(metric_distance_graph, positions)
			draw_graph(distance_graph, positions)
			plt.show()
			break
		else:
			print(f'No solution found for {choices}.')
			break

	# Statistics.
	print('\nStatistics')
	print(f'  status   : {solver.StatusName(status)}')
	print(f'  conflicts: {solver.NumConflicts()}')
	print(f'  branches : {solver.NumBranches()}')
	print(f'  wall time: {solver.WallTime()} s')


if __name__ == '__main__':
	main()