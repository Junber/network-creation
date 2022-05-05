from itertools import chain, combinations
import math
import networkx as nx
import matplotlib.pyplot as plt

positions = [(-0.13698283326720598, 0.08288618577076463), (1, 0), (2, 0), (0.4999994645292778, 1.9364916180298117), (1.4979992586034918, 1.93700707153958)]
alpha = 0.6
greedy_equilibria = False
greedy_routing = True
directed_edges = False
only_unilateral_edges = True # Only relevant if directed_edges = False
skip_infinite = True

n = len(positions)

def distance(a: int, b:int) -> float:
	pa = positions[a]
	pb = positions[b]
	d = (pa[0] - pb[0], pa[1] - pb[1])
	return math.sqrt(d[0]*d[0] + d[1]*d[1])


def player_costs(graph : nx.Graph, edges: tuple) -> dict:
	costs = {}
	total_cost = 0
	for node in graph.nodes():
		cost = 0

		#Edge cost
		cost += alpha * len(edges)

		#Stretches
		lengths = nx.shortest_path_length(graph, node)
		for other_node in graph.nodes():
			if other_node != node:
				if other_node in lengths:
					cost += lengths[other_node] / distance(node, other_node)
				else:
					if skip_infinite:
						return math.inf
					cost = math.inf
		
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
	return costs

all_edges = [(a,b) for a in range(n) for b in range(n) if a != b and (directed_edges or a < b)]

def build_graph(edges : tuple) -> nx.Graph:
	g : nx.Graph = nx.empty_graph(n, (nx.DiGraph if directed_edges else nx.Graph))
	for edge in edges:
		if directed_edges or not only_unilateral_edges or (edge[1], edge[0]) in edges:
			g.add_edge(edge[0], edge[1], weight=distance(edge[0], edge[1]))
	return g


outcome_graph = nx.Graph()
def build_outcome(edges : tuple) -> None:
	if skip_infinite and len(edges) < n - 1:
		return

	costs = player_costs(build_graph(edges), edges)
	if not skip_infinite or (costs != math.inf and costs['total'] != math.inf):
		outcome_graph.add_node(edges, costs = costs)

def connect_outcomes() -> None:
	for edges in outcome_graph:
		if greedy_equilibria:
			for edge in edges:
				neighbor = tuple(i for i in edges if i != edge)
				if neighbor in outcome_graph:
					outcome_graph.add_edge(edges, neighbor, changer=edge[0])
		else:
			for player in range(n):
				player_edges = [(player, b) for b in range(n) if b != player and (directed_edges or player < b)]
				for toggle_edges in chain.from_iterable(combinations(player_edges, r) for r in range(1, len(player_edges)+1)):
					neighbor = tuple(edge for edge in all_edges if (edge in toggle_edges) != (edge in edges))
					if neighbor in outcome_graph:
						outcome_graph.add_edge(edges, neighbor, changer=player)

def build_outcome_graph() -> None:
	print('Building outcomes')
	for edges in chain.from_iterable(combinations(all_edges, r) for r in range(len(all_edges)+1)):
		build_outcome(edges)
	print('Connecting outcomes')
	connect_outcomes()

def is_equilibrium(outcome_graph: nx.Graph, costs: dict, node: int) -> bool:
	for neighbor in outcome_graph[node]:
		player = outcome_graph[node][neighbor]['changer']
		if costs[node][player] > costs[neighbor][player]:
			return False
	return True
			
build_outcome_graph()

#valid_nodes = [node[0] for node in outcome_graph.nodes().data() if node[1]['costs']['total'] != math.inf]
#finite_outcome_graph = outcome_graph.subgraph(valid_nodes)

print('Finding equilibria')
colors = []
equilibria = []
costs = nx.get_node_attributes(outcome_graph, 'costs')
for node in outcome_graph.nodes():
	if is_equilibrium(outcome_graph, costs, node):
		colors.append((0,1,0))
		equilibria.append(node)
	else:
		colors.append((1,0,0))

print('Drawing')
print(len(equilibria))
if len(equilibria) > 0:
	w = math.ceil(math.sqrt(len(equilibria) + 1))
	h = math.ceil((len(equilibria) + 1) / w)
	print(w,h)
	fig, axs = plt.subplots(w,h)
	labels = {graph : index + 1 for index, graph in enumerate(equilibria)}
	#nx.draw(outcome_graph, node_color=colors)
	nx.draw(outcome_graph.subgraph(equilibria), labels=labels, ax=axs[0])


	for i, equilibrium in enumerate(equilibria):
		print(costs[equilibrium])
		nx.draw(build_graph(equilibrium), pos = positions, with_labels=True, ax=axs[i+1])
		plt.show()
