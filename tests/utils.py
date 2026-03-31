import csv

from datetime import datetime


def load_test_samples(fpath):
    """Load the test data from the csv file."""
    samples = []
    with open(fpath, mode='r', encoding='utf-8', newline='') as file_csv:
        reader = csv.DictReader(file_csv)
        for row in reader:
            try:
                record = {
                    "DATE": datetime.fromisoformat(row["DATE"]),
                    "TMEAN": float(row["TMEAN"]),
                    "RHMEAN": float(row["RHMEAN"]),
                    "LEAFWETNESS": int(row["LEAFWETNESS"]),
                    "RAIN": int(row["RAIN"])
                }
                samples.append(record)
            except (ValueError, KeyError) as e:
                print(f"Unable to convert line: {reader.line_num}: -> {e}")
    return samples
