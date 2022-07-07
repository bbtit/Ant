import networkx as nx
import matplotlib.pyplot as plt

# Graphオブジェクトの作成
G = nx.Graph()
 
# nodeデータの追加
G.add_nodes_from(["A", "B", "C", "D", "E", "F"])
 
# edgeデータの追加
G.add_edges_from([("A", "B"), ("B", "C"), ("B", "F"),("C", "D"), ("C", "E"), ("C", "F"), ("B", "F")])
 
# ネットワークの可視化
nx.draw(G, with_labels = True)
plt.show()