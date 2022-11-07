class Item():
  def __init__(self,attr1,attr2,attr3):
    self.attr1 = attr1
    self.attr2 = attr2
    self.attr3 = attr3

item_list = []

item_list.append(Item(1,2,3)) #No.0
item_list.append(Item(0,2,3)) #No.1

for item in reversed(item_list):
  print("------------------------------------")
  print("item No." + str(item_list.index(item)))

  if item.attr1 == 1:
    print("if 1 → true")
  
  if item.attr2 == 2:
    print("if 2 → true")
    item_list.remove(item)
  
  elif item.attr3 == 3:
    print("if 3 → true")
    item_list.remove(item)

  print("length: " + str(len(item_list)))
