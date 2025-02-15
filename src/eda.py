# author: Linh Giang Nguyen
# date: 2021-11-28

"""Creates eda plots for the pre-processed training data from the 
National Collision Database (NCDB) 2017 data (from https://open.canada.ca/data/en/
dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a/resource/01426d41-529c-443f-a901-6bc2f94f3d73).
Saves the plots as png files.

Usage: src/eda.py --train=<train> --out_dir=<out_dir>

Options:
--train=<train>     Path (including filename) to training data
--out_dir=<out_dir> Path to directory where the plots should be saved
"""

from docopt import docopt
import pandas as pd
import altair as alt
import os

alt.data_transformers.enable("data_server")
alt.renderers.enable("mimetype")

opt = docopt(__doc__)


def main():

    train_path = opt["--train"]
    save_path = opt["--out_dir"]

    train_df = (
        pd.read_csv(train_path, low_memory=False).set_index("index").rename_axis(None)
    )
    
    # Converts values of P_SEX column into numeric
    sex = {"M": 1, "F": 0, "missing": "missing"}
    train_df["P_SEX"] = [sex[item] for item in train_df["P_SEX"]]
    
    # Creates the list of features to feed into distribution plots
    features = list(set(train_df.columns.values) - set(["index", "FATALITY"]))

    # Creates distribution plots when Fatality = 0
    Chart_False = (
        alt.Chart(train_df)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(alt.repeat("row"), type="quantitative", bin=alt.Bin(maxbins=40)),
            y=alt.Y("count()", title="Number of collisions"),
            color=alt.Color("FATALITY", scale=alt.Scale(scheme="category20c"), legend=None))
        .properties(width=150, height=100)
        .repeat(
            row=features,
            title="No fatality")
        .resolve_scale(y="independent")
        .transform_filter(alt.FieldOneOfPredicate(field="FATALITY", oneOf=[0]))
    )
    
    # Creates distribution plots when Fatality = 1
    Chart_True = (
        alt.Chart(train_df)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(alt.repeat("row"), type="quantitative", bin=alt.Bin(maxbins=40)),
            y=alt.Y("count()", title="Number of collisions"),
            color=alt.Color("FATALITY", scale=alt.Scale(scheme="category20b"), legend=None))
        .properties(width=150, height=100)
        .repeat(
            row=features,
            title="Fatality")
        .resolve_scale(y="independent")
        .transform_filter(alt.FieldOneOfPredicate(field="FATALITY", oneOf=[1]))
    )

    # Save distribution plots
    # Test if we have the given filepath in the directory, if not, create one.
    try:
        Chart_False.save(f"{save_path}Distribution_of_no_fatality.png")
        Chart_True.save(f"{save_path}Distribution_of_fatality.png")
    except:
        os.makedirs(os.path.dirname(save_path))
        Chart_False.save(f"{save_path}Distribution_of_no_fatality.png")
        Chart_True.save(f"{save_path}Distribution_of_fatality.png")

    
if __name__ == "__main__":
    main()