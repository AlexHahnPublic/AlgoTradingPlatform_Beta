#==========================================================
#=============== forcastingMLTechniques.py ================
#==========================================================

# Purpose
#----------------------------------------------------------
# To implement several Machine Learning techniques in hopes to create a decent
# forecaster of the SP500 series given only historical price time series. Will
# leverage: Logistic Regression, Linear Discriminant Analysis, Quadratic
# Discriminant Analysis, Linear and Non-Linear Support Vector
# Classifiers/Machines, and Random Forest techniques.

from __future__ import print_function

import datetime as dt
import numpy as np
import pandas as pd
import sklearn

from pandas.io.data import DataReader
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix
from sklearn.qda import QDA
from sklearn.svm import LinearSVC, SVC

def create_Lagged_Series(symbol, start_date, end_date, lags=5):
    """ This function will create a Pandas DataFrame that stores the percentage
    returns of the adjusted closing value of a stock (yahoo finance), along with
    a number of lag returns from previous trading days. Trading volume and the
    previous Directions will be included as well
    """

    ts = DataReader(symbol, "yahoo", start_date-dt.timedelta(days=365),
            end_date)

    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index=ts.index)
    tslag["Today"] = ts["Adj Close"]
    tslag["Volume"] = ts["Volume"]

    # Create the shifted lag series of prior trading period close values
    for i in range(0,lags):
        tslag["Lag%s" % str(i+1)] = ts["Adj Close"].shift(i+1)

    # Create the returns DataFrame
    tsret = pd.DataFrame(index=tslag.index)
    tsret["Today"] = tslag["Today"].pct_change()*100.0
    tsret["Volume"] = tslag["Volume"]
    
    # If any of the values of percentage returns equal zero, set them to a 
    # small number (prevents issues with QDA model in Scikit-Learn)
    for i,x in enumerate(tsret["Today"]):
        if (abs(x) < 0.0001):
            tsret["Today"][i] = 0.0001

    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret["Lag%s" % str(i+1)] = \
        tslag["Lag%s" % str(i+1)].pct_change()*100.0

    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[tsret.index >= start_date]

    return tsret

# TODO: refactor to take command line start and end date inputs (split as well?)
if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_Lagged_Series("^GSPC", dt.datetime(2001,1,10),
            dt.datetime(2005,12,31), lags=5)

    # Use the prior two days of return as predictor values, with the direction
    # as the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # Split the test data into two part: training data before 1/1/2005 and
    # test/results comparison data for the year after 1/1/2005
    start_test = dt.datetime(2005,1,1)

    # Create the X and y train and test sets
    X_train = X[X.index < start_test]
    X_test = X[X.index >= start_test]
    y_train = y[y.index < start_test]
    y_test = y[y.index >= start_test]

    # Create the (parametrised) models
    print("Hit Rates/Confusion Matrices:\n")
    models = [("LR", LogisticRegression()),
              ("LDA", LDA()),
              ("QDA", QDA()),
              ("LSVC", LinearSVC()),
              ("RSVM", SVC(
                  C=1000000.0, cache_size=200, class_weight=None,
                  coef0=0.0, degree=3, gamma=0.0001, kernel='rbf',
                  max_iter=-1, probability=False, random_state=None,
                  shrinking=True, tol=0.001, verbose=False)
              ),
              ("RF", RandomForestClassifier(
                n_estimators=1000, criterion='gini',
                max_depth=None, min_samples_split=2,
                min_samples_leaf=1, max_features='auto',
                bootstrap=True, oob_score=False, n_jobs=1,
                random_state=None, verbose=0)
              )]
            
    # Iterate through the models
    for m in models:
        
        # Train each of the models on the training set
        m[1].fit(X_train, y_train)
        # Make an array of predictions on the one year test set
        pred = m[1].predict(X_test)

        # Output the hit-rate and the confusion matrix for each model
        print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
        print("%s\n" % confusion_matrix(pred, y_test))

