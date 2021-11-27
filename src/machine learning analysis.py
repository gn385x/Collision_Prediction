# author: Siqi Tao
# date: 2021-11-26

"""Downloads data as a csv file from online to a local filepath via a URL.
Usage: download_script.py --url=<url> --filepath=<filepath> 
 
Options:
--data=<data>       The path or filename pointing to the data
--prefix=<prefix>   The prefix where to write the output figure(s)/table(s) to and what to call it 
"""

import os
import pandas as pd
from docopt import docopt

import os
import string

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import RFE, RFECV
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge, RidgeCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    ShuffleSplit,
    cross_val_score,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    PolynomialFeatures,
    StandardScaler,
)
from sklearn.svm import SVC, SVR
from scipy.stats import loguniform

# Function copied from DSCI571 note
def mean_std_cross_val_scores(model, X_train, y_train, **kwargs):
    """
    Returns mean and std of cross validation

    Parameters
    ----------
    model :
        scikit-learn model
    X_train : numpy array or pandas DataFrame
        X in the training data
    y_train :
        y in the training data

    Returns
    ----------
        pandas Series with mean scores from cross_validation
    """

    scores = cross_validate(model, X_train, y_train, **kwargs)

    mean_scores = pd.DataFrame(scores).mean()
    std_scores = pd.DataFrame(scores).std()
    out_col = []

    for i in range(len(mean_scores)):
        out_col.append((f"%0.3f (+/- %0.3f)" % (mean_scores[i], std_scores[i])))

    return pd.Series(data=out_col, index=mean_scores.index)

opt = docopt(__doc__)

def main(): 
    df = opt["--data"]
    X_train = train_df[["C_WTHR", 'C_RCFG', 'C_MNTH', 'V_TYPE', 'P_AGE']]
    X_test = df.drop(columns=["P_ISEV"])
    
    y_train = train_df["P_ISEV"]
    y_test = df["P_ISEV"]
    
    categorical_feats = ["C_WTHR", 'C_RCFG', 'C_MNTH', 'V_TYPE', 'P_AGE']
    preprocessor = make_column_transformer(
        (OneHotEncoder(handle_unknown="ignore", sparse=False), categorical_feats),
    )
    
    preprocessor.fit(X_train)
    
    columns = list(
        preprocessor.named_transformers_["onehotencoder"].get_feature_names_out(
            categorical_features
        )
    )
    
    # Pipeline including OneHotEncoder and LogisticRegression
    pipe = make_pipeline(
        OneHotEncoder(handle_unknown="ignore", sparse=False), 
        LogisticRegression(max_iter=2000)
    )
    
    # Hyperparameter tuning using RandomSearchCV 
    param_grid = {
        "logisticregression__C": loguniform(1e-3, 1e3),
    }
    
    # Scoring include f1, recall, precision. 
    results = {}
    scoring = [
        "f1", 
        "recall", 
        "precision", 
        "roc_auc", 
        "average_precision"
    ]
    results["Logistic Regression"] = mean_std_cross_val_scores(pipe, X_train, y_train, scoring=scoring)
    result_df = pd.DataFrame(results)
    

    

    # Feature selection using pipeline including OneHotEncoder, RFECV, LogisticRegression.
    
if __name__ == "__main__":
    main() 