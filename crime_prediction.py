# -*- coding: utf-8 -*-
"""Crime Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16ucAuwZUNACaPnD5m7gUlkt5VCD-xRTx

# using tensorflow 1.14.0
"""

!pip uninstall tensorflow
!pip install tensorflow==1.14.0

"""# **importing the required libraries**"""

# Commented out IPython magic to ensure Python compatibility.
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Flatten,Input
from keras import backend as K
from keras.models import Model, load_model
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
from scipy.spatial import distance
from sklearn.decomposition import PCA
from numpy import linalg as LA
from keras.objectives import categorical_crossentropy
from sklearn.metrics import roc_curve, auc
import math
from scipy.stats import pearsonr
import copy
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import itertools
import csv
from sklearn import metrics
import tensorflow as tf
import tensorflow.contrib.layers as tl
import numpy as np
import pandas as pd 
from sklearn import linear_model
from sklearn.ensemble import RandomForestClassifier
import seaborn as sb
# %matplotlib inline

"""# loading the dataset"""

X = pd.read_csv('/content/drive/My Drive/Crime Prediction/crime_prep.csv',delimiter=',')
print(X.shape)
X[0:5]

"""# **Data Cleaning**

Missing data can either be filled with the means of the features or maybe 0 to ignore them or even other data imputation techniques to predict the missing values
In this case the mean of the features is taken for the missing values.
"""

print(len(X['v_cat_2'].unique()))
X = X.fillna(X.mean())
del X['v_cat_2']
del X['v_cat_3']
Y = X['target']
del X['target']
X.head()

"""# Standardise v_cont_0, v_cat_0, v_cat_1 columns"""

X['v_cat_0'] = StandardScaler().fit_transform(X['v_cat_0'].values.reshape(-1, 1))
X['v_cat_1'] = StandardScaler().fit_transform(X['v_cat_1'].values.reshape(-1, 1))
X['v_cont_0'] = StandardScaler().fit_transform(X['v_cont_0'].values.reshape(-1, 1))
X.head()

"""# **Principal Component Analysis**"""

print(X.shape)
X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size = 0.3,random_state=42)

Covariance = np.dot(X_train.T,X_train)
print(Covariance.shape)

Lambda, e = LA.eigh(Covariance)
Lambda = Lambda.reshape(Lambda.shape[0],1)
Lambda = sorted(Lambda,reverse=True)
TotalLambda = np.sum(Lambda)
LambdaProp = []
for i in range(X_train.shape[1]):
    temp = np.sum(Lambda[0:i])*1.0/TotalLambda
    LambdaProp.append(temp)

Dim = np.linspace(0, X_train.shape[1], X_train.shape[1])

plt.plot(Dim,LambdaProp)
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.xlabel('Dimensions')
plt.ylabel('Lambda/TotalLambda')
plt.show()

X1 = X
Y1 = Y

for i in (range(1,100)):
    print(i)
    NewFeatureSet = np.dot(X1,e[:,125-i:125])
    print (NewFeatureSet.shape)
    X_train,X_test,Y_train,Y_test = train_test_split(NewFeatureSet,Y1,test_size = 0.2,random_state=42)
    #Normal Linear Regression
    regr = linear_model.LinearRegression(normalize = True)
    regr.fit(X_train,Y_train)
    Y_pred = regr.predict(X_test)
    Weights = regr.coef_
    print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
    print('Variance/R2 score: %.2f' % r2_score(Y_test, Y_pred))

X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size = 0.3,random_state=42)
RMSETrain =[]
RMSETest =[]
VarainceRatio = []
Dim = np.linspace(0, X_train.shape[1], X_train.shape[1])
for i in range(1,X_train.shape[1]+1):
    pca = PCA(n_components = i)
    pca.fit(X_train)
    VarainceRatio.append(pca.explained_variance_ratio_)
    X_trainhat = np.dot(pca.transform(X_train)[:,:i], pca.components_[:i,:])
    RMSETrain.append(math.sqrt(mean_squared_error(X_train,X_trainhat)))
    X_testhat = np.dot(pca.transform(X_test)[:,:i], pca.components_[:i,:])
    RMSETest.append(math.sqrt(mean_squared_error(X_test,X_testhat)))
    
plt.plot(Dim,RMSETrain,label="RMSE Train")
plt.plot(Dim,RMSETest,label="RMSE Test")
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.xlabel('Dimensions')
plt.ylabel('Reconstruction Loss RMSE')
plt.show()

X1 = X
Y1 = Y
for i in range(1,15):
    pca = PCA(n_components = i)
    X_1 = pca.fit_transform(X1)
    #VarainceRatio.append(pca.explained_variance_ratio_)
    print (X_1)
    print ("no of componenets",i)
    print ("predict for transformed data")
    
    X_train,X_test,Y_train,Y_test = train_test_split(X_1,Y1,test_size = 0.2,random_state=42)
    #Normal Linear Regression
    regr = linear_model.LinearRegression(normalize = True)
    regr.fit(X_train,Y_train)
    Y_pred = regr.predict(X_test)
    Weights = regr.coef_
    print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
    print('Variance/R2 score: %.2f' % r2_score(Y_test, Y_pred))

"""Feature engineering using **Pearson**'**s** **Coefficient**"""

X = (X - X.mean())
Matrix = X.values
#print TrainX['ALSQM_Count']
r=[]
p=[]
for i in range(X.shape[1]):
    t1,t2 = pearsonr(Matrix[:,i],Y)
    #print t1,i,
    r.append((t1,i,X.columns[i],t2))
r.sort()

frequencies = []
labels =[]
count=0
for ind,x in enumerate(r):
    if(x[0]<-0.4 or x[0]>0.4):
        frequencies.append(x[0])
        labels.append(x[2])
    else:
        if count<10:
            labels.append('-')
            frequencies.append(0.01)
            count+=1
print (len(frequencies))
freq_series = pd.Series(frequencies)
x_labels = range(len(freq_series))
plt.figure(figsize=(15, 10))
ax = freq_series.plot(kind='bar')
ax.set_title('Correlation between Dependent and Indpendent variables')
ax.set_xlabel('Features Columns')
ax.set_ylabel('Pearson Correlation Score')
rects = ax.patches
ax.set_xticklabels(labels)
plt.show()

IndList =[]
for ind,x in enumerate(r):
    if(x[0]<-0.4 or x[0]>0.4):
        IndList.append(x[1])
CorrList =[]
CorrMatrix = np.zeros((len(IndList),len(IndList)))
Cols =[]
for i in range(len(IndList)):
    Cols.append(X.columns[IndList[i]])
    for j in range(len(IndList)):
        t1,t2 = pearsonr(Matrix[:,IndList[i]],Matrix[:,IndList[j]])
        CorrList.append((t1,IndList[i],X.columns[IndList[i]],IndList[j],X.columns[IndList[j]],t2))
        CorrMatrix[i][j] = t1
print (CorrMatrix.shape)

fig, ax = plt.subplots(figsize=(20,20)) 
sb.heatmap(CorrMatrix, 
        xticklabels=Cols,
        yticklabels=Cols,linewidths=1,annot=True, ax=ax,square =True)

plt.show()

"""# **Model Development and Performance**"""

print (IndList)
t=[]
for i in IndList:
    t.append(X.columns[i])
print (t)
FinalTrainSet = np.zeros((len(IndList),Matrix.shape[0]))
for ind,i in enumerate(IndList):
    FinalTrainSet[ind] = (Matrix[:,i])
FinalTrainSet = FinalTrainSet.T
print (FinalTrainSet.shape)
print (Y.shape)

"""# **Linear Regression**"""

X_train,X_test,Y_train,Y_test = train_test_split(FinalTrainSet,Y,test_size = 0.3,random_state=42)
#Normal Linear Regression
clf = linear_model.LinearRegression(normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
Weights = clf.coef_
print (Weights)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance/R2 score: %.2f' % r2_score(Y_test, Y_pred))

# Linear Regression With Ridge regularisation
clf = linear_model.Ridge(alpha = 0.1,normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance/R2 score: %.2f' % r2_score(Y_test, Y_pred))


# Linear Regression With Lasso regularisation
clf = linear_model.Lasso(alpha = 0.1,normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance/R2 score: %.2f' % r2_score(Y_test, Y_pred))

"""# **Neural Nets**"""

X_train,X_test,Y_train,Y_test = train_test_split(FinalTrainSet,Y,test_size = 0.3,random_state=42)
InputWidth = X_train.shape[1]
K.clear_session()
model = Sequential()
model.add(Dense(128, input_shape = (InputWidth,), activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1, activation='relu'))
#model.add(Dense(InputWidth, activation='relu'))
print (model.summary())
# Compile model
model.compile(loss='mean_squared_error', optimizer='sgd', metrics=['accuracy'])
op = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), nb_epoch=150, batch_size=64, verbose=2).history
y_pred = model.predict(X_test)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance score: %.2f' % r2_score(Y_test, Y_pred))

"""# FNN (Feedforward Neural Networks) doesnt perform as well possibly due to the limited number of training samples"""

HighCorrTuples =[]
LowCorrTuples=[]
Col =[]
ht ={}
CorrCopy = copy.deepcopy(CorrList)
for var in CorrCopy:
    if((var[0]>=0.8 or var[0]<=-0.8) and var[1]!=var[3]):
        if(var[1] not in ht or var[3] not in ht):
            print (var)
            ht[var[3]] =0
    else:
        LowCorrTuples.append(var)
print (len(ht))
FinalFeatureSet =[]
print (len(CorrCopy))
for index,var in enumerate(CorrCopy):
    if(not(var[1] in ht or var[3] in ht)):
        #print var
        FinalFeatureSet.append(var)
print (len(CorrList))
print (len(CorrCopy))
print (len(FinalFeatureSet))

Indfor ={}
for ind,x in enumerate(FinalFeatureSet):
    if(x[1] not in Indfor):
        Indfor[x[1]] = x[1]
print (len(Indfor))
IndforCor =[]
for key,val in Indfor.items():
    IndforCor.append(val)
Cols=[]
FinalcorMatrix = np.zeros((len(Indfor),len(Indfor)))
for i in range(FinalcorMatrix.shape[0]):
    Cols.append(X.columns[IndforCor[i]])
    for j in range(FinalcorMatrix.shape[1]):
        t1,t2 = pearsonr(Matrix[:,IndforCor[i]],Matrix[:,IndforCor[j]])
        FinalcorMatrix[i][j] = t1
        
fig, ax = plt.subplots(figsize=(20,20)) 
sb.heatmap(FinalcorMatrix, 
        xticklabels=Cols,
        yticklabels=Cols,linewidths=1,annot=True, ax=ax,square =True)

plt.show()

print(IndforCor)

"""# **Linear regression on the remaining features**"""

FinalTrainSetForTrain = np.zeros((3,Matrix.shape[0]))
for ind,k in enumerate(IndforCor):
    FinalTrainSetForTrain[ind] = (Matrix[:,k]) 
FinalTrainSetForTrain = FinalTrainSetForTrain.T
X_train,X_test,Y_train,Y_test = train_test_split(FinalTrainSetForTrain,Y,test_size = 0.3,random_state=42)
#Normal Linear Regression

clf = linear_model.LinearRegression(normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
Weights = clf.coef_
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance score: %.2f' % r2_score(Y_test, Y_pred))

# Linear Regression With Ridge regularisation
clf = linear_model.Ridge(alpha = 0.1,normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance score: %.2f' % r2_score(Y_test, Y_pred))


# Linear Regression With Lasso regularisation
clf = linear_model.Lasso(alpha = 0.1,normalize = True)
clf.fit(X_train,Y_train)
Y_pred = clf.predict(X_test)
print ("RMSE %.2f" % math.sqrt(mean_squared_error(Y_test,Y_pred)))
print('Variance score: %.2f' % r2_score(Y_test, Y_pred))