import networkx as nx
import matplotlib.pyplot as plt

# Graphオブジェクトの作成
G = nx.Graph()
 
# nodeデータの追加
G.add_nodes_from([1, 2, 3, 4, 5, 6])
 
# edgeデータの追加
G.add_edges_from([(1, 2), (2, 3), (2, 6),(3, 4), (3, 5), (3, 6), (2, 6)])
 
# ネットワークの可視化
nx.draw(G, with_labels = True)
plt.show()