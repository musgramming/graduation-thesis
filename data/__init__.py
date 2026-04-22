from pathlib import Path
import polars as pl

# Lấy đường dẫn của chính thư mục chứa file này (thư mục data)
DATA_DIR = Path(__file__).parent 

# Trỏ đúng vào combs_scores nằm bên trong data
BASE_DIR = DATA_DIR / "combs_scores"
TO_HOP_PATH = DATA_DIR / "bang_to_hop_mon.csv"

# Kiểm tra xem file có tồn tại không để tránh lỗi im lặng
if not TO_HOP_PATH.exists():
    print(f"⚠️ Cảnh báo: Không tìm thấy file {TO_HOP_PATH}")

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
    int(f.stem.split('_')[-1]): pl.scan_parquet(f) 
    for f in BASE_DIR.glob("bang_diem_to_hop_*.parquet")
}


# Chuyển DataFrame thành một danh sách Python đơn thuần
danh_sach_don_thuan = (
    TO_HOP.select(["Môn 1", "Môn 2", "Môn 3"]).unpivot(variable_name="Số thứ tự", value_name="Tên môn")
    .select("Tên môn")
    .unique()
    .collect()
    .get_column("Tên môn")
    .to_list()
)

# Tạo options cho Dropdown
BANG_CHON_MON = [
    {
        "label": mon, 
        "value": mon
    } for mon in danh_sach_don_thuan if mon not in ["Toán", "Văn"] # Lưu ý tên chính xác của môn
]
