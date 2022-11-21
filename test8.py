class Car():
  def __init__(self,id):
    self.id = id

# def change_id(car_list):
#   for car in car_list:
#     car.id = 2

# car_list = [Car(1)]

# print(car_list[0])

# change_id(car_list)

# print(car_list[0].id)

#--------------------------------

# a = 10

# def change_num(num):
#   num = 20

# print(a)

# change_num(a)

# print(a)

#--------------------------------
a = []

a.extend([Car(1)]* 10)

print(len(a))
