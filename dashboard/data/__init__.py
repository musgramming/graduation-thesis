from pathlib import Path
import geopandas as gpd
import polars as pl
import json5


# =====================================================================
# Gọi thư mục 
# =====================================================================

# Thư mục gốc 'data/'
DATA_DIR = Path(__file__).parent 


# Thư mục chứa các bảng tra cứu/quy đổi
LOOKUP_DIR = DATA_DIR / "lookup_tables"


# Thư mục chứa bảng điểm thô
BASE_RAW_SCORE_DIR = DATA_DIR / "raw_scores"


# Thư mục chứa bảng điểm tổ hợp
BASE_COMB_SCORE_DIR = DATA_DIR / "combs_scores"


# Sửa lại đường dẫn trỏ đúng vào lookup_tables/
TO_HOP_PATH = LOOKUP_DIR / "bang_to_hop_mon.csv"

if not TO_HOP_PATH.exists():
    print(f"⚠️ Cảnh báo: Không tìm thấy file {TO_HOP_PATH}")


# Thư mục chứa bản đồ
BASE_GRAPH_DIR = DATA_DIR / "graph"





# =====================================================================
# Gọi file
# =====================================================================

TO_HOP = pl.scan_csv(TO_HOP_PATH).with_columns(
        pl.concat_str(
            [
                pl.col("Tổ hợp"),
                pl.lit(" ("),
                pl.col("Môn 1"),
                pl.lit(", "),
                pl.col("Môn 2"),
                pl.lit(", "),
                pl.col("Môn 3"),
                pl.lit(")")
            ]
        ).alias("Tên tổ hợp")
    )


BANG_DIEM = {
    str(f.stem.split('-')[-1]): pl.scan_parquet(f)
    for f in BASE_RAW_SCORE_DIR.glob("bang_diem-*.parquet")
}


NAM = BANG_DIEM.keys()


BANG_DIEM_TO_HOP = {
    int(f.stem.split('-')[-1]): pl.scan_parquet(f)
    for f in BASE_COMB_SCORE_DIR.glob("bang_diem_to_hop-*.parquet")
}


danh_sach_don_thuan = (
    (
        TO_HOP
            .select(["Môn 1", "Môn 2", "Môn 3"])
            .unpivot(
                variable_name="Số thứ tự", 
                value_name="Tên môn"
            )
    )
    .select("Tên môn")
    .unique()
    .collect()
    .get_column("Tên môn")
    .to_list()
)


BANG_CHON_MON = [
    {
        "label": mon, 
        "value": mon
    } for mon in danh_sach_don_thuan if mon not in ["Toán", "Văn"]
]


with open(DATA_DIR / "lookup_tables" / "bang_chon_mon.jsonc", "r", encoding = "utf-8") as f: 
    __bang_chon = json5.load(f)
    BANG_CHON_MON_DICT = __bang_chon["short-ver"]
    BANG_CHON_MON_DROPDOWN = __bang_chon["long-ver"]


with open(DATA_DIR / "lookup_tables" / "bang_quy_doi_tinh_thanh.jsonc", "r", encoding = "utf-8") as f:
    BANG_QUY_DOI_TINH_THANH = json5.load(f)


BANG_TINH_THANH = {
    code: name
    for code, name in BANG_QUY_DOI_TINH_THANH["2026"].items()
}


COMB_OPTIONS = [
    {
        "label": row["Tên tổ hợp"],
        "value": row["Tổ hợp"],
    }
    for row in TO_HOP.collect().to_dicts()
]


BAN_DO_HANH_CHINH = gpd.read_file(
    BASE_GRAPH_DIR / "ban_do_hanh_chinh.geojson"
)