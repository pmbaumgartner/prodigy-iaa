from functools import partial
from typing import Callable, Dict, List

import prodigy
import srsly
from prodigy.util import msg
from prodigy.components.loaders import JSONL

from .measures import calculate_agreement
from .processors import VALUE_GETTERS, datasets_to_long, examples_to_reliability
from .render import render_descriptives, render_stats

ANNOTATION_TYPE_HELP = (
    "Type of annotations, can be 'binary' (from `classification` interface, uses 'answer' key), "
    "'multiclass' (from `choices` interface, uses first value in 'accept' key), or "
    "'multilabel' (from `choices` interface, treats every possible label as a binary classification task)."
)


def iaa_dispatch(
    examples,
    annotation_type: str,
    value_getter: Callable[[Dict], str],
    labels: List[str],
    dataset_id_key: str,
):
    if annotation_type in ("binary", "multiclass"):
        reliability_matrix = examples_to_reliability(
            examples, annotator_id=dataset_id_key, value_getter=value_getter
        )
        agreement_stats = calculate_agreement(
            reliability_matrix,
        )
        msg.info("Annotation Statistics")
        print(render_descriptives(agreement_stats))
        print()
        msg.info("Agreement Statistics")
        print(render_stats(agreement_stats))
    if annotation_type == "multilabel":
        if not labels:
            msg.fail("Comma separated label values required for 'multilabel'", exits=1)
        for label in labels:
            label_value_getter = partial(value_getter, value=label)
            reliability_matrix = examples_to_reliability(
                examples,
                annotator_id=dataset_id_key,
                value_getter=label_value_getter,
            )
            agreement_stats = calculate_agreement(reliability_matrix)
            msg.info(f"Annotation Statistics. LABEL: {label}")
            print(render_descriptives(agreement_stats))
            print()
            msg.info(f"Agreement Statistics. LABEL: {label}")
            print(render_stats(agreement_stats))


@prodigy.recipe(
    "iaa.datasets",
    # fmt: off
    datasets=("Datasets to get examples from. Assuming one dataset per annotator. Comma separated values.", "positional", None, prodigy.util.split_string),
    annotation_type=(ANNOTATION_TYPE_HELP, "positional", None, str),
    labels=("Labels for when annotation type is 'multiclass'. Comma separated values.", "option", None, prodigy.util.split_string),
    # fmt: on
)
def iaa_datasets(datasets: List[str], annotation_type: str, labels: List[str]):
    """Calculates IAA using Percent (Simple) Agreement, Krippendorff's `Alpha`, and Gwet's `AC2` given a unique dataset per annotator."""
    value_getter = VALUE_GETTERS.get(annotation_type)
    if value_getter is None:
        msg.fail("Invalid `annotation_type` passed", exits=1)
    DB = prodigy.components.db.connect()
    for set_id in datasets:
        if set_id not in DB:
            msg.fail(f"Can't find dataset '{set_id}' in database", exits=1)
    examples = datasets_to_long(datasets, dataset_id_key="_dataset_id")

    iaa_dispatch(examples, annotation_type, value_getter, labels, "_dataset_id")


@prodigy.recipe(
    "iaa.sessions",
    # fmt: off
    dataset=("Dataset to get examples from. Assuming annotators are captured per-example in _session_id", "positional", None, str),
    annotation_type=(ANNOTATION_TYPE_HELP, "positional", None, str),
    labels=("Labels for when annotation type is 'multiclass'. Comma separated values.", "option", None, prodigy.util.split_string),
    dataset_id_key=("Per-Example key with annotator ID. Defaults to '_session_id'", "option", None, str),
    # fmt: on
)
def iaa_sessions(
    dataset: List[str], annotation_type: str, labels: List[str], dataset_id_key: str
):
    """Calculates IAA using Percent (Simple) Agreement, Krippendorff's `Alpha`, and Gwet's `AC2` assuming multiple annotators within dataset."""
    value_getter = VALUE_GETTERS.get(annotation_type)
    if value_getter is None:
        msg.fail("Invalid `annotation_type` passed", exits=1)

    DB = prodigy.components.db.connect()
    if dataset not in DB:
        msg.fail(f"Can't find dataset '{dataset}' in database", exits=1)
    examples = DB.get_dataset_examples(dataset)
    if dataset_id_key is None:
        dataset_id_key = "_session_id"

    iaa_dispatch(examples, annotation_type, value_getter, labels, dataset_id_key)


@prodigy.recipe(
    "iaa.jsonl",
    # fmt: off
    dataset=("Exported JSONL Dataset to get examples from. Assuming annotators are captured per-example in _session_id", "positional", None, str),
    annotation_type=(ANNOTATION_TYPE_HELP, "positional", None, str),
    labels=("Labels for when annotation type is 'multiclass'. Comma separated values.", "option", None, prodigy.util.split_string),
    dataset_id_key=("Per-Example key with annotator ID. Defaults to '_session_id'", "option", None, str),
    # fmt: on
)
def iaa_jsonl(
    dataset: str, annotation_type: str, labels: List[str], dataset_id_key: str
):
    """Calculates IAA using Percent (Simple) Agreement, Krippendorff's `Alpha`, and Gwet's `AC2` assuming multiple annotators within dataset."""
    value_getter = VALUE_GETTERS.get(annotation_type)
    if value_getter is None:
        msg.fail("Invalid `annotation_type` passed", exits=1)

    examples = list(JSONL(dataset))
    if dataset_id_key is None:
        dataset_id_key = "_session_id"
    iaa_dispatch(examples, annotation_type, value_getter, labels, dataset_id_key)
