from geoBase import solve
import pygeosolve

epsilon = 0

vertices = {
	'a': (0, 0),
	'b': (1, 0),
	'c': (2, 0),
	'y': (0.5, 2),
	'z': (1.5, 2),

	'w': (0.5,2.5),
	'x': (1.5,2.5),
}

distances = {
	'ab': 1.14,
	'bc': 1,
	'yz': 1-2*epsilon,
	'ay': 1.96,
	'by': 2-epsilon,
	'bz': 2,
	'cz': 2+epsilon,

	'yw' : 0.4,
	'zw' : 1.2,
	'yx' : 1.2,
	'zx' : 0.4,
}

def check(problem: pygeosolve.Problem):
	return problem["aw"].length() >= problem["ay"].length() and problem["ax"].length() >= problem["az"].length()


problem = solve(vertices, distances, ['b', 'c'], check)

maxi = 0
for v1 in 'abc':
	for v2 in 'wx':
		
		#edgecost = 0.6   # Const
		edgecost = 0.3 * problem[v1+v2].length()   # Dist

		x = edgecost / (min(problem[v1+'y'].length() + problem['y'+v2].length(), problem[v1+'z'].length() + problem['z'+v2].length()) / problem[v1+v2].length() - 1)
		print(v1, v2, x)
		maxi = max(maxi,x)
print("Max:", maxi)