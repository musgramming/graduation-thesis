from utils.direction import PageDirection


# ============================================================================
# PAGE DIRECTION
# ============================================================================

direction = PageDirection()
page_direction = direction.assign_page("without_sbd")


# ============================================================================
# ID REGISTRY
# ============================================================================

for _id in [
    "year",
    "math",
    "literature",
    "mon-1",
    "mon-2",
    "diem-mon-1",
    "diem-mon-2",
    "build-combs",
    "error",
    "scenario",
    "your-comb",
    "your-score",
    "stored-results",
    "floor-score-input",
    "floor-score",
    "combs-list-container",
    "combs-list",
    "run-scenario",
    "loading-main",
    "right-content",
]:
    page_direction.assign_id(_id)


def pid(id_name: str):
    return page_direction.use_id(id_name)