import pandas as pd
from io import StringIO

import pytest


def df_to_reliability(df):
    """Converts a DataFrame to a list of lists, where missing values
    are replaced with `None`."""
    df = df.where(pd.notnull(df), None)
    reliability_data = df.values.tolist()
    return reliability_data


@pytest.fixture
def reliability_data1_df():
    # from 'K. L. Gwet, “On Krippendorff’s Alpha Coefficient,” p. 16, 2015.'
    data = """
Unit	A	B	C	D
1	1	1	.	1
2	2	2	3	2
3	3	3	3	3
4	3	3	3	3
5	2	2	2	2
6	1	2	3	4
7	4	4	4	4
8	1	1	2	1
9	2	2	2	2
10	.	5	5	5
11	.	.	1	1
12	.	.	3	.
    """
    df = pd.read_csv(
        StringIO(data), sep="\t", index_col="Unit", na_values=["."]
    ).astype(object)
    return df


@pytest.fixture
def reliability_data2_df():
    # From
    # Hayes, A. F., & Krippendorff, K. (2007).
    #  Answering the Call for a Standard Reliability Measure for Coding Data.
    #  Communication Methods and Measures, 1(1), 77–89.
    #  doi:10.1080/19312450709336664
    data = """
Unit	obs1	obs2	obs3	obs4	obs5
1	1	1	2	.	2
2	1	1	0	1	.
3	2	3	3	3	.
4	.	0	0	.	0
5	0	0	0	.	0
6	0	0	0	.	0
7	1	0	2	.	1
8	1	.	2	0	.
9	2	2	2	.	2
10	2	1	1	1	.
11	.	1	0	0	.
12	0	0	0	0	.
13	1	2	2	2	.
14	3	3	2	2	3
15	1	1	1	.	1
16	1	1	1	.	1
17	2	1	2	.	2
18	1	2	3	3	.
19	1	1	0	1	.
20	0	0	0	.	0
21	0	0	1	1	.
22	0	0	.	0	0
23	2	3	3	3	.
24	0	0	0	0	.
25	1	2	.	2	2
26	0	1	1	1	.
27	0	0	0	1	0
28	1	2	1	2	.
29	1	1	2	2	.
30	1	1	2	.	2
31	1	1	0	.	0
32	2	1	2	1	.
33	2	2	.	2	2
34	3	2	2	2	.
35	2	2	2	.	2
36	2	2	3	.	2
37	2	2	2	.	2
38	2	2	.	1	2
39	2	2	2	2	.
40	1	1	1	.	1
    """
    df = pd.read_csv(
        StringIO(data), sep="\t", index_col="Unit", na_values=["."]
    ).astype(object)
    return df


@pytest.fixture
def reliability_data1(reliability_data1_df):
    return df_to_reliability(reliability_data1_df)


@pytest.fixture
def reliability_data2(reliability_data2_df):
    return df_to_reliability(reliability_data2_df)
