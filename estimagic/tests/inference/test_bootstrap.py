import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal as afe

from estimagic.inference.bootstrap import get_results_table


@pytest.fixture
def setup():
    out = {}

    out["df"] = pd.DataFrame(
        np.array([[1, 10], [2, 7], [3, 6], [4, 5]]), columns=["x1", "x2"]
    )

    x = np.array([[2.0, 8.0], [2.0, 8.0], [2.5, 7.0], [3.0, 6.0], [3.25, 5.75]])
    out["estimates"] = pd.DataFrame(x, columns=["x1", "x2"])

    return out


@pytest.fixture
def expected():
    out = {}

    z = np.array([[2.55, 0.5701, 2, 3.225], [6.95, 1.0665, 5.775, 8]])

    out["results"] = pd.DataFrame(
        z, columns=["mean", "std", "lower_ci", "upper_ci"], index=["x1", "x2"]
    )

    return out


def g(data):
    return data.mean(axis=0)


def test_get_results_table(setup, expected):

    results = get_results_table(
        data=setup["df"], f=g, estimates=setup["estimates"], ci_method="percentile"
    )

    afe(results, expected["results"], check_less_precise=True)