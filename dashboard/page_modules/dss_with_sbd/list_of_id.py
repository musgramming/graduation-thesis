from utils.direction import PageDirection


# ---------------------------------------------------------------------------
# PAGE DIRECTION
# ---------------------------------------------------------------------------

direction = PageDirection()
page_direction = direction.assign_page("sbd")


# ---------------------------------------------------------------------------
# ID REGISTRY
# ---------------------------------------------------------------------------

ids = [
    "sbd",
    "sbd-feedback",
    "year",
    "search-info",
    "comb",
    "status-output-2",
    "score",
    "combs-script",
    "floor-score-input",
    "floor-score-slider",
    "floor-score-warning",
    "mode-selection",
    "analysis",
    "loading-analysis",
    "full-div",
]

for item_id in ids:
    page_direction.assign_id(item_id)


def pid(id_name: str):
    return page_direction.use_id(id_name)