from pathlib import Path
import json

from utils.direction import GLOBAL_DIRECTION

# ---------------------------------------------------------------------------
# PAGE DIRECTION
# ---------------------------------------------------------------------------

page_direction = GLOBAL_DIRECTION.assign_page("stat-provinces-nation")



# ============================================================================
# ID REGISTRY
# ============================================================================

current_dir = Path(__file__).resolve().parent
json_path = current_dir / "ids.json"

with open(json_path, "r", encoding="utf-8") as f:
    ids = json.load(f)

for _id in ids:
    page_direction.assign_id(_id)


def pid(id_name: str):
    return page_direction.use_id(id_name)