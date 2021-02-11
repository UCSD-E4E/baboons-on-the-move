import pandas as pd

from library.metrics import get_metrics


# test function, hard coded to pull from input.mp4 and input.xml
def test_metrics():
    df = pd.DataFrame(get_metrics())
    df.to_csv("input_metrics.csv")


if __name__ == "__main__":
    test_metrics()
