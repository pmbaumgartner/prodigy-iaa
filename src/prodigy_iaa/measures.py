from collections import Counter
from itertools import chain, product
from typing import Any, Callable, List, Optional


def KnownCounter(keys):
    """This is like a combination of a defaultdict and Counter, for when
    we know what keys we'll have that should start at 0."""
    return Counter({k: 0 for k in keys})


def build_agreement_table(data: List[List[Optional[Any]]]):
    """Converts a (N x A) data matrix into an (N x K) agreement table, containing the
    number of values for each of K categories for each example."""
    categories = set(chain.from_iterable(data))
    categories.discard(None)
    agreement_table = []
    for row in data:
        counter = KnownCounter(categories)
        counter.update([r for r in row if r is not None])
        agreement_table.append(counter)
    return agreement_table


def identity_weighting(k, l) -> float:
    """These measures provide a weighting metric option where the output is [0, 1]. This defines agreement if the two
    values are equal.

    As an example of how you might want to use a different function, imagine
    'Good' and 'Great' indicate some agreement."""
    return float(k == l)


def calculate_agreement(
    reliability_matrix: List[List[Optional[Any]]],
    weighting: Callable[[Any, Any], float] = identity_weighting,
):
    """This calculates Percent Agreement, Krippendorff's Alpha, and Gwet's AC1. Most variable names
    follow the equations from from 'Gwet, Kilem L. “On Krippendorff’s Alpha Coefficient,” 2015.' with
    a few exceptions to distinguish variables per metric.

    Input is an (N x A) reliability matrix, where N is the number
    of unique examples, A is the number of unique annotators,
    and the value is the annotation given by annotator A to example N
    (or None if not annotated)
    """
    agreement_table = build_agreement_table(reliability_matrix)
    raters_per_example = ri = [sum(example.values()) for example in agreement_table]
    categories = list(agreement_table[0].keys())
    n_annotators = len(reliability_matrix[0])
    n_categories = q = len(categories)
    # Krippendorff's Alpha percent expected (PE) + percent agreement (PA)
    #   uses only rows with more than 1 rater
    # AC1 uses full agreement table for PE
    coincidence_ix = [i for i, v in enumerate(raters_per_example) if v != 1]
    coincident_agreement_table = [agreement_table[i] for i in coincidence_ix]
    coincident_raters_per_example = ri_c = [
        raters_per_example[i] for i in coincidence_ix
    ]

    # These are named different from the paper because we want to distinguish them.
    n_c = len(coincidence_ix)
    n_a = len(raters_per_example)

    rbar = sum(coincident_raters_per_example) / n_c

    # Some summary statistics to display
    avg_raters_per_example = sum(raters_per_example) / n_a
    n_single_annotation = n_a - n_c
    coincident_annotations_per_category = sum(coincident_agreement_table, Counter())

    kripp_pa_sum = 0
    ac_pa_sum = 0
    for i, counts in enumerate(coincident_agreement_table):
        kripp_pa_i = 0
        ac_pa_i = 0
        for k in categories:
            r_ik = counts[k]
            rbar_ik = 0
            for l in categories:
                v = weighting(k, l) * r_ik
                rbar_ik += v
            kripp_p_ai_k = (r_ik * (rbar_ik - 1)) / (rbar * (ri_c[i] - 1))
            kripp_pa_i += kripp_p_ai_k
            # p_ai_k is the different calculation between the two
            ac_pa_ik = (r_ik * (rbar_ik - 1)) / (ri_c[i] * (ri_c[i] - 1))
            ac_pa_i += ac_pa_ik
        kripp_pa_sum += kripp_pa_i
        ac_pa_sum += ac_pa_i

    kripp_pa_prime = kripp_pa_sum / n_c
    kripp_pa = ((1 - (1 / (rbar * n_c))) * kripp_pa_prime) + (1 / (rbar * n_c))

    # AC also differs in that it uses this "raw" pa and not pa_prime in a later equation
    ac_pa = ac_pa_sum / n_c

    # Calculations for Alpha PE
    codes_per_category = KnownCounter(categories)
    codes_per_category.update(
        chain.from_iterable([reliability_matrix[i] for i in coincidence_ix])
    )
    codes_per_category = {k: v for k, v in codes_per_category.items() if k is not None}
    average_category_per_unit = {
        k: v / len(coincidence_ix) for k, v in codes_per_category.items()
    }
    kripp_pi_k = {k: v / rbar for k, v in average_category_per_unit.items()}

    kripp_pe = sum(
        weighting(k, l) * kripp_pi_k[k] * kripp_pi_k[k]
        for k, l in product(categories, categories)
    )
    ac_pi_k = {}
    for category in categories:
        cat_sums = 0
        for i, counts in enumerate(agreement_table):
            # Note: we use the full agreement table
            v = counts[category] / ri[i]
            cat_sums += v
        ac_pi_k[category] = cat_sums / n_a

    tw = sum(weighting(k, l) for k, l in product(categories, categories))
    ac_pe = (tw / (q * (q - 1))) * (sum(ac_pi_k[k] * (1 - ac_pi_k[k]) for k in ac_pi_k))
    percent_agreement = ac_pa
    kripp_alpha = (kripp_pa - kripp_pe) / (1 - kripp_pe)
    ac2 = (ac_pa - ac_pe) / (1 - ac_pe)
    return {
        "percent_agreement": percent_agreement,
        "kripp_alpha": kripp_alpha,
        "ac2": ac2,
        "n_categories": n_categories,
        "n_annotators": n_annotators,
        "n_examples": n_a,
        "n_coincident_examples": n_c,
        "avg_raters_per_example": avg_raters_per_example,
        "n_single_annotation": n_single_annotation,
        "coincident_annotations_per_category": coincident_annotations_per_category,
    }
