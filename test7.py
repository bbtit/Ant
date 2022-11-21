import math

class Node():
  def __init__ (self, connection, pheromone, width):
    self.connection = connection # 接続先ノードの配列
    self.pheromone = pheromone # 接続先ノードとのフェロモンの配列
    self.width = width # 接続先ノードとのフェロモンの配列

M = 90
V = 0.9

def volatilize(node_list):
  # node_listの全nodeのフェロモンをV倍する関数 フェロモンの揮発に相当
  for node in node_list:
    for i in range(len(node.pheromone)):
      new_pheronone = math.floor(node.pheromone[i] * V)
      if new_pheronone <= M:
        node.pheromone[i] = M
      else:
        node.pheromone[i] = new_pheronone

node_list = []
node_list.append(Node([1],[100],[100]))

volatilize(node_list)

print(node_list[0].connection)
print(node_list[0].pheromone)
print(node_list[0].width)