import random

W = 1000 # 帯域幅初期値
M = 100 # フェロモン最小値


class Node():
  def __init__ (self, connection:list[int], pheromone:list[int], width:list[int]):
    self.connection = connection # 接続先ノードの配列
    self.pheromone = pheromone # 接続先ノードとのフェロモンの配列
    self.width = width # 接続先ノードとの帯域の配列

def show_node_info(node_list:list[Node]) -> None:
  for i in range(len(node_list)):
    print("Node"+str(i))
    print(str(node_list[i].connection))
    print(str(node_list[i].pheromone))
    print(str(node_list[i].width))

def create_equal_edge_graph2(node_list:list[Node], edge_num:int) -> None:
  for i in range(len(node_list)):
    print("Num "+str(i)) # debug
    # 規定の辺の数より少ないなら繰り返す
    while (len(node_list[i].connection) < edge_num):
      # 規定の辺の数より辺が少ないノードのインデックスを候補として格納
      cand_index = [x for x ,y in enumerate(node_list) if len(y.connection) < edge_num]
      # 自分のインデックスと接続先インデックスは候補から削除
      if i in cand_index:
        cand_index.remove(i)

      for j in node_list[i].connection:
        if j in cand_index:
          cand_index.remove(j)
          
      print("->"+str(cand_index)) # debug

      if cand_index == []:
        break

      else:
        next_node_idx = random.choice(cand_index)
        
        node_list[i].connection.append(next_node_idx)
        node_list[next_node_idx].connection.append(i)

  for i in range(len(node_list)):
    print(str(i)+"->"+str(node_list[i].connection))



def create_equal_edge_graph(node_num:int, edge_num:int) -> list[Node]:
  # 正則グラフを作成し，Nodeオブジェクトが含まれたlistを返す
  node_list = [Node([],[],[]) for _ in range(node_num)]  
  # node_listの先頭から一本ずつ辺を引く
  for _ in range(edge_num):
    for i in range(len(node_list)):
      # print("Num "+str(i)) # debug
      # 規定の辺の数より少ないなら実行
      if (len(node_list[i].connection) < edge_num):
        # 規定の辺の数より辺が少ないノードのインデックスを候補として格納
        cand_index = [x for x ,y in enumerate(node_list) if len(y.connection) < edge_num]
        # 自分のインデックスと接続先インデックスは候補から削除
        if i in cand_index:
          cand_index.remove(i)
        for j in node_list[i].connection:
          if j in cand_index:
            cand_index.remove(j)   
        # print("->"+str(cand_index)) # debug
        # 候補がなければやめる
        if cand_index == []:
          continue
        # 候補先があればランダムに選択
        else:
          next_node_idx = random.choice(cand_index)
          # 新たな接続先情報を追加
          node_list[i].connection.append(next_node_idx)
          node_list[i].pheromone.append(M)
          node_list[i].width.append(random.randint(1,10) * 10)
          
          node_list[next_node_idx].connection.append(i)
          node_list[next_node_idx].pheromone.append(M)
          node_list[next_node_idx].width.append(random.randint(1,10) * 10)

  return node_list


while(1):
  node_list = create_equal_edge_graph(100,5)
  show_node_info(node_list)
  if(all(len(node.connection) == 5 for node in node_list)):
    print("Good Graph")
    break
  else:
    print("Bad Graph")
