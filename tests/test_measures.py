"""Tests from examples in:

K. L. Gwet, “On Krippendorff’s Alpha Coefficient,” p. 16, 2015.
https://agreestat.com/papers/onkrippendorffalpha_rev10052015.pdf
"""
import pytest

from prodigy_iaa.measures import calculate_agreement


def test_data1(reliability_data1):
    agreement_stats = calculate_agreement(
        reliability_data1,
    )
    assert agreement_stats["percent_agreement"] == pytest.approx(0.8182, 0.0001)
    assert agreement_stats["kripp_alpha"] == pytest.approx(0.7434, 0.0001)
    assert agreement_stats["ac2"] == pytest.approx(0.7754, 0.0001)


def test_data2(reliability_data2):
    agreement_stats = calculate_agreement(
        reliability_data2,
    )
    assert agreement_stats["percent_agreement"] == pytest.approx(0.6250, 0.0001)
    assert agreement_stats["kripp_alpha"] == pytest.approx(0.4765, 0.0001)
    assert agreement_stats["ac2"] == pytest.approx(0.5093, 0.0001)
