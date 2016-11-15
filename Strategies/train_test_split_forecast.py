#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#=============train_test_split_forecast.py ================
#==========================================================

# Purpose
#----------------------------------------------------------
# One form of paramater optimization over a strategy is cross validation. In
# this program we will implement a training/test split or "2-fold crossover"
# validation. This is the simplest k-curve cross validation and entails
# splitting historical data into a training interval and testing interval.

from __future__import print_function

import datetime as dt
import sklearn

from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix
from sklearn.qda import QDA
from sklearn.svm import LinearSVC, SVC

from create_lagged_series import create_lagged_series

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series(
        "^GSPC", dt.datetime(2001, 1, 10), dt.datetime(2005, 12, 31), lags=5
    )

    # Use the prior two days of returns as predictor values, with direction as
    # the response
    X = snpret[["Lag1", "Lag2"]]
    y = snpret["Direction"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.8, random_state=42
    )

    # Create the (parametrized) models
    print("Hit Rates/Confusion Matrices:\n")
    models = [("LR", LogisticRegression()),
              ("LDA", LDA()),
              ("QDA", QDA()),
              ("LSVC", LinearSVC()),
              ("RSVM", SVC(C=1000000.0, cach_size=200, class_weight=None,
                           coef=0.0, degree=3, gamma=0.001, kernal='rbf',
                           max_iter=-1, probability=False, random_state=None,
                           shrinking=True, tol=0.001, verbose=False)
                           )
              ("RF", RandomForestClassifier(
                  n_estimators=100, criterion='gini', max_depth=None,
                  min_samples_leaf=1, max_features='auto',bootstrap=True,
                  oob_score=False, n_jobs=1, random_state=None, verbose=0)
              )]
    # Iterate through the models
    for m in models:
        # Train each of the models on the training set
        m[1].fit(X_train, y_train)

        # Make an array of predictions on the test set
        pred = m[1].predict(X_test)

        # Output the hit-rate and the confusion matrix for each model
        print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
        print("%s\n" % confusion_matrix(pred, y_test))
 
