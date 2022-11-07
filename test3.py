import numpy as np
import random

can = np.array([])

can = np.append(can,10)
can = np.append(can,20)

print(can)
print(can.max())

a = np.array( [[0,30], [2,50], [3,10]] )

line0 = a[:,0]
line1 = a[:,1]

print(type(line0))
print(line0)
print(line1)

print(np.where(line1 == line1.max())[0])

# 次進むノード番号
next_node = line0[random.choice(np.where(line1 == line1.max())[0])]

print(next_node)