import itertools
from ortools.sat.python import cp_model
import networkx as nx
import matplotlib.pyplot as plt

var_upper_bound = 100
model:cp_model.CpModel = None

def mult(*args):
	mult.counter += 1 
	var = model.NewIntVar(1, var_upper_bound * var_upper_bound, f'mult{mult.counter}')
	model.AddMultiplicationEquality(var, args)
	return var
mult.counter = 0


def main():
	for choices in itertools.product([True, False], repeat=2):
		global model
		model = cp_model.CpModel()

		alpha_mult = 10

		ab = model.NewIntVar(1, var_upper_bound, 'ab')
		bc = model.NewIntVar(1, var_upper_bound, 'bc')
		yz = model.NewIntVar(1, var_upper_bound, 'yz')
		ya = model.NewIntVar(1, var_upper_bound, 'ya')
		yb = model.NewIntVar(1, var_upper_bound, 'yb')
		yc = model.NewIntVar(1, var_upper_bound, 'yc')
		za = model.NewIntVar(1, var_upper_bound, 'za')
		zb = model.NewIntVar(1, var_upper_bound, 'zb')
		zc = model.NewIntVar(1, var_upper_bound, 'zc')
		alpha = model.NewIntVar(1, var_upper_bound, 'alpha')

		alphaya = mult(alpha, ya)
		alphayb = mult(alpha, yb)
		alphayc = mult(alpha, yc)
		alphaza = mult(alpha, za)
		alphazb = mult(alpha, zb)
		alphazc = mult(alpha, zc)

		#Candidate a
		model.Add(alpha_mult*(yz + zb - yb) > alphayc)
		model.Add(alpha_mult*(ya + ab - yb) > alphayc)

		#Candidate b
		model.Add(zc>zb)
		#model.Add(mult(yz, zc) + mult(ya, zc) + mult(ab, zc) < mult(zb, zb) + mult(bc, zb)) # zyab > zbc

		#Candidate c
		model.Add(mult(yz, zc) + mult(yb, zc) < mult(zb, zb) + mult(bc, zb))

		#Candidate d
		model.Add(alpha_mult*(mult(ya, yc) + mult(ab, yc) - (mult(yb, yb) + mult(bc, yb))) < mult(alphayb, yc)) # yab < ybc + alpha
		model.Add(alpha_mult*(yz+zc - (yb+bc)) < alphayc) # yzc < ybc + alpha

		#Some Routing Requirements
		model.Add(yb < zb)
		model.Add(zb < zc)
		model.Add(ya < za)

		model.Add(alpha_mult*(yb + ab) > alpha_mult*ya + 2 * alphaya) #y will build to a
		model.Add(alpha_mult*(yb + bc) < alpha_mult*yc + alphayc) #y will not build both b and c
		#y will not build c
		model.Add(yc > yb)
		model.Add(mult(ya, yc) + mult(ab, yc) > mult(yb, yb) + mult(bc, yb)) #yab > ybc

		#z needs b or c for greedy path to c
		if True:#choices[0]:
			model.Add(ab + bc > zc)
		else:
			model.Add(alpha_mult*(za + ab + bc) > alpha_mult*zc + alphazc)
		if True:#choices[1]:
			model.Add(yc > zc)
		else:
			model.Add(alpha_mult*(yz + yc) > alpha_mult*zc + alphazc)
		
		#z will not build b and c
		model.Add(alpha_mult*(zb+bc) < alpha_mult*zc + alphazc)

		#z will not build a
		model.Add(alpha_mult*(yz+ya) < alpha_mult*za + alphaza)
		model.Add(za + ab > zc + bc)

		#ab and bc will be built both ways
		#model.Add(ab == bc) # We could maybe also do without this
		model.Add(ab < ya)
		model.Add(ab < yb)
		model.Add(ab < za)
		model.Add(ab < zb)
		model.Add(ab < yc)
		model.Add(ab < zc)
		model.Add(bc < ya)
		model.Add(bc < yb)
		model.Add(bc < yb)
		model.Add(bc < zb)
		model.Add(bc < yc)
		model.Add(bc < zc)
		
		#yz will be built both ways
		model.Add(yz < ya)
		model.Add(yz < za)
		model.Add(yz < yb)
		model.Add(yz < zb)
		model.Add(yz < yc)
		model.Add(yz < zc)

		#Metricness (incomplete)
		model.Add(yz + ya >= za)
		model.Add(yz + zc >= yc)

		#Undirected things
		x = model.NewIntVar(1, var_upper_bound, 'x')
		model.Add(x < yz)
		model.Add(alpha_mult*(mult(yb, yz) + mult(ab, yz) - 2* mult(x, ya)) > mult(alphayb, ya)) # yba - yxz > alpha NOT SURE WHY THIS IS HERE!
		model.Add(2 * mult(x, za) > mult(yz, yz)+mult(ya,yz)) # zxy > zya
		model.Add(mult(zc,za) + mult(bc,za) > mult(yz, zb) + mult(yz, zb)) #zcb > zya

		model.Minimize(10 * alpha + ab + bc + yz + ya - 10* yb + yc + za + zb + zc + 1000*(zc - zb + zb - yb + yc - zc))

		# Creates a solver and solves the model.
		solver = cp_model.CpSolver()
		status = solver.Solve(model)

		if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
			print(f'Maximum of objective function: {solver.ObjectiveValue()}\n')
			print(f'ab = {solver.Value(ab)}')
			print(f'bc = {solver.Value(bc)}')
			print(f'yz = {solver.Value(yz)}')
			print(f'ya = {solver.Value(ya)}')
			print(f'yb = {solver.Value(yb)}')
			print(f'yc = {solver.Value(yc)}')
			print(f'za = {solver.Value(za)}')
			print(f'zb = {solver.Value(zb)}')
			print(f'zc = {solver.Value(zc)}')
			print(f'alpha = {solver.Value(alpha)/alpha_mult}')


			distance_mult = 10			

			distance_graph = nx.Graph()
			distance_graph.add_edge(0, 1, length=solver.Value(ab)/distance_mult)
			distance_graph.add_edge(0, 3, length=solver.Value(ya)/distance_mult)
			distance_graph.add_edge(0, 4, length=solver.Value(za)/distance_mult)
			distance_graph.add_edge(1, 2, length=solver.Value(bc)/distance_mult)
			distance_graph.add_edge(1, 3, length=solver.Value(yb)/distance_mult)
			distance_graph.add_edge(1, 4, length=solver.Value(zb)/distance_mult)
			distance_graph.add_edge(2, 3, length=solver.Value(yc)/distance_mult)
			distance_graph.add_edge(2, 4, length=solver.Value(zc)/distance_mult)
			distance_graph.add_edge(3, 4, length=solver.Value(yz)/distance_mult)
			distance_graph.add_edge(3, 5, length=solver.Value(x)/distance_mult)
			distance_graph.add_edge(4, 5, length=solver.Value(x)/distance_mult)

			positions = [(0,0), (2,0), (4,0), (1,-1), (3, -1), (2,-2)]
			nx.draw(distance_graph, pos = positions, with_labels=True)
			nx.draw_networkx_edge_labels(distance_graph, edge_labels={(u,v) : l for (u,v,l) in distance_graph.edges.data('length')}, pos = positions, label_pos = 0.3)
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