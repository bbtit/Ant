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
    print(str(node_list[i].connection) + str(node_list[i].pheromone) + str(node_list[0].width))


#---------------------------------------------------

if __name__ == "__main__":

  # シミュレーション回数を指定
  for _ in range(100):

    node_list:     list[Node] = [] # Nodeオブジェクト格納リスト

    ant_list:      list[Ant] = [] # Antオブジェクト格納リスト

    interest_list: list[Interest] = [] # Interestオブジェクト格納リスト
    interest_log:  list[int] = [] # interestのログ用リスト

    rand_list:     list[Rand] = [] # Randオブジェクト格納リスト
    rand_log:      list[int] = [] # Randのログ用リスト


    # 10×10のネットワークを生成
    node_list.extend([
      Node([ 10, 1 ],[ M, M ],[ 10, 10 ]),            #0
      Node([ 0, 11, 2 ],[ M, M, M ],[ 10, 10, 10 ]),  #1
      Node([ 1, 12, 3 ],[ M, M, M ],[ 10, 10, 10 ]),  #2
      Node([ 2, 13, 4 ],[ M, M, M ],[ 10, 10, 10 ]),  #3
      Node([ 3, 14, 5 ],[ M, M, M ],[ 10, 10, 10 ]),  #4
      Node([ 4, 15, 6 ],[ M, M, M ],[ 10, 10, 10 ]),  #5
      Node([ 5, 16, 7 ],[ M, M, M ],[ 10, 10, 10 ]),  #6
      Node([ 6, 17, 8 ],[ M, M, M ],[ 10, 10, 10 ]),  #7
      Node([ 7, 18, 9 ],[ M, M, M ],[ 10, 10, 10 ]),  #8
      Node([ 8, 19 ],[ M, M ],[ 10, 10 ]),            #9

      Node([ 0, 20, 11 ],[ M, M, M ],[ 10, 10, 10 ]),      #10
      Node([ 1, 10, 21, 12 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #11
      Node([ 2, 11, 22, 13 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #12
      Node([ 3, 12, 23, 14 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #13
      Node([ 4, 13, 24, 15 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #14
      Node([ 5, 14, 25, 16 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #15
      Node([ 6, 15, 26, 17 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #16
      Node([ 7, 16, 27, 18 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #17
      Node([ 8, 17, 28, 19 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #18
      Node([ 9, 18, 29 ],[ M, M, M ],[ 10, 10, 10 ]),      #19

      Node([ 10, 30, 21 ],[ M, M, M ],[ 10, 10, 10 ]),      #20
      Node([ 11, 20, 31, 22 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #21
      Node([ 12, 21, 32, 23 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #22
      Node([ 13, 22, 33, 24 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #23
      Node([ 14, 23, 34, 25 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #24
      Node([ 15, 24, 35, 26 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #25
      Node([ 16, 25, 36, 27 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #26
      Node([ 17, 26, 37, 28 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #27
      Node([ 18, 27, 38, 29 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #28
      Node([ 19, 28, 39 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),      #29

      Node([ 20, 40, 31 ],[ M, M, M ],[ 10, 10, 10 ]),      #30
      Node([ 21, 30, 41, 32 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #31
      Node([ 22, 31, 42, 33 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #32
      Node([ 23, 32, 43, 34 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #33
      Node([ 24, 33, 44, 35 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #34
      Node([ 25, 34, 45, 36 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #35
      Node([ 26, 35, 46, 37 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #36
      Node([ 27, 36, 47, 38 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #37
      Node([ 28, 37, 48, 39 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #38
      Node([ 29, 38, 49 ],[ M, M, M ],[ 10, 10, 10 ]),      #39

      Node([ 30, 50, 41 ],[ M, M, M ],[ 10, 10, 10 ]),      #40
      Node([ 31, 40, 51, 42 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #41
      Node([ 32, 41, 52, 43 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #42
      Node([ 33, 42, 53, 44 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #43
      Node([ 34, 43, 54, 45 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #44
      Node([ 35, 44, 55, 46 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #45
      Node([ 36, 45, 56, 47 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #46
      Node([ 37, 46, 57, 48 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #47
      Node([ 38, 47, 58, 49 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #48
      Node([ 39, 48, 59 ],[ M, M, M ],[ 10, 10, 10 ]),      #49

      Node([ 40, 60, 51 ],[ M, M, M ],[ 10, 10, 10 ]),      #50
      Node([ 41, 50, 61, 52 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #51
      Node([ 42, 51, 62, 53 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #52
      Node([ 43, 52, 63, 54 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #53
      Node([ 44, 53, 64, 55 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #54
      Node([ 45, 54, 65, 56 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #55
      Node([ 46, 55, 66, 57 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #56
      Node([ 47, 56, 67, 58 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #57
      Node([ 48, 57, 68, 59 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #58
      Node([ 49, 58, 69 ],[ M, M, M ],[ 10, 10, 10 ]),      #59

      Node([ 50, 70, 61 ],[ M, M, M ],[ 10, 10, 10 ]),      #60
      Node([ 51, 60, 71, 62 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #61
      Node([ 52, 61, 72, 63 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #62
      Node([ 53, 62, 73, 64 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #63
      Node([ 54, 63, 74, 65 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #64
      Node([ 55, 64, 75, 66 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #65
      Node([ 56, 65, 76, 67 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #66
      Node([ 57, 66, 77, 68 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #67
      Node([ 58, 67, 78, 69 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #68
      Node([ 59, 68, 79 ],[ M, M, M ],[ 10, 10, 10 ]),      #69

      Node([ 60, 80, 71 ],[ M, M, M ],[ 10, 10, 10 ]),      #70
      Node([ 61, 70, 81, 72 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #71
      Node([ 62, 71, 82, 73 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #72
      Node([ 63, 72, 83, 74 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #73
      Node([ 64, 73, 84, 75 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #74
      Node([ 65, 74, 85, 76 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #75
      Node([ 66, 75, 86, 77 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #76
      Node([ 67, 76, 87, 78 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #77
      Node([ 68, 77, 88, 79 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #78
      Node([ 69, 78, 89 ],[ M, M, M ],[ 10, 10, 10 ]),      #79

      Node([ 70, 90, 81 ],[ M, M, M ],[ 10, 10, 10 ]),      #80
      Node([ 71, 80, 91, 82 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #81
      Node([ 72, 81, 92, 83 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #82
      Node([ 73, 82, 93, 84 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #83
      Node([ 74, 83, 94, 85 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #84
      Node([ 75, 84, 95, 86 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #85
      Node([ 76, 85, 96, 87 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #86
      Node([ 77, 86, 97, 88 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #87
      Node([ 78, 87, 98, 89 ],[ M, M, M, M ],[ 10, 10, 10, 10 ]),  #88
      Node([ 79, 88, 99 ],[ M, M, M ],[ 10, 10, 10 ]),      #89

      Node([ 80, 91 ],[ M, M ],[ 10, 10 ]),             #90
      Node([ 81, 90, 92 ],[ M, M, M ],[ 10, 10, 10 ]),  #91
      Node([ 82, 91, 93 ],[ M, M, M ],[ 10, 10, 10 ]),  #92
      Node([ 83, 92, 94 ],[ M, M, M ],[ 10, 10, 10 ]),  #93
      Node([ 84, 93, 95 ],[ M, M, M ],[ 10, 10, 10 ]),  #94
      Node([ 85, 94, 96 ],[ M, M, M ],[ 10, 10, 10 ]),  #95
      Node([ 86, 95, 97 ],[ M, M, M ],[ 10, 10, 10 ]),  #96
      Node([ 87, 96, 98 ],[ M, M, M ],[ 10, 10, 10 ]),  #97
      Node([ 88, 97, 99 ],[ M, M, M ],[ 10, 10, 10 ]),  #98
      Node([ 89, 98 ],[ M, M ],[ 10, 10 ]),             #99
    ])

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
    

    