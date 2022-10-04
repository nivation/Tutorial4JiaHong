# 
# target = 100
# a = random.random() # 0-1 float

# for i in range(target):
    # b = random.randint(0,100)# Int  
    # print(b)
    
    
#我要知道有幾個水
file_path = "../2_Solute/solvate.out"

with open(file_path,'r') as f:
    for line in f.readlines():
        if "Waters:" in line:
            temp = line.split()
            total_num_water = int(temp[-1]) # string
            
# 找A B
KEMA = 1
GCMA = 1
#水開始
W_start = KEMA+GCMA
W_end   = W_start + total_num_water

print(W_start,W_end)


import numpy as np
water_list = np.arange(W_start,W_end)
print(water_list)


import random
random.shuffle(water_list)

print()

print(water_list)

goal = 100
print(water_list[0:goal])
final = water_list[0:goal]


#自動化的產生tcl檔

text = ""
for i in range(len(final)):
    print(final[i])
    text = text + str(final[i]) + ' '


print(text)
with open("Delete_water_2.tcl",'w') as f:
    f.writelines("mol load psf solvate.psf pdb solvate.pdb\n")
    line = 'set a [atomselect top " fragment 0 to ' + str(KEMA+GCMA) + ' or fragment ' + text +'"]\n'
    f.writelines(line)
    f.writelines("$a writepdb solvate_delete.pdb          \n")
    f.writelines("$a writepsf solvate_delete.psf          ")


#set a [atomselect top " fragment 0 to 8 or fragment 32147 21373 48544 22888 52984 4888 21090 21593 48734 51078 18584 50116 29270 7649 11726 27124 8395 24559 39366 5845 40736 11000 3481 25541 3473 43768 48267 1689 3640 42812 20666 44465 "]
