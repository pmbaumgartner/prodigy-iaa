from wasabi import table


def _format_number(number: float, ndigits: int = 2) -> str:
    """Formats a number rounding to `ndigits`, without truncating trailing 0s,
    as happens with `round(number, ndigits)`"""
    return f"{number:.{ndigits}f}"


def render_descriptives(iaa_stats):
    data = [
        (
            "Examples",
            iaa_stats["n_examples"],
        ),
        (
            "Categories",
            iaa_stats["n_categories"],
        ),
        ("Co-Incident Examples*", iaa_stats["n_coincident_examples"]),
        ("Single Annotation Examples", iaa_stats["n_single_annotation"]),
        (
            "Annotators",
            iaa_stats["n_annotators"],
        ),
        (
            "Avg. Annotations per Example",
            _format_number(iaa_stats["avg_raters_per_example"], 2),
        ),
    ]
    aligns = ("l", "r")
    formatted = table(data, header=("Attribute", "Value"), divider=True, aligns=aligns)
    formatted += "\n* (>1 annotation)"
    return formatted


def render_stats(iaa_stats):

    data = [
        (
            "Percent (Simple) Agreement",
            _format_number(iaa_stats["percent_agreement"], 4),
        ),
        ("Krippendorff's Alpha", _format_number(iaa_stats["kripp_alpha"], 4)),
        ("Gwet's AC2", _format_number(iaa_stats["ac2"], 4)),
    ]
    aligns = ("l", "r")
    formatted = table(data, header=("Statistic", "Value"), divider=True, aligns=aligns)
    return formatted
