# 複数回のシミュレーション csvに追記型
# [方式C] 付加フェロモン量は　その辺の帯域　×　辿った経路の帯域の平均

import math
import random
import csv

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from cairosvg import svg2png

V = 0.9 # フェロモン揮発量
M = 100 # フェロモン最小値
TTL = 100 # 蟻のTime to Live
W = 1000 # 帯域幅初期値
BETA = 0 # 経路選択の際のヒューリスティック値に対する重み(累乗)

ANT_NUM = 10 # 一回で放つAntの数
INTEREST_NUM = 1 # 一回で放つInterestの数
START_NODE = 0 # 出発ノード
GOAL_NODE = 99 # 目的ノード
GENERATION = 100 # 蟻，interestを放つ回数(世代)

node_list=[] # Nodeオブジェクト格納リスト
ant_list=[] # Antオブジェクト格納リスト
interest_list=[] # Interestオブジェクト格納リスト
interest_log=[] # interestのログ用リスト


class Node():
  def __init__(self,connection=np.empty([0,3],dtype=int)):
    # 経路表として[接続先ノード,フェロモン,帯域幅]のテーブルを二次元配列で保持
    self.connection = connection

class Ant():
  def __init__(self,current,destination,route,width):
    self.current = current # 現在のノード
    self.destination = destination # 目的ノード(コンテンツ保持ノード)
    self.route = route # 辿ってきた経路の配列
    self.width = width # 辿ってきた経路の帯域の配列

class Interest():
  def __init__(self,current,destination,route,minwidth):
    self.current = current # 現在のノード
    self.destination = destination # 目的ノード(コンテンツ保持ノード)
    self.route = route # 辿ってきた経路の配列
    self.minwidth = minwidth # 辿ってきた経路の最小帯域

#---------------------------------------------------


def volatilize(node_list,V):
  # node_listの全nodeのフェロモンをV倍する関数 フェロモンの揮発に相当
  for node in node_list:
    for j in range(len(node.connection)):
      new_pheronone=math.floor(node.connection[j][1] * V)
      # 最小フェロモン量を下回らないように
      if new_pheronone <= M:
        node.connection[j][1] = M
      else:
        node.connection[j][1] = new_pheronone

def update_pheromone(ant,node_list):
  # 目的ノードに到着したantによるフェロモンの付加(片側)
  for i in range(1,len(ant.route)):
    # ant.routeのi-1番目のノードを取得
    node = node_list[ant.route[i-1]]
    # ant.routeのi-1番目からi番目のedgeのフェロモン値を変更
    # bofore_nodeのconnectionの0列目を取得
    before_line0 = node.connection[:,0]
    # before_nodeのconnectionからafter_node番号の行を探索
    row = np.where(before_line0 == ant.route[i])[0][0]
    # i-1番ノードからi番ノードのフェロモン値に (その辺の帯域 × 辿った経路の帯域の平均) を加算
    node.connection[row][1] += node.connection[row][2] * ( sum(ant.width) / len(ant.width) )

def ant_next_node(ant_list,node_list):
  # antの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for ant in reversed(ant_list):
    candidacy_pheromones = []
    candidacy_width = []
    current_node = node_list[ant.current]
    # antが今いるノードの接続ノード・フェロモン値・帯域幅を取得
    line0 = current_node.connection[:,0]
    line1 = current_node.connection[:,1]
    line2 = current_node.connection[:,2]

    # 接続ノードの内、antが辿っていないノード番号を取得
    and_set=set(ant.route) & set(line0)
    diff_list=list(set(line0) ^ and_set)

    # 候補先がないなら削除
    if diff_list == []:
      ant_list.remove(ant)
      print("Can't Find Route! → " + str(ant.route))

    else:
      # 蟻が辿っていないノード番号のフェロモンを取得
      for i in diff_list:
        # diff_listの要素がline0の何行目か取得
        diff_row = np.where(line0 == i)[0][0]
        # diff_listの要素のフェロモン値をcandidacy_pheromonsにappend
        candidacy_pheromones.append(line1[diff_row])
        # diff_listの要素の帯域幅をcandidacy_widthにappend
        candidacy_width.append(line2[diff_row])
        weight_width = [i ** BETA for i in candidacy_width]

        weighting = [x*y for (x, y) in zip(candidacy_pheromones,weight_width)]

      # 次のノード番号をl1の重みづけでl0からランダムに選択
      next_node = random.choices(diff_list,k=1,weights=weighting)[0]
      # 次のノード番号がconnection0列目の何行目か探索
      row = np.where(line0 == next_node)[0][0]

      # antの属性更新
      # 蟻の現在地更新
      ant.current = current_node.connection[row][0]
      # 蟻の経路の配列にノード番号追加
      ant.route.append(next_node)
      # 蟻の経路の帯域の配列に帯域を追加
      ant.width.append(current_node.connection[row][2])

    # 蟻が目的ノードならばノードにフェロモンの付加後ant_listから削除
      if ant.current==ant.destination:
        update_pheromone(ant,node_list)
        ant_list.remove(ant)
        print("Goal! → " + str(ant.route) + " : " + str(ant.width))

    # 蟻がTTLならばant_listから削除
      elif (len(ant.route)==TTL):
        ant_list.remove(ant)
        print("TTL! →" + str(ant.route))

def interest_next_node(interest_list,node_list,interest_log,gen):
  # interestの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for interest in reversed(interest_list):
    candidacy_pheromones = np.array([])
    current_node = node_list[interest.current]
    # interestが今いるノードの接続ノードとフェロモン値を取得
    line0 = current_node.connection[:,0]
    line1 = current_node.connection[:,1]
    # 接続ノードの内、interestが辿っていないノード番号を取得
    and_set = set(interest.route) & set(line0)
    diff_list = list(set(line0) ^ and_set)
    # 候補先がないなら削除
    if diff_list == []:
      interest_list.remove(interest)
      interest_log.append(0)
      print("Interest Can't Find Route! → " + str(interest.route))
      
    # 候補先がある場合
    else:
      # interestが辿っていないノード番号(diff_list)のフェロモンを取得
      for i in diff_list:
        # diff_listの要素がline0の何行目か取得
        diff_row = np.where(line0 == i)[0][0]
        # diff_listの要素のフェロモン値をcandidacy_pheromonsにappend
        candidacy_pheromones = np.append(candidacy_pheromones, line1[diff_row])

      # 次のノード番号をl1の重みづけでl0からランダムに選択 → フェロモン濃度が最も高いものを選択(最大値が複数ある場合はランダム)
      next_node = diff_list[random.choice(np.where(candidacy_pheromones == candidacy_pheromones.max())[0])]
      # 次のノード番号がconnect0列目の何行目か探索
      row = np.where(line0 == next_node)[0][0]

      # interestの属性更新
      # もし現在ノードから次ノードの帯域幅が今までの最小帯域より小さかったら更新
      if current_node.connection[row][2] < interest.minwidth:
        interest.minwidth = current_node.connection[row][2]
      interest.current = current_node.connection[row][0]
      interest.route.append(next_node)

    # interestが目的ノードならばinterest_listから削除
      if interest.current==interest.destination:
        interest_list.remove(interest)
        interest_log.append(interest.minwidth)
        print("Interest Goal! → " + str(interest.route) + " : " + str(interest.minwidth))

    # interestがTTLならばinterest_listから削除
      elif (len(interest.route)==TTL):
        interest_list.remove(interest)
        interest_log.append(0)
        print("Interest TTL! →" + str(interest.route))

def show_node_info(node_list):
  for i in range(len(node_list)):
    print(node_list[i].connection)

def edge2node(edges,node_list):
  # グラフ表示用のedgesからnodeのconnection属性を作成
  # 事前にnode_listに無垢のNodeインスタンスをNodeの数だけ準備しておく必要あり
  for edge in edges:
    before_node = node_list[edge[0]]
    after_node = node_list[edge[1]]
    # 帯域幅をランダムに作成
    width = 10
    # nodeのconnection属性に情報を追加
    before_node.connection = np.append(before_node.connection , np.array([[edge[1],M,width]]) , axis=0)
    after_node.connection = np.append(after_node.connection , np.array([[edge[0],M,width]]) , axis=0)

def node2edge(node_list):
  # node_listからネットワークのグラフ表示のためのedgeのリストedgesを返す
  edges=[]
  for i in range(len(node_list)):
    # i番目ノードの接続先を取得
    line0 = node_list[i].connection[:,0]
    # i番目ノードのフェロモン値を取得
    line1 = node_list[i].connection[:,1]
    # i番目ノードの帯域幅を取得
    line2 = node_list[i].connection[:,2]

    sum_line1 = sum(line1)

    for j in range(len(line0)):
      # 色はフェロモン量の絶対値ではなく、そのノードのフェロモン総和との相対値で決定
      # 太さは帯域÷20
      edge=(i,line0[j],{"minlen":"5.0", "label": str(line2[j])+":"+str(line1[j]), "color": "0.000 " + str(round(line1[j]/sum_line1,2)) + " 1.000", "penwidth":str(line2[j]/20), "fontsize":"8"})
      edges.append(edge)

  return edges

def visualize_graph(node_list):
  nodes = [i for i in range(len(node_list))]
  edges = node2edge(node_list)

  g = nx.MultiDiGraph()
  g.add_nodes_from(nodes)
  g.add_edges_from(edges)

  agraph = nx.nx_agraph.to_agraph(g)
  agraph.node_attr["shape"] = "circle" 
  agraph.draw( "./sample.pdf", prog="fdp", format="pdf")

def visualize_interest(interest_log):
  # 横軸:放ったAntの総数
  x=[]
  # 縦軸:Interestの到達率
  reach_rate=[]
  # 縦軸:到達したInterestの帯域の平均
  ave_wid=[]

  for i in range(len(interest_log)):
    x.append(i*ANT_NUM)
    ave_wid.append(interest_log[i])


  fig = plt.figure()

  ax1 = fig.add_subplot(1,1,1)
  ax1.scatter(x,ave_wid)
  ax1.set_ylim(0,100)
  ax1.set_xlabel("The number of released ant")
  ax1.set_ylabel("Capacity path of interest")

  plt.show()


#---------------------------------------------------

if __name__ == "__main__":

  for _ in range(100):

    node_list=[] # Nodeオブジェクト格納リスト
    ant_list=[] # Antオブジェクト格納リスト
    interest_list=[] # Interestオブジェクト格納リスト
    interest_log=[] # interestのログ用リスト

    # 10×10のネットワークを生成
    # 0行目
    node_list.append(Node(np.array([         [10,M,10],[1,M,100]]))) #0
    node_list.append(Node(np.array([[0,M,10],[11,M,100],[2,M,10]]))) #1
    node_list.append(Node(np.array([[1,M,10],[12,M,10],[3,M,10]]))) #2
    node_list.append(Node(np.array([[2,M,10],[13,M,10],[4,M,10]]))) #3
    node_list.append(Node(np.array([[3,M,10],[14,M,10],[5,M,10]]))) #4
    node_list.append(Node(np.array([[4,M,10],[15,M,10],[6,M,10]]))) #5
    node_list.append(Node(np.array([[5,M,10],[16,M,10],[7,M,10]]))) #6
    node_list.append(Node(np.array([[6,M,10],[17,M,10],[8,M,10]]))) #7
    node_list.append(Node(np.array([[7,M,10],[18,M,10],[9,M,10]]))) #8
    node_list.append(Node(np.array([[8,M,10],[19,M,10]         ]))) #9
    # 1行目
    node_list.append(Node(np.array([[0,M,10]          ,[20,M,10],[11,M,10]]))) #10
    node_list.append(Node(np.array([[1,M,10],[10,M,10],[21,M,10],[12,M,100]]))) #11
    node_list.append(Node(np.array([[2,M,10],[11,M,10],[22,M,100],[13,M,10]]))) #12
    node_list.append(Node(np.array([[3,M,10],[12,M,10],[23,M,10],[14,M,10]]))) #13
    node_list.append(Node(np.array([[4,M,10],[13,M,10],[24,M,10],[15,M,10]]))) #14
    node_list.append(Node(np.array([[5,M,10],[14,M,10],[25,M,10],[16,M,10]]))) #15
    node_list.append(Node(np.array([[6,M,10],[15,M,10],[26,M,10],[17,M,10]]))) #16
    node_list.append(Node(np.array([[7,M,10],[16,M,10],[27,M,10],[18,M,10]]))) #17
    node_list.append(Node(np.array([[8,M,10],[17,M,10],[28,M,10],[19,M,10]]))) #18
    node_list.append(Node(np.array([[9,M,10],[18,M,10],[29,M,10]          ]))) #19
    # 2行目
    node_list.append(Node(np.array([[10,M,10]          ,[30,M,10],[21,M,10]]))) #20
    node_list.append(Node(np.array([[11,M,10],[20,M,10],[31,M,10],[22,M,10]]))) #21
    node_list.append(Node(np.array([[12,M,10],[21,M,10],[32,M,10],[23,M,100]]))) #22
    node_list.append(Node(np.array([[13,M,10],[22,M,10],[33,M,100],[24,M,10]]))) #23
    node_list.append(Node(np.array([[14,M,10],[23,M,10],[34,M,10],[25,M,10]]))) #24
    node_list.append(Node(np.array([[15,M,10],[24,M,10],[35,M,10],[26,M,10]]))) #25
    node_list.append(Node(np.array([[16,M,10],[25,M,10],[36,M,10],[27,M,10]]))) #26
    node_list.append(Node(np.array([[17,M,10],[26,M,10],[37,M,10],[28,M,10]]))) #27
    node_list.append(Node(np.array([[18,M,10],[27,M,10],[38,M,10],[29,M,10]]))) #28
    node_list.append(Node(np.array([[19,M,10],[28,M,10],[39,M,10]          ]))) #29
    # 3行目
    node_list.append(Node(np.array([[20,M,10]          ,[40,M,10],[31,M,10]]))) #30
    node_list.append(Node(np.array([[21,M,10],[30,M,10],[41,M,10],[32,M,10]]))) #31
    node_list.append(Node(np.array([[22,M,10],[31,M,10],[42,M,10],[33,M,10]]))) #32
    node_list.append(Node(np.array([[23,M,10],[32,M,10],[43,M,10],[34,M,100]]))) #33
    node_list.append(Node(np.array([[24,M,10],[33,M,10],[44,M,100],[35,M,10]]))) #34
    node_list.append(Node(np.array([[25,M,10],[34,M,10],[45,M,10],[36,M,10]]))) #35
    node_list.append(Node(np.array([[26,M,10],[35,M,10],[46,M,10],[37,M,10]]))) #36
    node_list.append(Node(np.array([[27,M,10],[36,M,10],[47,M,10],[38,M,10]]))) #37
    node_list.append(Node(np.array([[28,M,10],[37,M,10],[48,M,10],[39,M,10]]))) #38
    node_list.append(Node(np.array([[29,M,10],[38,M,10],[49,M,10]          ]))) #39
    # 4行目
    node_list.append(Node(np.array([[30,M,10]          ,[50,M,10],[41,M,10]]))) #40
    node_list.append(Node(np.array([[31,M,10],[40,M,10],[51,M,10],[42,M,10]]))) #41
    node_list.append(Node(np.array([[32,M,10],[41,M,10],[52,M,10],[43,M,10]]))) #42
    node_list.append(Node(np.array([[33,M,10],[42,M,10],[53,M,10],[44,M,10]]))) #43
    node_list.append(Node(np.array([[34,M,10],[43,M,10],[54,M,10],[45,M,100]]))) #44
    node_list.append(Node(np.array([[35,M,10],[44,M,10],[55,M,100],[46,M,10]]))) #45
    node_list.append(Node(np.array([[36,M,10],[45,M,10],[56,M,10],[47,M,10]]))) #46
    node_list.append(Node(np.array([[37,M,10],[46,M,10],[57,M,10],[48,M,10]]))) #47
    node_list.append(Node(np.array([[38,M,10],[47,M,10],[58,M,10],[49,M,10]]))) #48
    node_list.append(Node(np.array([[39,M,10],[48,M,10],[59,M,10]          ]))) #49
    # 5行目
    node_list.append(Node(np.array([[40,M,10]          ,[60,M,10],[51,M,10]]))) #50
    node_list.append(Node(np.array([[41,M,10],[50,M,10],[61,M,10],[52,M,10]]))) #51
    node_list.append(Node(np.array([[42,M,10],[51,M,10],[62,M,10],[53,M,10]]))) #52
    node_list.append(Node(np.array([[43,M,10],[52,M,10],[63,M,10],[54,M,10]]))) #53
    node_list.append(Node(np.array([[44,M,10],[53,M,10],[64,M,10],[55,M,10]]))) #54
    node_list.append(Node(np.array([[45,M,10],[54,M,10],[65,M,10],[56,M,100]]))) #55
    node_list.append(Node(np.array([[46,M,10],[55,M,10],[66,M,100],[57,M,10]]))) #56
    node_list.append(Node(np.array([[47,M,10],[56,M,10],[67,M,10],[58,M,10]]))) #57
    node_list.append(Node(np.array([[48,M,10],[57,M,10],[68,M,10],[59,M,10]]))) #58
    node_list.append(Node(np.array([[49,M,10],[58,M,10],[69,M,10]          ]))) #59
    # 6行目
    node_list.append(Node(np.array([[50,M,10]          ,[70,M,10],[61,M,10]]))) #60
    node_list.append(Node(np.array([[51,M,10],[60,M,10],[71,M,10],[62,M,10]]))) #61
    node_list.append(Node(np.array([[52,M,10],[61,M,10],[72,M,10],[63,M,10]]))) #62
    node_list.append(Node(np.array([[53,M,10],[62,M,10],[73,M,10],[64,M,10]]))) #63
    node_list.append(Node(np.array([[54,M,10],[63,M,10],[74,M,10],[65,M,10]]))) #64
    node_list.append(Node(np.array([[55,M,10],[64,M,10],[75,M,10],[66,M,10]]))) #65
    node_list.append(Node(np.array([[56,M,10],[65,M,10],[76,M,10],[67,M,100]]))) #66
    node_list.append(Node(np.array([[57,M,10],[66,M,10],[77,M,100],[68,M,10]]))) #67
    node_list.append(Node(np.array([[58,M,10],[67,M,10],[78,M,10],[69,M,10]]))) #68
    node_list.append(Node(np.array([[59,M,10],[68,M,10],[79,M,10]          ]))) #69
    # 7行目
    node_list.append(Node(np.array([[60,M,10]          ,[80,M,10],[71,M,10]]))) #70
    node_list.append(Node(np.array([[61,M,10],[70,M,10],[81,M,10],[72,M,10]]))) #71
    node_list.append(Node(np.array([[62,M,10],[71,M,10],[82,M,10],[73,M,10]]))) #72
    node_list.append(Node(np.array([[63,M,10],[72,M,10],[83,M,10],[74,M,10]]))) #73
    node_list.append(Node(np.array([[64,M,10],[73,M,10],[84,M,10],[75,M,10]]))) #74
    node_list.append(Node(np.array([[65,M,10],[74,M,10],[85,M,10],[76,M,10]]))) #75
    node_list.append(Node(np.array([[66,M,10],[75,M,10],[86,M,10],[77,M,10]]))) #76
    node_list.append(Node(np.array([[67,M,10],[76,M,10],[87,M,10],[78,M,100]]))) #77
    node_list.append(Node(np.array([[68,M,10],[77,M,10],[88,M,100],[79,M,10]]))) #78
    node_list.append(Node(np.array([[69,M,10],[78,M,10],[89,M,10]          ]))) #79
    # 8行目
    node_list.append(Node(np.array([[70,M,10]          ,[90,M,10],[81,M,10]]))) #80
    node_list.append(Node(np.array([[71,M,10],[80,M,10],[91,M,10],[82,M,10]]))) #81
    node_list.append(Node(np.array([[72,M,10],[81,M,10],[92,M,10],[83,M,10]]))) #82
    node_list.append(Node(np.array([[73,M,10],[82,M,10],[93,M,10],[84,M,10]]))) #83
    node_list.append(Node(np.array([[74,M,10],[83,M,10],[94,M,10],[85,M,10]]))) #84
    node_list.append(Node(np.array([[75,M,10],[84,M,10],[95,M,10],[86,M,10]]))) #85
    node_list.append(Node(np.array([[76,M,10],[85,M,10],[96,M,10],[87,M,10]]))) #86
    node_list.append(Node(np.array([[77,M,10],[86,M,10],[97,M,10],[88,M,10]]))) #87
    node_list.append(Node(np.array([[78,M,10],[87,M,10],[98,M,10],[89,M,100]]))) #88
    node_list.append(Node(np.array([[79,M,10],[88,M,10],[99,M,100]          ]))) #89
    # 9行目
    node_list.append(Node(np.array([[80,M,10],[91,M,10]]))) #90
    node_list.append(Node(np.array([[81,M,10],[90,M,10],[92,M,100]]))) #91
    node_list.append(Node(np.array([[82,M,10],[91,M,10],[93,M,10]]))) #92
    node_list.append(Node(np.array([[83,M,10],[92,M,10],[94,M,10]]))) #93
    node_list.append(Node(np.array([[84,M,10],[93,M,10],[95,M,10]]))) #94
    node_list.append(Node(np.array([[85,M,10],[94,M,10],[96,M,10]]))) #95
    node_list.append(Node(np.array([[86,M,10],[95,M,10],[97,M,10]]))) #96
    node_list.append(Node(np.array([[87,M,10],[96,M,10],[98,M,10]]))) #97
    node_list.append(Node(np.array([[88,M,10],[97,M,10],[99,M,10]]))) #98
    node_list.append(Node(np.array([[89,M,10],[98,M,10]         ]))) #99



    for gen in range(GENERATION):

      print("gen" + str(gen))

      # Antによるフェロモン付加フェーズ
      # Antを配置(ant_listにAntインスタンスを追加)
      for _ in range(ANT_NUM):
        ant_list.append(Ant(START_NODE,GOAL_NODE,[START_NODE],[]))

      # Antの移動
      for _ in range(TTL):
        ant_next_node(ant_list, node_list)

      volatilize(node_list, V)
      
      # Interestによる評価フェーズ
      # Interestを配置(interest_listにInterestインスタンスを追加)
      for _ in range(INTEREST_NUM):
        interest_list.append(Interest(START_NODE,GOAL_NODE,[START_NODE],W))

      # Interestの移動
      for _ in range(TTL):
        interest_next_node(interest_list, node_list, interest_log, gen)

    print()
    print("----------------------End Gen------------------------------")
    print()

    # show_node_info(node_list)

    print(interest_log)

    # visualize_graph(node_list)

    # visualize_interest(interest_log)

    f = open("./sample.csv", "a", newline = "")
    writer = csv.writer(f)
    writer.writerow(interest_log)
    f.close()