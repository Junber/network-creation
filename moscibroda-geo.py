import pygeosolve

problem = pygeosolve.Problem()
problem.add_point('a', 0, 0)
problem.add_point('b', 1, 0)
problem.add_point('c', 2, 0)
problem.add_point('1', 0.5, 1)
problem.add_point('2', 1.5, 1)

problem.add_line('ab', problem['a'], problem['b'])
problem.add_line('bc', problem['b'], problem['c'])
problem.add_line('12', problem['1'], problem['2'])
problem.add_line('a1', problem['a'], problem['1'])
problem.add_line('b1', problem['b'], problem['1'])
problem.add_line('b2', problem['b'], problem['2'])
problem.add_line('c2', problem['c'], problem['2'])

delta = 0.001

problem.constrain_position('b')
problem.constrain_position('c')
problem.constrain_line_length('ab', 1.14)
problem.constrain_line_length('bc', 1)
problem.constrain_line_length('12', 1-2*delta)
problem.constrain_line_length('a1', 1.96)
problem.constrain_line_length('b1', 2)
problem.constrain_line_length('b2', 2)
problem.constrain_line_length('c2', 2+delta)

result = problem.solve()
#problem.plot()
print("Success:", result.success)
positions = [(problem[point].x, problem[point].y) for point in ['a', 'b', 'c', '1', '2']]
print(positions)