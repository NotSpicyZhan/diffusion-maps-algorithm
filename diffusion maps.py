
# coding: utf-8

# In[19]:

get_ipython().magic(u'matplotlib inline')
import numpy as np
from numpy import linalg as LA
from PIL import Image
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import os, math

newDim = 64

def normalize(arr):
    arr=arr.astype('float32')
    if arr.max() > 1.0:
        arr/=255.0
    return arr

def weightedAverage(pixel):
    return 0.299*pixel[0] + 0.587*pixel[1] + 0.114*pixel[2]

def getImgData(path, preview=True):
    filelist = os.listdir( path )
    imglist = []
    for filename in filelist:
        img = Image.open(path+filename)
        img = img.resize((newDim,newDim))
        img = np.asarray(img)

        grey = np.zeros((img.shape[0], img.shape[1])) # init 2D numpy array
        for rownum in range(len(img)):
            for colnum in range(len(img[rownum])):
                grey[rownum][colnum] = weightedAverage(img[rownum][colnum])

        grey = normalize(grey)
        imglist.append(grey)

    data=[]
    for img in imglist:
        vector = img.flatten()
        data.append(vector)

    if preview:
        for img in imglist:
            plt.imshow(img, cmap = cm.Greys_r)
            plt.show()
        
    return data


# In[20]:

def diffusionMapping(data, k, t, **kwargs):
    try:
        kwargs['dim'] or kwargs['delta']
    except KeyError:
        raise KeyError('specify either dim or delta as keyword argument!')
    
    dataList=[] # create list whose indices will serve as references for the vectors from now on
    for x in data:
        dataList.append(x)
    X = range(len(dataList))
    
    # construct Markov matrix
    v = []
    for x in X:
        vx = 0
        for y in X:
            _x = np.array(dataList[x])
            _y = np.array(dataList[y])
            vx += k(_x,_y)
        v.append(math.sqrt(vx))
            
    a = []
    for x in X:
        a.append([])
        for y in X:
            _x = np.array(dataList[x])
            _y = np.array(dataList[y])
            a[x].append(k(_x,_y)/(v[x]*v[y]))
    
    # compute eigenvectors of (a_ij)
    phi = []
    eigval, eigvec = LA.eigh(np.array(a))
    for i in range(len(eigvec)):
        phi.append(eigvec[:, i])
    #reverse order
    eigval[:] = eigval[::-1]
    phi[:] = phi[::-1]
    
    # compute embedding coordinates
    Psi = []
    for x in X:
        Psi.append([])
        for j in range(kwargs['dim']):
            i=j+1 #ignore the first eigenvector/value as this is only constant
            Psi[x].append((eigval[i]**t)*phi[i][x]/v[x])
    return (Psi, dataList)


# In[27]:

data = getImgData("_img/", False)


# In[25]:

coordinates, dataList = diffusionMapping(data, lambda x,y: math.exp(-LA.norm(x-y)/1024), 1,dim=2)
a = np.asarray(coordinates)
x = a[:,0]
y = a[:,1]
plt.plot(x, y, 'ro')
labels = ['image {0}'.format(i+1) for i in range(len(x))]
for label, xpt, ypt in zip(labels, x, y):
    plt.annotate(
        label,
        xy = (xpt, ypt), xytext = (-20, 20),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'white', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
plt.show()

