# ✨ Prodigy - 🤝 Inter-Annotator Agreement Recipes 

These recipes calculate [Inter-Annotator Agreement](https://en.wikipedia.org/wiki/Inter-rater_reliability) (aka Inter-Rater Reliability) measures for [Prodigy](https://prodi.gy/). The measures include Percent (Simple) Agreement, Krippendorff's `Alpha`, and Gwet's `AC2`. All calculations were derived using the equations in [this paper](https://agreestat.com/papers/onkrippendorffalpha_rev10052015.pdf)[^1], and this includes tests to match the values given on the datasets referenced in that paper. 

Currently this package supports IAA metrics for binary classification, multiclass classification, and multilabel (binary per label) classification. Span-based IAA measures for NER and Span Categorization will be integrated in the future.

Recipes depend the source data structure:
- `iaa.datsets` will calculate measures assuming you have multiple datasets in prodigy, one dataset per annotator
- `iaa.sessions` will calculate measures assuming you have multiple annotators, identified typically by `_session_id`, in a single dataset
- `iaa.jsonl` operates the same as `iaa.sessions`, but on a file exported to JSONL with `prodigy db-out`.

ℹ️ **Get details on each recipe's arguments with `prodigy <recipe> --help`**

# Example

Calculates agreement using dataset `my-dataset`, which is a `multiclass` problem -- meaning it's data is generated using the `choice` interface, exclusive choices, storing choices in the "accept" key. In this example, there are 5 total examples, 4 of them have co-incident annotations (i.e. overlap), and 3 unique annotators.

```
$ prodigy iaa.sessions my-dataset multiclass

ℹ Annotation Statistics

Attribute                      Value
----------------------------   -----
Examples                           5
Categories                         3
Co-Incident Examples*              4
Single Annotation Examples         1
Annotators                         3
Avg. Annotations per Example    2.60

* (>1 annotation)

ℹ Agreement Statistics

Statistic                     Value
--------------------------   ------
Percent (Simple) Agreement   0.4167
Krippendorff's Alpha         0.1809
Gwet's AC2                   0.1640
```

## Validations & Practical Use

All recipes depend on examples being hashed uniquely and stored under `_task_hash` on the example. There are other validations involved as well:
- Checks if `view_id` is the same for all examples
- Checks if `label` is the same for all examples
- Checks that each annotator has not double-annotated the same `_task_hash`

If any validations fail, or your data is weird in some way, `iaa.jsonl` will be the recipe you want. Export your data, identify any issues and remedy them, and then calculate your measures on the cleaned exported data.


## Theory

There is no single measure across all datasets to give a reasonable measurement of agreement - often times the measures are conditional on qualities of the data. The metrics here have nice properties that make them flexible to various annotation situations: they can handle missing values (i.e. incomplete overlap), scale to any number of annotators, scale to any number of categories, and can be customized with your own weighting functions. In addition, the choice of metrics available within this package follow the recommendations in the literature[^2][^3], plus theoretical analysis[^4] demonstrating when certain metrics might be most useful.

Table 13 in [this paper](https://scholar.google.com/scholar?cluster=17269958574032994585&hl=en&as_sdt=0,34&as_vis=1)[^4] highlights systematic issues with each metric. They are as follows:

- **When there is _low agreement_**: Percent (Simple) Agreement can produce high scores.
  - Imagine a binary classification problem with a very low base rate. Annotators can often agree on the negative case, but rarely agree on the positive.
- **When there are _highly uneven sizes of categories_**: `AC2` will be high, `Alpha` can produce high scores.
- **When there are _N < 20_ co-incident annotated examples**: `Alpha` can produce high scores.
  - You probably shouldn't trust _N < 100_ generally.
- **When there are _3 or more categories_**: `AC2` can produce high scores.

**Summary**: Use simple agreement and `Alpha`. If simple agreement is high, and `Alpha` is low, verify with `AC2`[^3]. 

## Use Outside Prodigy / Other Use-Cases

If you want to calculate these measures in a custom script on your own data, you can use `from prodigy_iaa.measures import calculate_agreement`. See tests in `tests/test_measures.py` for an example. The docstrings for each function should indicate the expected data structures. You could also use this, for example, to print out some nice output during an `update` callback and get annotation statistics as each user submits examples.

## References


[^1]: K. L. Gwet, “On Krippendorff’s Alpha Coefficient,” p. 16, 2015.
[^2]: J. Lovejoy, B. R. Watson, S. Lacy, and D. Riffe, “Three Decades of Reliability in Communication Content Analyses: Reporting of Reliability Statistics and Coefficient Levels in Three Top Journals,” p. 44.
[^3]: S. Lacy, B. R. Watson, D. Riffe, and J. Lovejoy, “Issues and Best Practices in Content Analysis,” Journalism & Mass Communication Quarterly, vol. 92, no. 4, pp. 791–811, Dec. 2015, doi: 10.1177/1077699015607338.
[^4]: X. Zhao, J. S. Liu, and K. Deng, “Assumptions Behind Intercoder Reliability Indices,” Communication Yearbook, p. 83.
