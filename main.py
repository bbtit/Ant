import math
import random
import numpy as np

N=10 # 総ノード数(実際は最初に用意する２つのノードで+2)
V=0.9 # フェロモン揮発量
M=10 # フェロモン最小値
F=0.1 # フェロモン値決定用定数
TTL=20 # 蟻のTime to Live
W=1000 # 帯域幅初期値
node_list=[] # Nodeオブジェクト格納リスト
ant_list=[] # Antオブジェクト格納リスト
interest_list=[] # Interestオブジェクト格納リスト
edge=[] # networkxで表示するためのエッジリスト


class Node():
  def __init__(self,connection):
    # 経路表として[接続先ノード,フェロモン,帯域幅]のセットを二次元配列で保持
    self.connection = connection

class Ant():
  def __init__(self,current,destination,route,minwidth):
    self.current = current # 現在のノード
    self.destination = destination # 目的ノード(コンテンツ保持ノード)
    self.route = route # 辿ってきた経路の配列
    self.minwidth = minwidth # 辿ってきた経路の最小帯域

class Interest():
  def __init__(self,current,destination,route,minwidth):
    self.current = current # 現在のノード
    self.destination = destination # 目的ノード(コンテンツ保持ノード)
    self.route = route # 辿ってきた経路の配列
    self.minwidth = minwidth # 辿ってきた経路の最小帯域

#---------------------------------------------------

def create_ba(node_list,N):
  # baモデルを作成する関数
  # 事前準備　２つのノードからなる完全グラフを用意
  node_list.append(Node(np.array[[1,M,random.randint(1,100)]]))
  node_list.append(Node(np.array[[0,M,random.randint(1,100)]]))

  for _ in range(N):
    candidacy_list=[] # 接続先ノードの候補リスト

    for i in range(len(node_list)):
      # 次数(接続ノードの数)の分だけ接続先ノード候補リストにノード番号を追加
      tmp_list=[i]*len(node_list[i].connection)
      candidacy_list.extend(tmp_list)

    # 接続先ノードをランダムに選択
    select_node = random.choice(candidacy_list)
    # 帯域幅をランダムに決定
    width=random.randint(1,random.randint(1,100))
    # 接続先ノードのconnection属性に新規ノード追加
    node_list[select_node].connection == np.append(node_list[select_node].connection, [len(node_list),M,width], axis=0)
    # 新規ノードをnode_listに追加
    node_list.append(Node(np.array[[select_node,M,width]]))

def volatilize(node_list,V):
  # node_listの全nodeのフェロモンをV倍する関数 フェロモンの揮発に相当
  # 最小フェロモン量を下回らないように(未実装)
  for node in node_list:
    for j in range(len(node.connection)):
      node.connection[j][1]=math.floor(node.connection[j][1]*0.9)

def update_pheromone(ant,node_list):
  # 目的ノードに到着したantによるフェロモンの付加(両側)
  for i in range(1,len(ant.route)):
    # ant.routeのi-1番目とi番目のノードを取得
    before_node = node_list[ant.route[i-1]]
    after_node = node_list[ant.route[i]]

    # ant.routeのi-1番目からi番目のedgeのフェロモン値を変更
    # bofore_nodeのconnectionの0列目を取得
    before_line0 = before_node.connection[:,0]
    # before_nodeのconnectionからafter_node番号の行を探索
    row = np.where(before_line0 == ant.route[i])[0][0]
    # i-1番ノードからi番ノードのフェロモン値を最小帯域を元に変更
    before_node.connection[row][1] += (F * ant.minwidth)

    # ant.routeのi番目からi-1番目のedgeのフェロモン値を変更
    # after_nodeのconnectionの0列目を取得
    after_line0 = after_node.connection[:,0]
    # after_nodeのconnectionからbefore_node番号の行を探索
    row = np.where(after_line0 == ant.route[i-1])[0][0]
    # i番ノードからi-1番ノードのフェロモン値を最小帯域を元に変更
    after_node.connection[row][1] += (F * ant.minwidth)

def ant_next_node(ant_list,node_list):
  # antの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for ant in reversed(ant_list):
    # antが今いるノードの接続ノードとフェロモン値を取得
    line0 = node_list[ant.current].connection[:,0]
    line1 = node_list[ant.current].connection[:,1]
    # 次のノード番号をl1の重みづけでl0からランダムに選択
    next_node=random.choices(line0,k=1,weights=line1)[0]
    # 次のノード番号がconnect1列目の何行目か探索
    row = np.where(line0 == next_node)[0][0]

    # antの属性更新
    # もし現在ノードから次ノードの帯域幅が今までの最小帯域より小さかったら更新
    if node_list[ant.current].connection[row][2] < ant.minwidth:
      ant.minwidth = node_list[ant.current].connection[row][2]
    ant.current = node_list[ant.current].connection[row][0]
    ant.route.append(next_node)

  # 蟻が目的ノードならばノードにフェロモンの付加後ant_listから削除
    if ant.current==ant.destination:
      update_pheromone(ant,node_list)
      ant_list.remove(ant)
      print(ant.route)

  # 蟻がTTLならばant_listから削除
    if (len(ant.route)==TTL):
      ant_list.remove(ant)
      print(ant.route)

def interest_next_node(interest_list,node_list):
  # interestの次のノードを決定
  # 繰り返し中にリストから削除を行うためreversed
  for interest in reversed(interest_list):
    # interestが今いるノードの接続ノードとフェロモン値を取得
    line0 = node_list[interest.current].connection[:,0]
    line1 = node_list[interest.current].connection[:,1]
    # 次のノード番号をl1の重みづけでl0からランダムに選択
    next_node=random.choices(line0,k=1,weights=line1)[0]
    # 次のノード番号がconnect1列目の何行目か探索
    row = np.where(line0 == next_node)[0][0]

    # interestの属性更新
    # もし現在ノードから次ノードの帯域幅が今までの最小帯域より小さかったら更新
    if node_list[interest.current].connection[row][2] < interest.minwidth:
      interest.minwidth = node_list[interest.current].connection[row][2]
    interest.current = node_list[interest.current].connection[row][0]
    interest.route.append(next_node)

  # interestが目的ノードならばノードにフェロモンの付加後interest_listから削除
    if interest.current==interest.destination:
      update_pheromone(interest,node_list)
      interest_list.remove(interest)
      print(interest.route)
      print(interest.minwidth)

  # interestがTTLならばinterest_listから削除
    if (len(interest.route)==TTL):
      interest_list.remove(interest)
      print(interest.route)
      print(interest.minwidth)

def show_node_info(node_list):
  for i in range(len(node_list)):
    print(node_list[i].connection)

#---------------------------------------------------

if __name__ == "__main__":

  #4×4のネットワークを生成
  node_list.append(Node(np.array([[1,M,random.randint(1,100)],[4,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[0,M,random.randint(1,100)],[5,M,random.randint(1,100)],[2,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[1,M,random.randint(1,100)],[6,M,random.randint(1,100)],[3,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[2,M,random.randint(1,100)],[7,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[0,M,random.randint(1,100)],[5,M,random.randint(1,100)],[8,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[1,M,random.randint(1,100)],[4,M,random.randint(1,100)],[6,M,random.randint(1,100)],[9,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[2,M,random.randint(1,100)],[5,M,random.randint(1,100)],[7,M,random.randint(1,100)],[10,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[3,M,random.randint(1,100)],[6,M,random.randint(1,100)],[11,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[4,M,random.randint(1,100)],[9,M,random.randint(1,100)],[12,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[5,M,random.randint(1,100)],[8,M,random.randint(1,100)],[10,M,random.randint(1,100)],[13,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[6,M,random.randint(1,100)],[9,M,random.randint(1,100)],[11,M,random.randint(1,100)],[14,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[7,M,random.randint(1,100)],[10,M,random.randint(1,100)],[15,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[8,M,random.randint(1,100)],[13,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[9,M,random.randint(1,100)],[12,M,random.randint(1,100)],[14,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[10,M,random.randint(1,100)],[13,M,random.randint(1,100)],[15,M,random.randint(1,100)]])))
  node_list.append(Node(np.array([[11,M,random.randint(1,100)],[14,M,random.randint(1,100)]])))


  for _ in range(20):
    ant_list.append(Ant(0,15,[0],W))

  for _ in range(20):
    ant_next_node(ant_list, node_list)

  show_node_info(node_list)

  volatilize(node_list,V)
  print("volatilize!")

  show_node_info(node_list)

  for _ in range(10):
    interest_list.append(Interest(0,15,[0],W))
  
  for _ in range(20):
    interest_next_node(interest_list, node_list)

