from typing import List

import pandas as pd
import pytest
import srsly
from prodigy.util import set_hashes


def binary_data():
    binary = [
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 1.0],
        [1.0, None, None],
        [1.0, 0.0, 1.0],
    ]
    binary_df = pd.DataFrame(binary)
    return binary_df


def multiclass_data():
    multiclass = [
        ["B", "A", "B"],
        ["A", "B", "C"],
        ["C", "C", "C"],
        ["B", None, None],
        ["B", "A", "B"],
    ]
    multiclass_df = pd.DataFrame(multiclass)
    return multiclass_df


def multilabel_data():
    """This one is complex compared to the others. We want a list of dataframes,
    where each dataframe is a N x K (K=n labels)."""

    # 3 annotators, 4 labels, 5 examples
    multilabel_a1 = [
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, 1.0, 0.0],
        [None, None, None, None],
        [None, None, None, None],
    ]
    multilabel_a2 = [
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, 1.0, 0],
        [None, None, None, None],
        [0.0, 1.0, 0.0, 0.0],
    ]
    multilabel_a3 = [
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 0.0],
        [None, None, None, None],
        [None, None, None, None],
        [0.0, 0.0, 0.0, 1.0],
    ]

    multilabel_dfs = [
        pd.DataFrame(data) for data in [multilabel_a1, multilabel_a2, multilabel_a3]
    ]
    return multilabel_dfs


def binary_df_to_prodigy(df):
    """Converts a DataFrame to prodigy task JSON

    - Index value will be used as the task 'text'. Make sure there are only
        values of annotations within the dataframe (no metadata)
    - Missing values are not added as examples
    - Values should be 0 and 1.
    """
    data = []
    for row in df.itertuples():
        text = f"Row {row.Index}"
        # first value is Index, skip it
        for (a_i, value) in enumerate(row[1:]):
            row_data = {"text": text}
            if pd.isnull(value):
                continue
            row_data["answer"] = "accept" if value == 1 else "reject"
            row_data["_session_id"] = f"Annotator-{a_i}"
            row_data = set_hashes(row_data)
            data.append(row_data)
    return data


def multiclass_df_to_prodigy(df):
    """Converts a DataFrame to prodigy task JSON

    - Index value will be used as the task 'text'. Make sure there are only
        values of annotations within the dataframe (no metadata)
    - Missing values are not added as examples
    """
    data = []
    for row in df.itertuples():
        text = f"Row {row.Index}"
        # first value is Index, skip it
        for (a_i, value) in enumerate(row[1:]):
            if pd.isnull(value):
                continue
            row_data = {
                "text": text,
                "answer": "accept",
            }  # assume 'accept' if annotated
            row_data["accept"] = []
            row_data["_session_id"] = f"Annotator-{a_i}"
            row_data = set_hashes(row_data)
            row_data["accept"].append(str(value))
            data.append(row_data)
    return data


def multilabel_dfs_to_prodigy(dfs: List[pd.DataFrame]):
    """Converts a DataFrame to prodigy task JSON. Takes a list of dataframes,
    where each dataframe is a N x K (K=n labels). This means len(dfs) == N annotators.

    - Index value will be used as the task 'text'. Make sure there are only
        values of annotations within the dataframe (no metadata)
    - Missing values are not added as examples (assumed they did not annotate that one)
    - Values should be 1 and 0. !!! This means if you want to indicate an annotator didn't annotate
        a specific example, set the whole row to NaN/None
    """
    data = []
    for (a_i, df) in enumerate(dfs):
        for row in df.itertuples():
            if all(pd.isnull(v) for v in row[1:]):
                # To indicate an annotator skipped this example, set all
                # values to NaN/None. This is because in the multilabel case
                # 'missing' can be interpreted as not selecting that label
                # at the unit/item level - equivalent to 0.
                continue
            text = f"Row {row.Index}"
            row_data = {"text": text, "answer": "accept"}
            row_data["accept"] = []
            row_data = set_hashes(row_data)
            # first value is Index, skip it
            for (k_i, value) in enumerate(row[1:]):
                if value == 1:
                    row_data["accept"].append(f"Label {k_i}")
            row_data["_session_id"] = f"Annotator-{a_i}"
            data.append(row_data)
    return data


@pytest.fixture
def binary_data_prodigy_json(tmp_path):
    lines = binary_df_to_prodigy(binary_data())
    path = tmp_path / "binary.jsonl"
    srsly.write_jsonl(path, lines)
    yield path


@pytest.fixture
def multiclass_data_prodigy_json(tmp_path):
    lines = multiclass_df_to_prodigy(multiclass_data())
    path = tmp_path / "multiclass.jsonl"
    srsly.write_jsonl(path, lines)
    yield path


@pytest.fixture
def multilabel_data_prodigy_json(tmp_path):
    lines = multilabel_dfs_to_prodigy(multilabel_data())
    path = tmp_path / "multilabel.jsonl"
    srsly.write_jsonl(path, lines)
    yield path


from prodigy_iaa import iaa_jsonl


def test_jsonl_binary(binary_data_prodigy_json):
    # Note that since we use the function these args are required, even though
    # they are optional, because PLAC is doing some CLI magic
    iaa_jsonl(binary_data_prodigy_json, "binary", [], None)


def test_jsonl_multiclass(multiclass_data_prodigy_json):
    # Note that since we use the function these args are required, even though
    # they are optional, because PLAC is doing some CLI magic
    iaa_jsonl(multiclass_data_prodigy_json, "multiclass", [], None)


def test_jsonl_multilabel(multilabel_data_prodigy_json):
    """Requires knowing that there are 4 labels we want to do this for."""
    iaa_jsonl(
        multilabel_data_prodigy_json,
        "multilabel",
        [f"Label {i}" for i in range(4)],
        None,
    )
