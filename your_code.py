N = int(input())
my_list = []
for i in range(6):
    number = (N // 10**i) % 10
    my_list.append(number)
if sum(my_list[:3]) == sum(my_list[3:]):
    print("YES")
else:
    print("NO")