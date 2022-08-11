from itertools import chain, combinations
import math
import networkx as nx
import matplotlib.pyplot as plt

positions = [(-1.3698280641262375, 0.8288605804412503), (10, 0), (20, 0), (4.99999616807546, 19.364915702993894), (14.97999485378764, 19.370070974880857)]
alpha = 0.6
greedy_equilibria = False
greedy_routing = True
directed_edges = True
only_unilateral_edges = False # Only relevant if directed_edges = False
skip_infinite = True
should_build_outcome_graph = False
determine_approx_equilibrium = False
max_stretch_cost = True

floating_point_error_multiplier = 1.000000001

delta = 0.01
distance_graph = nx.Graph()
distance_graph.add_edge(0, 1, length=1.14)
distance_graph.add_edge(0, 2, length=2.14)
distance_graph.add_edge(0, 3, length=1.96)
distance_graph.add_edge(0, 4, length=2.45)
distance_graph.add_edge(1, 2, length=1)
distance_graph.add_edge(1, 3, length=2)
distance_graph.add_edge(1, 4, length=2)
distance_graph.add_edge(2, 3, length=2.45)
distance_graph.add_edge(2, 4, length=2 + delta)
distance_graph.add_edge(3, 4, length=1 - 2*delta)

n = len(positions)

def distance(a: int, b:int) -> float:
	if a == b:
		return 0
	return distance_graph[a][b]['length']
	pa = positions[a]
	pb = positions[b]
	d = (pa[0] - pb[0], pa[1] - pb[1])
	return math.sqrt(d[0]*d[0] + d[1]*d[1])


social_optimum = math.inf
best_approx = math.inf

def player_costs(graph : "nx.Graph | nx.DiGraph", edges: tuple) -> dict:
	costs = {}
	total_cost = 0
	for node in graph.nodes():
		cost = 0

		#Edge cost
		cost += alpha * len([edge for edge in edges if edge[0] == node])
		if not directed_edges and only_unilateral_edges:
			cost += alpha * len([edge for edge in edges if edge[1] == node])

		#Stretches
		lengths = nx.shortest_path_length(graph, node, weight="weight")
		max_stretch = 0
		for other_node in graph.nodes():
			if other_node != node:
				if other_node in lengths:
					if max_stretch_cost:
						max_stretch = max(lengths[other_node] / distance(node, other_node), max_stretch)
					else:
						cost += lengths[other_node] / distance(node, other_node)
				else:
					if skip_infinite:
						return math.inf
					cost = math.inf
		
		cost += max_stretch
		
		#Greedy Routing
		if greedy_routing:
			for target in graph.nodes():
				if target != node:
					found = False
					for neighbor in graph[node]:
						if distance(neighbor, target) < distance(node, target):
							found = True
							break
					if not found:
						if skip_infinite:
							return math.inf
						cost = math.inf
						break

		costs[node] = cost
		total_cost += cost
	costs['total'] = total_cost
	global social_optimum
	social_optimum = min(social_optimum, total_cost)
	return costs

all_edges = [(a,b) for a in range(n) for b in range(n) if a != b]
all_edges.sort()

def build_graph(edges : tuple, visual : bool) -> nx.Graph:
	g : nx.Graph = nx.empty_graph(n, (nx.DiGraph if directed_edges or visual else nx.Graph))
	for edge in edges:
		if directed_edges or not only_unilateral_edges or (edge[1], edge[0]) in edges:
			g.add_edge(edge[0], edge[1], weight=distance(edge[0], edge[1]))
	return g


outcome_graph = nx.Graph()
def build_outcome(edges : tuple) -> None:
	if skip_infinite and len(edges) < n - 1:
		return

	costs = player_costs(build_graph(edges, False), edges)
	if not skip_infinite or (costs != math.inf and costs['total'] != math.inf):
		outcome_graph.add_node(edges, costs = costs)

def connect_outcomes() -> None:
	for edges in outcome_graph:
		if greedy_equilibria:
			for remove_edge in edges:
				neighbor = tuple(i for i in edges if i != remove_edge)
				if neighbor in outcome_graph:
					outcome_graph.add_edge(edges, neighbor, changer=remove_edge[0])
				player_edges = [(remove_edge[0], b) for b in range(n) if b != remove_edge[0]]
				for add_edge in player_edges:
					if add_edge not in edges:
						new_edges = list(neighbor)
						new_edges.append(add_edge)
						new_edges.sort()
						new_neighbor = tuple(new_edges)
						if new_neighbor in outcome_graph:
							outcome_graph.add_edge(edges, new_neighbor, changer=remove_edge[0])
			for add_edge in all_edges:
				if add_edge not in edges:
					new_edges = list(edges)
					new_edges.append(add_edge)
					new_edges.sort()
					new_neighbor = tuple(new_edges)
					if new_neighbor in outcome_graph:
						outcome_graph.add_edge(edges, new_neighbor, changer=remove_edge[0])

		else:
			for player in range(n):
				player_edges = [(player, b) for b in range(n) if b != player]
				for toggle_edges in chain.from_iterable(combinations(player_edges, r) for r in range(1, len(player_edges)+1)):
					neighbor = tuple(edge for edge in all_edges if (edge in toggle_edges) != (edge in edges))
					if neighbor in outcome_graph:
						outcome_graph.add_edge(edges, neighbor, changer=player)

def get_equilibria(outcome_graph: nx.Graph) -> list:
	global best_approx
	equilibria = []
	costs = nx.get_node_attributes(outcome_graph, 'costs')
	for edges in outcome_graph:
		equilibrium = True
		approx = 1
		if greedy_equilibria:
			raise NotImplemented() #TODO
		else:
			for player in range(n):
				player_edges = [(player, b) for b in range(n) if b != player]
				for toggle_edges in chain.from_iterable(combinations(player_edges, r) for r in range(1, len(player_edges)+1)):
					neighbor = tuple(edge for edge in all_edges if (edge in toggle_edges) != (edge in edges))
					if neighbor in outcome_graph and costs[edges][player] > costs[neighbor][player] * floating_point_error_multiplier:
						equilibrium = False
						approx = max(approx, costs[edges][player] / costs[neighbor][player])
						if not determine_approx_equilibrium or approx > best_approx:
							break
				if not equilibrium and (not determine_approx_equilibrium or approx > best_approx):
					break
		if equilibrium:
			equilibria.append(edges)
		if determine_approx_equilibrium:
			best_approx = min(best_approx, approx)
	
	return equilibria

def build_outcome_graph() -> None:
	print('Building outcomes')
	for edges in chain.from_iterable(combinations(all_edges, r) for r in range(len(all_edges)+1)):
		build_outcome(edges)
	print('Connecting outcomes')
	if should_build_outcome_graph:
		connect_outcomes()

def is_equilibrium(outcome_graph: nx.Graph, costs: dict, node: int) -> bool:
	if determine_approx_equilibrium:
		raise NotImplemented() #TODO
	for neighbor in outcome_graph[node]:
		player = outcome_graph[node][neighbor]['changer']
		if costs[node][player] > costs[neighbor][player] * floating_point_error_multiplier:
			return False
	return True
			
build_outcome_graph()

#valid_nodes = [node[0] for node in outcome_graph.nodes().data() if node[1]['costs']['total'] != math.inf]
#finite_outcome_graph = outcome_graph.subgraph(valid_nodes)

equilibria = []
costs = nx.get_node_attributes(outcome_graph, 'costs')
print('Finding equilibria')
if should_build_outcome_graph:
	for node in outcome_graph.nodes():
		if is_equilibrium(outcome_graph, costs, node):
			equilibria.append(node)
else:
	equilibria = get_equilibria(outcome_graph)

print('Drawing')
print(len(equilibria))
print("Optimum:", social_optimum)
print("Best Approximate Equilibrium: ", best_approx)
if len(equilibria) > 0:
	w = math.ceil(math.sqrt(len(equilibria) + 1))
	h = math.ceil((len(equilibria) + 1) / w)
	print(w,h)
	fig, axs = plt.subplots(w,h)
	if w > 1 and h > 1:
		axs = [ax for ax_list in axs for ax in ax_list]
	labels = {graph : index + 1 for index, graph in enumerate(equilibria)}
	nx.draw(outcome_graph.subgraph(equilibria), labels=labels, ax=axs[0])


	for i, equilibrium in enumerate(equilibria):
		print(costs[equilibrium], ", \"PoA\":", costs[equilibrium]['total']/social_optimum)
		nx.draw(build_graph(equilibrium, True), pos = positions, with_labels=True, ax=axs[i+1])
	
	plt.show()
