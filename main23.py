# randの追加
import math
import random
import csv

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from cairosvg import svg2png

V = 0.9 # フェロモン揮発量
M = 100 # フェロモン最小値
TTL = 100 # antのTime to Live
W = 1000 # 帯域幅初期値
BETA = 0 # 経路選択の際のヒューリスティック値に対する重み(累乗)

ANT_NUM = 10 # 一回で放つAntの数
START_NODE = 0 # 出発ノード
GOAL_NODE = 99 # 目的ノード
GENERATION = 100 # ant，interestを放つ回数(世代)


class Node():
  def __init__ (self, connection:list[int], pheromone:list[int], width:list[int]):
    self.connection = connection # 接続先ノードの配列
    self.pheromone = pheromone # 接続先ノードとのフェロモンの配列
    self.width = width # 接続先ノードとの帯域の配列

class Ant():
  def __init__(self, current:int, destination:int, route:list[int], width:list[int]):
    self.current = current # 現在のノード
    self.destination = destination # コンテンツ保持ノード
    self.route = route # 辿ってきた経路の配列
    self.width = width # 辿ってきた経路の帯域の配列

class Interest():
  def __init__(self, current:int, destination:int, route:list[int], minwidth:int):
    self.current = current # 現在のノード
    self.destination = destination # コンテンツ保持ノード
    self.route = route # 辿ってきた経路の配列
    self.minwidth = minwidth # 辿ってきた経路の最小帯域

class Rand(Interest):
  def __init__(self, current:int, destination:int, route:list[int], minwidth:int):
    super().__init__(current,destination,route,minwidth)


#---------------------------------------------------


def volatilize(node_list:list[Node]) -> None:
  # node_listの全nodeのフェロモンをV倍する関数 フェロモンの揮発に相当
  for node in node_list:
    for i in range(len(node.pheromone)):
      new_pheronone = math.floor(node.pheromone[i] * V)
      if new_pheronone <= M:
        node.pheromone[i] = M
      else:
        node.pheromone[i] = new_pheronone

def update_pheromone(ant:Ant, node_list:list[Node]) -> None:
  # 目的ノードに到着したantによるフェロモンの付加(片側)
  for i in range(1,len(ant.route)):
    # ant.routeのi-1番目とi番目のノードを取得
    before_node:Node = node_list[ant.route[i-1]]
    after_node: Node = node_list[ant.route[i]]
    # before_nodeからafter_nodeへのフェロモン値を変更
    # before_node.connectionからafter_nodeのインデックスを取得
    index = before_node.connection.index(ant.route[i])
    # print("find!") # debug
    # i-1番ノードからi番ノードのフェロモン値に (その辺の帯域 × 辿った経路の帯域の平均) を加算
    before_node.pheromone[index] += before_node.width[index] * ( sum(ant.width) / len(ant.width) )

def ant_next_node(ant_list:list[Ant], node_list:list[Node]) -> None:
  # antの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for ant in reversed(ant_list):

    # print("current->"+str(ant.current)+" route->"+str(ant.route)+" width->"+str(ant.width)) # debug

    # antが今いるノードの接続ノード・フェロモン値・帯域幅を取得
    connection:list[int] = node_list[ant.current].connection
    pheromone: list[int] = node_list[ant.current].pheromone
    width:     list[int] = node_list[ant.current].width

    # print("connection->"+str(connection)+" pheromone->"+str(pheromone)+" width->"+str(width)) # debug

    # 接続ノードの内、antが辿っていないノード番号を取得
    and_set = set(ant.route) & set(connection)
    diff_list = list(set(connection) ^ and_set)
    # print("diff_list"+str(diff_list)) # debug

    # 候補先がないなら削除
    if diff_list == []:
      ant_list.remove(ant)
      print("Can't Find Route! → " + str(ant.route))

    # 候補先がある場合
    else:
      # antが辿っていないノード番号のフェロモンと帯域幅を取得
      candidacy_pheromones: list[int] = []
      candidacy_width:      list[int] = []
      for i in diff_list:
        index = connection.index(i)
        
        candidacy_pheromones.append(pheromone[index])
        candidacy_width.append(width[index])

      weight_width = [i ** BETA for i in candidacy_width]
      weighting = [x*y for (x, y) in zip(candidacy_pheromones,weight_width)]

      next_node = random.choices(diff_list,k=1,weights=weighting)[0]

      # antの属性更新
      # antの現在地更新
      ant.current = next_node
      # antの経路の配列にノード番号追加
      ant.route.append(next_node)
      # antの経路の帯域の配列に帯域を追加
      ant.width.append(width[connection.index(next_node)])

    # antが目的ノードならばノードにフェロモンの付加後ant_listから削除
      if ant.current == ant.destination:
        update_pheromone(ant,node_list)
        ant_list.remove(ant)
        print("Goal! → " + str(ant.route) + " : " + str(ant.width))

    # antがTTLならばant_listから削除
      elif (len(ant.route) == TTL):
        ant_list.remove(ant)
        print("TTL! →" + str(ant.route))

def interest_next_node(interest_list:list[Interest], node_list:list[Node], interest_log:list[int]) -> None:
  # interestの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for interest in reversed(interest_list):
    # interestが今いるノードの接続ノードとフェロモン値を取得
    connection = node_list[interest.current].connection
    pheromone = node_list[interest.current].pheromone
    width = node_list[interest.current].width

    # 接続ノードの内、interestが辿っていないノード番号を取得
    and_set = set(interest.route) & set(connection)
    diff_list = list(set(connection) ^ and_set)

    # 候補先がないなら削除
    if diff_list == []:
      interest_list.remove(interest)
      interest_log.append(0)
      print("Interest Can't Find Route! → " + str(interest.route))
      
    # 候補先がある場合
    else:
      candidacy_pheromones: list[int] = []
      # interestが辿っていないノード番号(diff_list)のフェロモンを取得
      for i in diff_list:
        index = connection.index(i)
        candidacy_pheromones.append(pheromone[index])

      # フェロモン濃度が最も高いものを選択(最大値が複数ある場合はランダム)
      max_pheromone_index = [i for i, x in enumerate(candidacy_pheromones) if x == max(candidacy_pheromones)]
      next_node = diff_list[random.choice(max_pheromone_index)]

      # interestの属性更新
      # もし現在ノードから次ノードの帯域幅が今までの最小帯域より小さかったら更新
      interest.current = next_node
      interest.route.append(next_node)
      if width[connection.index(next_node)] < interest.minwidth:
        interest.minwidth = width[connection.index(next_node)]

    # interestが目的ノードならばinterest_listから削除
      if interest.current == interest.destination:
        interest_log.append(interest.minwidth)
        interest_list.remove(interest)
        print("Interest Goal! → " + str(interest.route) + " : " + str(interest.minwidth))

    # interestがTTLならばinterest_listから削除
      elif (len(interest.route) == TTL):
        interest_list.remove(interest)
        interest_log.append(0)
        print("Interest TTL! →" + str(interest.route))

def rand_next_node(rand_list:list[Rand], node_list:list[Node], rand_log:list[int]) -> None:
  # randの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for rand in reversed(rand_list):
    # randが今いるノードの接続ノードとフェロモン値を取得
    connection = node_list[rand.current].connection
    width = node_list[rand.current].width

    # 接続ノードの内、randが辿っていないノード番号を取得
    and_set = set(rand.route) & set(connection)
    diff_list = list(set(connection) ^ and_set)

    # 候補先がないなら削除
    if diff_list == []:
      rand_list.remove(rand)
      rand_log.append(0)
      print("Rand Can't Find Route! → " + str(rand.route))
      
    # 候補先がある場合
    else:
      next_node = random.choice(diff_list)

      # randの属性更新
      # もし現在ノードから次ノードの帯域幅が今までの最小帯域より小さかったら更新
      rand.current = next_node
      rand.route.append(next_node)
      if width[connection.index(next_node)] < rand.minwidth:
        rand.minwidth = width[connection.index(next_node)]

    # randが目的ノードならばrand_listから削除
      if rand.current == rand.destination:
        rand_log.append(rand.minwidth)
        rand_list.remove(rand)
        print("rand Goal! → " + str(rand.route) + " : " + str(rand.minwidth))

    # randがTTLならばrand_listから削除
      elif (len(rand.route) == TTL):
        rand_list.remove(rand)
        rand_log.append(0)
        print("rand TTL! →" + str(rand.route))

def show_node_info(node_list:list[Node]) -> None:
  for i in range(len(node_list)):
    print("Node"+str(i))
    print(str(node_list[i].connection))
    print(str(node_list[i].pheromone))
    print(str(node_list[0].width))

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
          node_list[i].width.append(10)
          
          node_list[next_node_idx].connection.append(i)
          node_list[next_node_idx].pheromone.append(M)
          node_list[next_node_idx].width.append(10)

  for i in range(len(node_list)):
    print(str(i)+"->"+str(node_list[i].connection))
    if (len(node_list[i].connection) != edge_num ):
      print("Bad Graph!")
      create_equal_edge_graph(node_num, edge_num)
  
  return node_list


#---------------------------------------------------

if __name__ == "__main__":

  # シミュレーション回数を指定
  for _ in range(1):

    node_list:     list[Node] = [] # Nodeオブジェクト格納リスト

    ant_list:      list[Ant] = [] # Antオブジェクト格納リスト

    interest_list: list[Interest] = [] # Interestオブジェクト格納リスト
    interest_log:  list[int] = [] # interestのログ用リスト

    rand_list:     list[Rand] = [] # Randオブジェクト格納リスト
    rand_log:      list[int] = [] # Randのログ用リスト

    node_list = create_equal_edge_graph(100,5)

    # show_node_info(node_list) # debug

    for gen in range(GENERATION):

      print("gen" + str(gen))

      # Antによるフェロモン付加フェーズ
      # Antを配置
      ant_list.extend( [ Ant(START_NODE,GOAL_NODE,[START_NODE],[]) ] * ANT_NUM)
      # Antの移動
      for _ in range(TTL):
        ant_next_node(ant_list, node_list)

      # 揮発フェーズ
      volatilize(node_list)
      
      # Interestによる評価フェーズ
      # Interestを配置
      interest_list.append(Interest(START_NODE,GOAL_NODE,[START_NODE],W))
      # Interestの移動
      for _ in range(TTL):
        interest_next_node(interest_list, node_list, interest_log)

      # Randによる評価フェーズ
      # Randを配置
      rand_list.append(Rand(START_NODE,GOAL_NODE,[START_NODE],W))
      # Randの移動
      for _ in range(TTL):
        rand_next_node(rand_list, node_list, rand_log)

    print()
    print("----------------------End Gen------------------------------")
    print()

    print(interest_log)
    f = open("./log_interest.csv", "a", newline = "")
    writer = csv.writer(f)
    writer.writerow(interest_log)
    f.close()

    print(rand_log)
    f = open("./log_rand.csv", "a", newline = "")
    writer = csv.writer(f)
    writer.writerow(rand_log)
    f.close()
    

    