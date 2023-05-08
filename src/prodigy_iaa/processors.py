from itertools import groupby
from typing import Any, Dict, List, Optional

import prodigy
from prodigy.util import msg

ExampleDict = Dict[str, Any]


def _has_single_value(annotations, key: str):
    """Checks if a series of annotations has a single value for a given
    key. Useful for checking that all annotations have the same `view_id` and `label`"""
    return len(set(a.get(key) for a in annotations)) == 1


def datasets_to_long(
    datasets: List[str], dataset_id_key="_dataset_id"
) -> List[ExampleDict]:
    """Convert annotations from multiple datasets into one long
    dataset, with the source dataset saved as `dataset_id_key`"""
    DB = prodigy.components.db.connect()
    for set_id in datasets:
        if set_id not in DB:
            msg.fail(f"Can't find dataset '{set_id}' in database", exits=1)
    all_examples = []
    for set_id in datasets:
        examples = DB.get_dataset_examples(set_id)
        for example in examples:
            example[dataset_id_key] = set_id
        all_examples.extend(examples)
    if not _has_single_value(all_examples, "label"):
        msg.fail(
            "Multiple `label` values present in dataset. Export your data to JSONL, clean it up, and try again with the 'iaa.jsonl' recipe.",
            exits=1,
        )

    if not _has_single_value(all_examples, "view_id"):
        msg.fail(
            "Multiple `view_id` values present in dataset. Export your data to JSONL, clean it up, and try again with the 'iaa.jsonl' recipe.",
            exits=1,
        )
    return all_examples


def get_answer(example) -> Optional[str]:
    answer = example["answer"]
    if answer in ("accept", "reject"):
        return answer
    else:
        return None


def get_choice(example) -> Optional[str]:
    if example["answer"] == "accept":
        try:
            # They could accept but have no choice
            return example["accept"][0]
        except IndexError:
            return None
    else:
        return None


def get_contains(example, value: str) -> int:
    """You'll need to use this with functools.partial to pass
    to examples_to_reliability in the multilabel case."""
    return int(value in example["accept"])


VALUE_GETTERS = {
    "binary": get_answer,
    "multiclass": get_choice,
    "multilabel": get_contains,
}


def _has_unique_annotations(annotations, key: str) -> bool:
    """Validate that a set of annotations is unique by `key`"""
    return len(set(a[key] for a in annotations)) == len(annotations)


def examples_to_reliability(
    examples: List[ExampleDict],
    annotator_id="_session_id",
    example_id="_task_hash",
    value_getter=get_answer,
) -> List[List[Optional[Any]]]:
    """Converts a long dataset to an (N x A) reliability matrix, where N is the number
    of unique examples keyed by `example_id` and A is the number of unique annotators
    given by `annotator_id`, and the value is the annotation given by annotator A to example N
    (or None if not annotated)"""
    annotators = tuple(set(example[annotator_id] for example in examples))
    grouped_by_task = groupby(
        sorted(examples, key=lambda x: x[example_id]), lambda x: x[example_id]
    )
    reliability_matrix = []
    for _, task_annotations in grouped_by_task:
        task_annotations = list(task_annotations)
        if not _has_unique_annotations(task_annotations, annotator_id):
            msg.fail(
                "Multiple annotations by single annotator for same task. Export your data to JSONL, clean it up, and try again with the 'iaa.jsonl' recipe.",
                exits=1,
            )
        task_values = []
        for annotator in annotators:
            value = next(
                (
                    value_getter(ex)
                    for ex in task_annotations
                    if ex[annotator_id] == annotator
                ),
                None,
            )
            task_values.append(value)
        reliability_matrix.append(task_values)
    return reliability_matrix
