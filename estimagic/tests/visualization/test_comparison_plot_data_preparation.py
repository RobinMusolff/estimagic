"""Tests for the comparison_plot_data_preparation functions."""
from collections import namedtuple

import pandas as pd
import pandas.testing as pdt
import pytest

from estimagic.visualization.comparison_plot import _flatten_dict
from estimagic.visualization.comparison_plot_data_preparation import (
    _add_model_class_and_color,
)
from estimagic.visualization.comparison_plot_data_preparation import _calculate_dodge
from estimagic.visualization.comparison_plot_data_preparation import _calculate_x_bounds
from estimagic.visualization.comparison_plot_data_preparation import (
    _construct_model_names,
)
from estimagic.visualization.comparison_plot_data_preparation import _create_plot_info
from estimagic.visualization.comparison_plot_data_preparation import (
    _determine_plot_height,
)
from estimagic.visualization.comparison_plot_data_preparation import (
    _ensure_correct_conf_ints,
)
from estimagic.visualization.comparison_plot_data_preparation import (
    _replace_by_bin_midpoint,
)

OPT_RES = namedtuple("optimization_result", ["params", "info"])
MEDIUMELECTRICBLUE = "#035096"


# consolidate_parameter_attribute
# ================================


def test_consolidate_parameter_attribute_standard_wildcards():
    pass


def test_consolidate_parameter_attribute_custom_wildcards():
    pass


def test_consolidate_parameter_attribute_different_results_indices():
    pass


def test_consolidate_parameter_attribute_uncompatible():
    pass


# construct_model_names
# ======================


def test_construct_model_names_no_names():
    params = pd.DataFrame()
    info1 = {"model_class": "small", "foo": "bar"}
    info2 = {"model_class": "large", "foo": "bar2"}
    no_name_results = [OPT_RES(params, info1), OPT_RES(params, info2)]
    res = _construct_model_names(results=no_name_results)
    expected = ["0", "1"]
    assert res == expected


def test_construct_model_names_unique_names():
    params = pd.DataFrame()
    info1 = {"model_name": "small_1", "foo": "bar"}
    info2 = {"model_name": "small_2", "foo": "bar2"}
    unique_name_results = [OPT_RES(params, info1), OPT_RES(params, info2)]
    res = _construct_model_names(results=unique_name_results)
    expected = ["small_1", "small_2"]
    assert res == expected


def test_construct_model_names_duplicate_names():
    params = pd.DataFrame()
    info1 = {"model_name": "small_1", "foo": "bar"}
    info2 = {"model_name": "small_1", "foo": "bar2"}
    results_with_duplicate_names = [OPT_RES(params, info1), OPT_RES(params, info2)]

    with pytest.raises(AssertionError):
        _construct_model_names(results_with_duplicate_names)


def test_construct_model_names_only_some_names():
    params = pd.DataFrame()
    info1 = {"model_name": "small_1", "foo": "bar"}
    info2 = {"foo": "bar2"}
    results_with_only_some_names = [OPT_RES(params, info1), OPT_RES(params, info2)]

    with pytest.raises(AssertionError):
        _construct_model_names(results_with_only_some_names)


# add_model_class_and_color
# ==========================


def test_add_model_class_and_color_no_color_dict():
    df = pd.DataFrame(index=[0, 1, 2], columns=["foo", "bar"])
    info = {}
    color_dict = None
    expected = df.copy(deep=True)
    expected["model_class"] = "no model class"
    expected["color"] = MEDIUMELECTRICBLUE
    res = _add_model_class_and_color(df, info, color_dict)
    pdt.assert_frame_equal(res, expected)


def test_add_model_class_and_color_unknown_model_class():
    df = pd.DataFrame(index=[0, 1, 2], columns=["foo", "bar"])
    info = {"model_class": "small"}
    color_dict = {"large": "blue"}
    expected = df.copy(deep=True)
    expected["model_class"] = "small"
    expected["color"] = MEDIUMELECTRICBLUE
    res = _add_model_class_and_color(df, info, color_dict)
    pdt.assert_frame_equal(res, expected)


def test_add_model_class_and_color_known_model_class():
    df = pd.DataFrame(index=[0, 1, 2], columns=["foo", "bar"])
    info = {"model_class": "small"}
    color_dict = {"small": "green"}
    expected = df.copy(deep=True)
    expected["model_class"] = "small"
    expected["color"] = "green"
    res = _add_model_class_and_color(df, info, color_dict)
    pdt.assert_frame_equal(res, expected)


# combine_params_data
# ====================


def test_combine_params_data():
    pass


def test_combine_params_data_complicated_index():
    pass


# ensure_correct_conf_ints
# ==========================


def test_ensure_correct_conf_ints_missing():
    df = pd.DataFrame(index=[0, 1, 2], columns=["a", "b", "c"])
    expected = df.copy(deep=True)
    expected["conf_int_upper"] = pd.np.nan
    expected["conf_int_lower"] = pd.np.nan
    res = _ensure_correct_conf_ints(df)
    pdt.assert_frame_equal(res, expected)


def test_ensure_correct_conf_ints_present():
    df = pd.DataFrame(index=[0, 1, 2], columns=["a", "b", "c"])
    df["conf_int_lower"] = 3
    df["conf_int_upper"] = 1
    expected = df.copy(deep=True)
    res = _ensure_correct_conf_ints(df)
    pdt.assert_frame_equal(res, expected)


def test_ensure_correct_conf_ints_raise_error():
    df = pd.DataFrame(index=[0, 1, 2], columns=["a", "b", "c"])
    df["conf_int_lower"] = 3
    df["conf_int_upper"] = pd.np.nan
    with pytest.raises(AssertionError):
        _ensure_correct_conf_ints(df)


# calculate_x_bounds
# ===================


def test_calculate_x_bounds_without_nan():
    params_data = pd.DataFrame()
    params_data["group"] = ["a", "a", "a"] + ["b", "b", "b"]
    params_data["value"] = [0, 1, 2] + [3, 4, 5]
    params_data["conf_int_lower"] = [-1, 0, -2] + [2, -5, 4]
    params_data["conf_int_upper"] = [1, 2, 3] + [3, 5, 10]

    padding = 0.0
    res_x_min, res_x_max = _calculate_x_bounds(params_data, padding)

    ind = pd.Index(["a", "b"], name="group")
    expected_x_min = pd.Series([-2.0, -5.0], index=ind, name="x_min")
    expected_x_max = pd.Series([3.0, 10.0], index=ind, name="x_max")

    pdt.assert_series_equal(expected_x_min, res_x_min)
    pdt.assert_series_equal(expected_x_max, res_x_max)


def test_calculate_x_bounds_with_nan():
    params_data = pd.DataFrame()
    params_data["group"] = ["a", "a", "a"] + ["b", "b", "b"]
    params_data["value"] = [0, 1, pd.np.nan] + [3, pd.np.nan, 5]
    params_data["conf_int_lower"] = pd.np.nan
    params_data["conf_int_upper"] = pd.np.nan

    padding = 0.0
    res_x_min, res_x_max = _calculate_x_bounds(params_data, padding)

    ind = pd.Index(["a", "b"], name="group")
    expected_x_min = pd.Series([0.0, 3.0], index=ind, name="x_min")
    expected_x_max = pd.Series([1.0, 5.0], index=ind, name="x_max")

    pdt.assert_series_equal(expected_x_min, res_x_min)
    pdt.assert_series_equal(expected_x_max, res_x_max)


def test_calculate_x_bounds_with_padding():
    params_data = pd.DataFrame()
    params_data["group"] = ["a", "a", "a"] + ["b", "b", "b"]
    params_data["value"] = [0, 1, pd.np.nan] + [3, pd.np.nan, 5]
    params_data["conf_int_lower"] = pd.np.nan
    params_data["conf_int_upper"] = pd.np.nan

    padding = 0.1
    res_x_min, res_x_max = _calculate_x_bounds(params_data, padding)

    ind = pd.Index(["a", "b"], name="group")
    expected_x_min = pd.Series([-0.1, 2.8], index=ind, name="x_min")
    expected_x_max = pd.Series([1.1, 5.2], index=ind, name="x_max")

    pdt.assert_series_equal(expected_x_min, res_x_min)
    pdt.assert_series_equal(expected_x_max, res_x_max)


# calculate_bins_and_rectangle_width
# ===================================


def test_calculate_bins_and_rectangle_width():
    pass


# replace_by_midpoint
# ====================


def test_replace_by_midpoint_without_nan():
    ind = ["model1", "model2", "corner_right", "corner_left"]
    values = pd.Series([0.1, 0.2, 0.6, 0.15], index=ind)
    group_bins = pd.Series([0.0, 0.15, 0.3, 0.45, 0.6, 0.75], name="group1")
    res = _replace_by_bin_midpoint(values, group_bins)
    expected = pd.Series([0.075, 0.225, 0.525, 0.075], index=ind)
    pdt.assert_series_equal(res, expected)


def test_replace_by_midpoint_with_nan():
    ind = ["model1", "missing", "corner_right", "corner_left"]
    values = pd.Series([0.1, pd.np.nan, 0.6, 0.15], index=ind)
    group_bins = pd.Series([0.0, 0.15, 0.3, 0.45, 0.6, 0.75], name="group1")
    res = _replace_by_bin_midpoint(values, group_bins)
    expected = pd.Series([0.075, 0.075, 0.525, 0.075], index=ind)
    pdt.assert_series_equal(res, expected)


# calculate dodge
# ================


def test_calculate_dodge_without_nan():
    ind = ["small1", "small2", "middle1", "large1", "large2", "large3"]
    values = pd.Series([0.05, 0.1, 0.2, 0.61, 0.62, 0.7], index=ind)
    group_bins = pd.Series([0.0, 0.15, 0.3, 0.45, 0.6, 0.75], name="group1")
    expected = pd.Series([0.5, 1.5, 0.5, 0.5, 1.5, 2.5], index=ind)
    res = _calculate_dodge(values, group_bins)
    pdt.assert_series_equal(res, expected)


def test_calculate_dodge_with_nan():
    ind = ["small1", "small2", "middle1", "large1", "nan0", "nan1"]
    values_with_nan = pd.Series([0.05, 0.1, 0.2, 0.61, pd.np.nan, pd.np.nan], index=ind)
    group_bins = pd.Series([0.0, 0.15, 0.3, 0.45, 0.6, 0.75], name="group1")
    expected = pd.Series([0.5, 1.5, 0.5, 0.5, 0.5, 1.5], index=ind)
    res = _calculate_dodge(values_with_nan, group_bins)
    pdt.assert_series_equal(res, expected)


# create_plot_info
# =================


def test_create_plot_info():
    ind = pd.Index(["group1", "group2", "group3"], name="group")
    x_min = pd.Series([0.0, 5.0, -3.5], index=ind, name="x_min")
    x_max = pd.Series([1.0, 149.3, -1.1], index=ind, name="x_max")
    rect_width = pd.Series([0.1, 20, 0.5], index=ind, name="width")
    res = _create_plot_info(
        x_min=x_min, x_max=x_max, rect_width=rect_width, y_max=10, plot_height=50
    )

    expected = {
        "plot_height": 50,
        "y_range": (0, 10),
        "group_info": {
            "group1": {"x_range": (0.0, 1.0), "width": 0.1},
            "group2": {"x_range": (5.0, 149.3), "width": 20},
            "group3": {"x_range": (-3.5, -1.1), "width": 0.5},
        },
    }
    assert res == expected


# determine_plot_height
# ======================


def test_determine_plot_height_none():
    res = _determine_plot_height(figure_height=None, y_max=10, n_params=10, n_groups=4)
    expected = 300
    assert res == expected


def test_determine_plot_height_given():
    res = _determine_plot_height(figure_height=500, y_max=5, n_params=5, n_groups=2)
    expected = 80
    assert res == expected


def test_determine_plot_height_warning():
    with pytest.warns(Warning):
        _determine_plot_height(figure_height=100, y_max=5, n_params=5, n_groups=3)


# comparison_plot_inputs
# =======================


def test_comparison_plot_inputs():
    # test that correct dodge comes out when results
    # are not fed in ordered by model_class!
    # -> nice coloring in the "histogram" plot!
    pass


# flatten_dict
# ==============


@pytest.fixture
def nested_dict():
    nested_dict = {
        "g1": {"p1": "val1"},
        "g2": {"p2": "val2"},
        "g3": {"p3": "val3", "p31": "val4"},
    }
    return nested_dict


flatten_dict_fixtures = [
    (None, ["val1", "val2", "val3", "val4"]),
    ("p31", ["val1", "val2", "val3"]),
]


@pytest.mark.parametrize("exclude_key, expected", flatten_dict_fixtures)
def test_flatten_dict_without_exclude_key(nested_dict, exclude_key, expected):
    flattened = _flatten_dict(nested_dict, exclude_key)
    assert flattened == expected