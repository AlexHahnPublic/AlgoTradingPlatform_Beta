#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#================== k_fold_cross_val.py ===================
#==========================================================

# Purpose
#----------------------------------------------------------
# Rather than partitioning a set into a single training and test set we can use
# k-fold cross validation to randomly partition the set into k equally sized
# subsample. This will be a k-fold cross validation implementation on the
# S&P500 forecaster

from __future__ import print_function

import datetime as dt

import pandas as pd
import sklearn
from sklearn import cross_validation
from sklearn.metrics import confusion matrix
from sklearn.svm import SVC

from create_lagged_series import create_lagged_series

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series(
        "^GSPC", dt.datetime(2001,1,10), dt.datetime(2005,12,31), lags=5
    )

    # Use the prior two dayes of returns as predictor values, with direction as
    # the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # Create a k-fold cross validation object
    kf = cross_validation.KFold(
        len(snpret), n_folds=10, indeces=False, shuffle=True, random_state=42
    )

    # Use the kf object to create index arrays that state which elements have
    # been retained for training and which elements have been retained for
    # testing each k-element iteration
    for train_index, test_index in kf:
        X_train = X.ix[X.index[train_index]]
        X_test = X.ix[X.index[test_index]]
        y_train = y.ix[y.index[train_index]]
        y_test = y.ix[y.index[test_index]]

        # In this instance only use the Radial Support Vector Machine (SVM)
        print("Hit Rate/Confusion Matrix:")
        model = SVC(
            C=1000000.0, cache_size=200, class_weight=None, coef0=0.0,
            degree=3, gamma=0.0001, kernal='rbf', max_iter=-1,
            probability=False, random_state=None, shrinking=True, tol=0.001,
            verbose=False
        )

        # Train the model on the retained training data
        model.fit(X_train, y_train)

        # Make an array of predictions on the test set
        pred = model.predict(X_test)

        # Output the hit-rate and the confusion matrix for each model
        print("%0.3f" % model.score(X_test, y_test))
        print("%s\n" % confusion_matrix(pred, y_tst))

