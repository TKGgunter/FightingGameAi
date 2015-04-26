# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 22:16:04 2014

@author: tgunter
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import preprocessing
from sklearn import svm as SVM
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
from sklearn.externals import joblib

def loadData(numberFiles=1):
    data = np.array([])
    for n in range(0, numberFiles):
        fileName = "Training/ThothvAiRyu_DeeJay_%s.txt"% n
        data_ = np.loadtxt(open(fileName, "r"), delimiter=" , ", skiprows= 0 , dtype=np.float64)
        if n != 0:
            data = np.concatenate((data, data_), 0)
        else:
            data = data_
    return data
    
def trainCLF(numberOfClassifications = 2):
    data = loadData(9)
    print data.shape
    featureNumb = data[1].shape[0] - numberOfClassifications
    X = data[:,:featureNumb]
    Y = data[:, featureNumb]
    print Y
    rfc = RandomForestClassifier(n_estimators=100)
    rfc= rfc.fit(X,Y)
    return rfc
    
def trainCombinedCLF(numberOfClassifications = 2):
    data = loadData(2)
    print data.shape
    featureNumb = data[1].shape[0] - numberOfClassifications
    X = data[:, :featureNumb]
    X_ = []
    Y_ActionClass = data[:, featureNumb+1]
    Y_ButtonClass = []

    rfc_Action = RandomForestClassifier(n_estimators = 100)
    rfc_Action = rfc_Action.fit(X, Y_ActionClass)
    
    rfc_Button = RandomForestClassifier(n_estimators = 100)
    
    i_ = 0
    for i in range(0, data.shape[0]):
        if rfc_Action.predict(X[i]) == 1:
        #concate predicted X into new training set
            print X[i]
            if i_ == 0:
                X_ = X[i]
                Y_ButtonClass = Y_ActionClass[i]
            else:
                X_ = np.vstack((X_, X[i]))
            Y_ButtonClass = np.append(Y_ButtonClass, Y_ActionClass[i])
    
    print Y_ButtonClass.shape
    print X_.shape
    
    rfc_Button = rfc_Button.fit(X_, Y_ButtonClass)
    
    return rfc_Action, rfc_Button
        
    
def trainAndTest():
    data = loadData(5)
    print data.shape
    X = data[:,:80]
    Y = data[:,80]
    print Y
    rfc = RandomForestClassifier(n_estimators=5)
    rfc= rfc.fit(X,Y)
    print rfc
    
    joblib.dump(rfc, 'Classes/rfcTest.pkl') 
    rfc1= joblib.load('Classes/rfcTest.pkl')
    #pickle.dump(rfc, open("rfc_test.pkl", "wb"))
"""    score = cross_val_score(rfc, X, Y)
    print "Random Forest", score

    X_scale = preprocessing.scale(X)   
    svm = SVM.SVC()
    
    print cross_val_score(svm, X_scale, Y)
    
    #personal cross-validation test
    
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.33, random_state = 42)
    rfc = rfc.fit(X_train, Y_train)
    Y_pred = rfc.predict(X_test)
    print classification_report(Y_test, Y_pred)
    """
    
    