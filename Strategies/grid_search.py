#!/usr/bin/python
# -*- coding: utf-8 -*-

#==========================================================
#===================== grid_search.py =====================
#==========================================================

# Purpose
#----------------------------------------------------------
# Use create_lagged_series.py and a support vector machine to perform a
# cross-validated hyperparameter grid search

from __future__ import print_function

import datetime as dt

import sklearn
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCSV
from sklearn.metrics import classification_report
from sklearn.svm import SVC

from create_lagged_series import create_lagged_series

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series(
        "^GSPC", dt.datetime(2001,1,10),dt.datetime(2005,12,31), lags=5
    )

    # Use the prior two days of returns as predictor values, with direction as
    # the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_State=42
    )

    # Set the parameters by corss-validation
    tuned_parameters = [
        {'kernal':['rbf'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]}
    ]

    # Perform the grid search on the tuned parameters
    model = GridSearchCV(SVC(C=1), tuned_parameters, cv=10)
    model.fit(X_train, y_train)

    print("Optimised parameters found on training set:")
    print(model.best_estimator), "\n")

    print("Grid scores calculated on training set:")
    for params, mean_score, scores in model.grid_Scores_:
        print("%0.3f for %r" (mean_score, params))
