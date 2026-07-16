import os
import csv

from datetime import datetime

from pyplants.core.context import UpdateCtx


def load_test_samples():
    """Load the test data from the csv file."""
    samples = []
    # Create the path to sample files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fpath = os.path.join(current_dir, "samples.csv")
    # Open the file and build a list of update context
    with open(fpath, mode='r', encoding='utf-8', newline='') as file_csv:
        reader = csv.DictReader(file_csv)
        for row in reader:
            uctx = UpdateCtx(
                dt=datetime.fromisoformat(row["DATE"]),
                lw=int(row["LEAFWETNESS"]),
                rain=int(row["RAIN"]),
                tmean=float(row["TMEAN"]),
                rhmean=float(row["RHMEAN"]))
            samples.append(uctx)
    return samples
