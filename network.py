from itertools import chain, combinations
import math
import networkx as nx
import matplotlib.pyplot as plt

positions = [
	(0,0),
	(1,1),
	(2,3),
	(10,3),
]
alpha = 0.6
greedy = False
skip_infinite=True

n = len(positions)

def distance(a: int, b:int) -> float:
	pa = positions[a]
	pb = positions[b]
	d = (pa[0] - pb[0], pa[1] - pb[1])
	return math.sqrt(d[0]*d[0] + d[1]*d[1])


def player_costs(graph : nx.Graph) -> dict:
	costs = {}
	total_cost = 0
	for node in graph.nodes():
		cost = 0

		#Edge cost
		cost += alpha * len(graph[node])

		#Stretches
		lengths = nx.shortest_path_length(graph, node)
		for other_node in graph.nodes():
			if other_node != node:
				if other_node in lengths:
					cost += lengths[other_node] / distance(node, other_node)
				else:
					cost = math.inf
		
		#Greedy
		for target in graph.nodes():
			if target != node:
				found = False
				for neighbor in graph[node]:
					if distance(neighbor, target) < distance(node, target):
						found = True
						break
				if not found:
					cost = math.inf
					break

		costs[node] = cost
		total_cost += cost
	costs['total'] = total_cost
	return costs

all_edges = [(a,b) for a in range(n) for b in range(n) if a != b]

outcomes = {}
outcome_graph = nx.Graph()
def build_outcome(edges : tuple) -> None:
	g : nx.DiGraph = nx.empty_graph(n, nx.DiGraph)
	for edge in edges:
		g.add_edge(edge[0], edge[1], weight=distance(edge[0], edge[1]))

	costs = player_costs(g)
	if not skip_infinite or costs['total'] != math.inf:
		outcome_graph.add_node(g, costs = costs)
		outcomes[edges] = g

# TODO: Do less stuff when costs are infinite
def connect_outcomes() -> None:
	for edges in outcomes:
		g = outcomes[edges]
		if greedy:
			for edge in edges:
				neighbor = outcomes.get(tuple(i for i in edges if i != edge), None)
				if neighbor is not None:
					outcome_graph.add_edge(g, neighbor)
		else:
			for player in range(n):
				player_edges = [(player, a) for a in range(n) if a != player]
				for toggle_edges in chain.from_iterable(combinations(player_edges, r) for r in range(1, len(player_edges)+1)):
					neighbor_edges = tuple(edge for edge in all_edges if (edge in toggle_edges) != (edge in edges))
					neighbor = outcomes.get(neighbor_edges, None)
					if neighbor is not None:
						outcome_graph.add_edge(g, neighbor)

def build_outcome_graph() -> None:
	for edges in chain.from_iterable(combinations(all_edges, r) for r in range(len(all_edges)+1)):
		build_outcome(edges)
	connect_outcomes()

def is_equilibrium(graph: nx.Graph, costs: dict, node: int) -> bool:
	for neighbor in graph[node]:
		for player in node[1]:
			if player != 'total' and costs[node][player] > costs[neighbor][player]:
				return False
	return True
			
build_outcome_graph()

#valid_nodes = [node[0] for node in outcome_graph.nodes().data() if node[1]['costs']['total'] != math.inf]
#finite_outcome_graph = outcome_graph.subgraph(valid_nodes)

colors = []
equilibria = []
costs = nx.get_node_attributes(outcome_graph, 'costs')
for node in outcome_graph.nodes():
	if is_equilibrium(outcome_graph, costs, node):
		colors.append((0,1,0))
		equilibria.append(node)
	else:
		colors.append((1,0,0))

nx.draw(outcome_graph, node_color=colors)
plt.show()


for equilibrium in equilibria:
	print(costs[equilibrium])
	nx.draw(equilibrium, pos = positions, with_labels=True)
	plt.show()
