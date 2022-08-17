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

		n = 8
		vars = {}
		for v in var_names(n):
			vars[v] = model.NewIntVar(1, var_upper_bound, v)
		
		t = model.NewIntVar(1, var_upper_bound, 't')

		good_paths = [
			"3015", "312", "342",
			"412", "4315",

			"430",
			
			"015", "215", "315", "415",

			"063", "064", "163", "164", "263", "264", "563", "564", 

			"067", "167", "267", "367", "467", "567", 
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
			"3012", "3412",
			"4215",

			"051", "251", "351", "451",

			"021", "031", "041",
			"201", "231", "241",
			"310", "320", "340",
			"304", "314", "324",

			"0367", "1367", "2367", "5367", 
			"0467", "1467", "2467", "5467", 
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
				for middle in range(n):
					if middle != v1 and middle != v2:
						model.Add(vars[name(v1, v2)] <= vars[name(v1, middle)] + vars[name(middle, v2)])
		
		# Extra stuff
		model.Add(vars[name(3,2)] > vars[name(3,1)])
		model.Add(vars[name(4,1)] > vars[name(4,2)])
		model.Add(vars[name(4,0)] > vars[name(4,1)])
		
		model.Add(vars[name(0,2)] == vars[name(0,1)] + vars[name(1,2)])
		
		model.Add(vars[name(6,0)] >= vars[name(3,0)])
		model.Add(vars[name(6,0)] >= vars[name(4,0)])
		model.Add(vars[name(6,1)] >= vars[name(3,1)])
		model.Add(vars[name(6,1)] >= vars[name(4,1)])
		model.Add(vars[name(6,2)] >= vars[name(3,2)])
		model.Add(vars[name(6,2)] >= vars[name(4,2)])
		model.Add(vars[name(6,5)] >= vars[name(3,5)])
		model.Add(vars[name(6,5)] >= vars[name(4,5)])

		model.Add(vars[name(7,0)] > vars[name(6,0)])
		model.Add(vars[name(7,1)] > vars[name(6,1)])
		model.Add(vars[name(7,2)] > vars[name(6,2)])
		model.Add(vars[name(7,5)] > vars[name(6,5)])

		model.Add(vars[name(1,5)] <= vars[name(5,6)])
		model.Add(vars[name(3,0)] <= vars[name(1,0)])

		model.Add(vars[name(4,6)] >= vars[name(3,4)])
		#model.Add(vars[name(4,6)] == vars[name(3,6)])

		for i in range(6):
			model.Add(vars[name(6,7)] <= vars[name(i,7)])


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

			positions = [(0,0), (2,-1), (4,0), (1,-3), (3, -3), (1.5,2), (2, -4), (1.5, -5)]
			draw_graph(all_distance_graph, positions)
			#draw_graph(metric_distance_graph, positions)
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