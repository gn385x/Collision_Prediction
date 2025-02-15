# author: DSCI-522 Group-21
# date: 2021-11-26

"""Perform machine learning analysis on the cleaned data
Usage: model.py --input=<input>  --output=<output> 
 
Options:
--input=<input>       The path or filename pointing to the data
--output=<output>     Directory specifying where to store output figure(s)/table(s)
"""

import os
import pandas as pd
from docopt import docopt

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV, cross_val_score, cross_validate
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder
from scipy.stats import loguniform
from sklearn.metrics import confusion_matrix
import pickle
import imblearn
from imblearn.pipeline import make_pipeline as make_imb_pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.dummy import DummyClassifier

opt = docopt(__doc__)


def main(input, output):

    # Get data
    train_df = (
        pd.read_csv(f"{input}", low_memory=False)
        .set_index("index")
        .rename_axis(None)
    )
    X_train = train_df.drop(columns=["FATALITY"])
    y_train = train_df["FATALITY"]

    # Convert columns into string data type
    X_train = X_train.astype("string")

    # Create pipeline containing the baseline model
    # Using undersampling to address class imbalance
    dummy_pipe = make_imb_pipeline(
        RandomUnderSampler(random_state=21),
        OneHotEncoder(handle_unknown="ignore", sparse=False),
        DummyClassifier()
    )

    # Create list of desired scoring metrics
    scoring_metrics = ["accuracy", "f1", "recall", "precision", "average_precision"]

    # Determine CV scores of baseline model
    results = {}
    results["Dummy Classifier"] = mean_std_cross_val_scores(
        dummy_pipe, X_train, y_train, scoring=scoring_metrics
    )

    # Pipeline including RandomUnderSampler, OneHotEncoder, and LogisticRegression
    # Using undersampling to address class imbalance
    pipe = make_imb_pipeline(
        RandomUnderSampler(random_state=21),
        OneHotEncoder(handle_unknown="ignore", sparse=False),
        LogisticRegression(max_iter=2000)
    )

    # Determine CV scores of unoptimized model

    results["Logistic Regression"] = mean_std_cross_val_scores(
        pipe, X_train, y_train, scoring=scoring_metrics
    )

    # Hyperparameter tuning using RandomSearchCV
    param_grid = {
        "logisticregression__C": loguniform(1e-3, 1e3),
    }
    random_search = RandomizedSearchCV(
        pipe,
        param_grid,
        n_iter=50,
        verbose=1,
        n_jobs=-1,
        random_state=123,
        scoring="f1"
    )
    random_search.fit(X_train, y_train)
    print("Best hyperparameter values: ", random_search.best_params_)
    print("Best score: %0.3f" % (random_search.best_score_))

    # Create optimized model
    pipe_opt = make_imb_pipeline(
        RandomUnderSampler(random_state=21),
        OneHotEncoder(handle_unknown="ignore", sparse=False),
        LogisticRegression(
            max_iter=2000,
            C=random_search.best_params_["logisticregression__C"]
        )
    )

    # Determine cross-validation scores of optimized model
    results["Logistic Regression Optimized"] = mean_std_cross_val_scores(
        pipe_opt, X_train, y_train, scoring=scoring_metrics
    )

    result_df = pd.DataFrame(results)
    result_df.index.name = "Scoring Metric"

    # Create output table
    result_df.to_csv(f"{output}CV_results.csv")

    # Creating the best model
    model = LogisticRegression(
        max_iter=2000,
        C=random_search.best_params_["logisticregression__C"]
    )

    # Storing optimized model
    pickle.dump(model, open(f"{output}lr_model.rds", "wb"))


# Function obtained from DSCI-571 lecture notes
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


if __name__ == "__main__":
    main(opt["--input"], opt["--output"])
