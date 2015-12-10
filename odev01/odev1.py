import numpy as np
import matplotlib.pyplot as P
import math
#soru1
__baseNums=[-5,1.5]
__topNums=[5,1.5]
__numberQuantity=10000
#soru2
__firstArray=np.random.normal(__baseNums[0],__baseNums[1],__numberQuantity)
__secondArray=np.random.normal(__topNums[0],__topNums[1],__numberQuantity)
__firstArray.sort()
__secondArray.sort()
sum1=0
sum2=0
#soru3
n=0
__dictHeight1={}
__dictHeight2={}
for i in range(0,__numberQuantity):
    __firstArray[i]=math.floor(__firstArray[i])
    if __firstArray[i] not in __dictHeight1:
        __dictHeight1[__firstArray[i]]=1
    else:
        __dictHeight1[__firstArray[i]]+=1
    __secondArray[i]=math.floor(__secondArray[i])
    if __secondArray[i] not in __dictHeight2:
        __dictHeight2[__secondArray[i]]=1
    else:
        __dictHeight2[__secondArray[i]]+=1
    n+=1
#x eksenini arraye yazma
__firstArrayRange=list(__dictHeight1.keys())
__firstArrayRange.sort()
__secondArrayRange=__dictHeight2.keys()
__secondArrayRange.sort()

#y eksenini normalize edip arraye ekleme
__firstArrayHeight=[]
for i in __firstArrayRange:
    __firstArrayHeight.append(__dictHeight1[i]/float(__numberQuantity))

__secondArrayHeight=[]
for i in __secondArrayRange:
    __secondArrayHeight.append(__dictHeight2[i]/float(__numberQuantity))

__destination=0
n=0
m=len(__secondArrayRange)
P.axis((-20,20,0,1))
P.bar(__firstArrayRange,__firstArrayHeight,color='green')
P.bar(__secondArrayRange,__secondArrayHeight,color='red')
P.show()
for i in __firstArrayHeight:
    while i>0:
        if n < m:
            if i <= __secondArrayHeight[n]:
                __secondArrayHeight[n]-=i
                __destination+=abs(__secondArrayRange[n])*i
                i=0
            else:
                i-=__secondArrayHeight[n]
                __destination+=abs(__secondArrayRange[n])*__secondArrayHeight[n]
                n+=1
        else:
            break
print
print "distance is",__destination