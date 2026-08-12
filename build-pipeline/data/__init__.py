import json5
import polars as pl


# ============================================================
# DANH SÁCH MÔN HỌC
# ============================================================

MON_BAT_BUOC = [
    "Toán",
    "Văn",
]

MON_TU_CHON = [
    "Lí",
    "Hóa",
    "Sinh",
    "Tin",
    "Công nghệ công nghiệp",
    "Công nghệ nông nghiệp",
    "Sử",
    "Địa",
    "Giáo dục kinh tế và pháp luật",
    "Ngoại ngữ",
]


# ============================================================
# BẢNG MÃ NGOẠI NGỮ
# ============================================================
NGOAI_NGU = {
    "N1": "Anh",
    "N2": "Nga",
    "N3": "Pháp",
    "N4": "Trung",
    "N5": "Đức",
    "N6": "Nhật",
    "N7": "Hàn"
}


# ============================================================
# BẢNG QUY ĐỔI CỘT
# ============================================================

"""
{
    "năm": {
        "drop": [
            Danh sách cột cần bỏ
        ],
        "rename": {
            "tên cũ": "tên mới"
        }
    }
}
"""

with open(
    "./data/mapping/bang_quy_doi_schema.jsonc",
    mode="r",
    encoding="utf-8",
) as f:
    COLUMN_MAPPING = json5.load(f)


# ============================================================
# BẢNG KẾT NỐI FILE
# ============================================================

"""
{
    "năm": {
        "File chính": file được đưa vào hàm tien_xu_ly_bang_chinh,
        "File phụ": file được đưa vào hàm tien_xu_ly_bang_phu
    }
}
"""

with open(
    "./data/mapping/bang_ket_noi_file.jsonc",
    mode="r",
    encoding="utf-8",
) as f:
    BANG_QUY_DOI_FILE = json5.load(f)


# ============================================================
# BẢNG TỔ HỢP MÔN
# ============================================================

BANG_TO_HOP_MON = pl.scan_csv(
    "./data/mapping/bang_to_hop_mon.csv"
)