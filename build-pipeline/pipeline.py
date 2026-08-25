import argparse
import os
import time
import itertools
from collections import defaultdict
from pathlib import Path



# Giới hạn số thread trước khi import Polars/Arrow.
os.environ["POLARS_MAX_THREADS"] = "1"
os.environ["ARROW_NUM_THREADS"] = "1"

import pandas as pd
import polars as pl

from data import (
    MON_BAT_BUOC,
    MON_TU_CHON,
    NGOAI_NGU,
    COLUMN_MAPPING,
    BANG_TO_HOP_MON,
    BANG_QUY_DOI_FILE
)

from logging_utils import (
    setup_logging,
    log_pipeline_success, 
    log_step, 
    log_success
)




def read_dataframe(file_path: str, nrows : int | None = None) -> pd.DataFrame | dict[str, pd.DataFrame]:
    ext = Path(file_path).suffix.lower()

    if ext == ".xlsx":
        sheets = pd.read_excel(
            file_path,
            sheet_name=None,
        )

        df = pd.concat(
            sheets.values(),
            ignore_index=True,
        )

        if nrows is not None:
            df = df.head(nrows)

        return df
    elif ext == ".csv":
        df = pd.read_csv(file_path)

        if nrows is not None:
            df = df.head(nrows)

        return df

    else:
        raise ValueError(
            f"Không hỗ trợ định dạng {ext}. Chỉ hỗ trợ .csv và .xlsx"
        )




def tien_xu_ly_bang_diem_chinh(file_chinh: str, year: int) -> pl.LazyFrame:
    """
    Tiền xử lý dữ liệu bảng điểm và xét tính hợp lệ của từng thí sinh
    
    Arguments:
        - file_chinh: File dữ liệu chính dạng xlsx
    """
    # B1: Kiểm tra file tồn tại chưa
    try:
        data = read_dataframe(file_chinh)
    except FileNotFoundError:
        print("Không tìm thấy file.")
        return


    # B2: Duyệt qua toàn bộ sheet trong `file_chinh`
    if isinstance(data, dict):
        # Excel nhiều sheet
        df = pd.concat(
            data.values(),
            ignore_index=True
        )
    else:
        # CSV
        df = data

    DF_CHINH = pl.LazyFrame(df)
    schema = DF_CHINH.collect_schema().names()

    if "__index_level_0__" in schema:
        DF_CHINH = DF_CHINH.drop("__index_level_0__")


    # B3: Tiền xử lý dữ liệu: 
    ## B3a. Xử lý tên các bảng
    column_mapping = COLUMN_MAPPING[str(year)]
    if column_mapping["drop"] is not None:
        DF_CHINH = DF_CHINH.drop(column_mapping["drop"])
                

    DF_CHINH = DF_CHINH.rename(
        column_mapping["rename"],
        strict=False,
    )
    
    
    ## B3b. Xử lý điểm Toán, Văn
    ## Theo quy chế, thí sinh nào không làm bài 1 trong 2 môn này thì bị điểm liệt
    DF_CHINH = DF_CHINH.with_columns([
        pl.col("Toán").cast(pl.Float32).round(2).fill_null(0),
        pl.col("Văn").cast(pl.Float32).round(2).fill_null(0),
    ])


    ## B3c. Xử lý điểm mấy môn kia
    DF_CHINH = DF_CHINH.with_columns(
        [
            pl.col(i).cast(pl.Float32).round(2)
            for i in MON_TU_CHON
        ]
    )


    ## B3d. Xử lý SBD:
    ## Theo quy chế, 
    ## 2 ký tự đầu là mã tỉnh thành (bây giờ chưa tách ra làm trường thông tin riêng)
    ## 6 ký tự sau là mã của thí sinh tại tỉnh thành đó
    DF_CHINH = DF_CHINH.with_columns(
        pl.col("SOBAODANH").cast(pl.String).str.zfill(8)
    )


    # B4: Xác định tính hợp lệ của điểm thi, gồm: 
    # - 2 môn bắt buộc (Văn, Toán) không được bị điểm liệt (dưới 1)
    # - Có đúng 2 bài tự chọn và không bài nào bị điểm liệt
    num_attempted = pl.sum_horizontal(
        pl.col(MON_TU_CHON)
            .is_not_null()
            .cast(pl.Int8)
    )

    num_passed = pl.sum_horizontal(
        (pl.col(MON_TU_CHON) > 1.0)
            .cast(pl.Int8)
    )

    DF_CHINH = DF_CHINH.with_columns([
        (
            (pl.col("Toán") > 1.0) &
            (pl.col("Văn") > 1.0) &
            (num_attempted == 2) &
            (num_passed == 2)
        ).alias("is_eligible")
    ])


    # B5: Xử lý dữ liệu môn ngoại ngữ
    bang_ngoai_ngu = (
        DF_CHINH
            .select(["SOBAODANH", "Ngoại ngữ", "Mã môn ngoại ngữ"])
            .filter(
                pl.col("Ngoại ngữ").is_not_null() &
                pl.col("Mã môn ngoại ngữ").is_not_null()
            )
            .collect()
            .pivot(
                on = "Mã môn ngoại ngữ",
                index = "SOBAODANH",
                values = "Ngoại ngữ"
            )
            .rename(NGOAI_NGU, strict=False)
            .lazy()
    )

    DF_CHINH = (
        DF_CHINH
            .drop(["Ngoại ngữ", "Mã môn ngoại ngữ"])
            .join(
                bang_ngoai_ngu, 
                on = "SOBAODANH", 
                how = "left"
            )
    )

    print(
        f"""
        Đã ghi thành công:
        - Số dòng: {DF_CHINH.select(pl.len()).collect().item()}
        - Số cột: {len(DF_CHINH.collect_schema())}
        """
    )

    return DF_CHINH





def xac_dinh_to_hop_kha_di(DF_CHINH : pl.LazyFrame) -> pl.LazyFrame:
    subjects = [i for i in DF_CHINH.collect_schema() if i not in ["SOBAODANH", "is_eligible"]]

    # B1: Xác định các tổ hợp khả dĩ

    ## B1a: Xây dựng bảng các môn mà thí sinh đã thi
    computation_subject = (
        DF_CHINH.with_columns([
            pl.concat_list([
                pl.when(pl.col(s).is_not_null())
                    .then(pl.lit(s))
                    .otherwise(None)
                for s in subjects
            ])
            .list.drop_nulls()
            .alias("Danh sách môn thi")
        ])
    ).select(["SOBAODANH", "Danh sách môn thi"])


    ## B1b: Xác định tổ hợp 3 môn trong danh sách dự thi
    def _get_combs(combs):
        if len(combs) < 3:
            return []
        return [list(c) for c in itertools.combinations(combs, 3)]

    # Giải thích: 
    # `defaultdict`` (từ `collections`) là lớp con sẽ khởi tạo một giá trị mặc định cho khóa đó
    # Ví dụ: `defaultdict(list)`` thì giá trị khởi tạo cho keys là kiểu dữ liệu `list`
    mapping_dict = defaultdict(list)
    for row in BANG_TO_HOP_MON.collect().to_dicts():
        key = frozenset((
            row["Môn 1"], 
            row["Môn 2"], 
            row["Môn 3"]
        ))
        mapping_dict[key].append(row["Tổ hợp"])

    # Giải thích
    # `frozenset` là một phiên bản không thể thay đổi của kiểu dữ liệu `set`.


    ## B1c. Sinh và phân rã tổ hợp
    df_final = (
        computation_subject.with_columns([
            pl.col("Danh sách môn thi")
                .map_elements(
                    _get_combs, 
                    return_dtype=pl.List(
                        pl.List(pl.String)
                    )
                )
                .alias("Tổ hợp 3 môn")
        ])
        .explode("Tổ hợp 3 môn", empty_as_null=True)
        .drop_nulls("Tổ hợp 3 môn")
    )


    ## B1d. Tách list thành 3 cột môn học riêng biệt, rồi ánh xạ mã tổ hợp và lọc rác
    df_final = df_final.with_columns([
        pl.col("Tổ hợp 3 môn").list.get(0).alias("Môn 1"),
        pl.col("Tổ hợp 3 môn").list.get(1).alias("Môn 2"),
        pl.col("Tổ hợp 3 môn").list.get(2).alias("Môn 3")
    ]).with_columns(
        pl.struct(["Môn 1", "Môn 2", "Môn 3"])
            .map_elements(
                lambda x : mapping_dict.get(
                    frozenset((
                        x["Môn 1"],
                        x["Môn 2"],
                        x["Môn 3"]
                    )),
                    []
                ), 
                return_dtype=pl.List(pl.String)
            )
            .alias("Tổ hợp")
    ).explode("Tổ hợp", empty_as_null=True)


    # B2: Tính toán điểm tổ hợp
    ## B2.1: Quy đổi bảng điểm về dạng long
    ## Các trường bị giữ lại: SOBAODANH, is_eligible
    ## Các trường bị đổi: 
    ## - *Danh sách môn học --> Môn
    ## - *Điểm
    df_diem_long = (
        DF_CHINH.unpivot(
            index=["SOBAODANH", "is_eligible"],
            variable_name="Môn",
            value_name="Diem_So"
        )
        .filter(pl.col("Diem_So").is_not_null())
    )


    ## B2.2: Tra cứu các cột điểm môn trong tổ hợp
    for i in range(1, 4):
        df_final = (
            df_final.join(
                df_diem_long.select(["SOBAODANH", "Môn", "Diem_So"]), 
                left_on=["SOBAODANH", f"Môn {i}"],
                right_on=["SOBAODANH", "Môn"],
                how="left"
            )
            .rename({"Diem_So" : f"Điểm {i}"})
        ) 

    
    ##B2.3: Tính tổng điểm trước khi JOIN
    df_final = df_final.with_columns(
        (
            pl.col("Điểm 1").fill_null(0) +
            pl.col("Điểm 2").fill_null(0) +
            pl.col("Điểm 3").fill_null(0)
        )
        .round(2)
        .cast(pl.Float32)
        .alias("Tổng điểm")
    )


    ## B2.4: FULL JOIN và xử lý hợp nhất cột SBD ngay lập tức
    ## Chú ý bugs: 1 mã tổ hợp có thể được gán cho 2 loại tổ hợp khác nhau, nên sử dụng max
    df_final = (
        df_final
        .group_by(["SOBAODANH", "Tổ hợp"])
        .agg(
            pl.col("Tổng điểm").max()
        )
        .join(
            DF_CHINH.select(["SOBAODANH", "is_eligible"]), 
            on = "SOBAODANH", 
            how = "full"
        )
        .with_columns([
            pl.coalesce(["SOBAODANH", "SOBAODANH_right"]).alias("SOBAODANH"),
            pl.col("is_eligible").fill_null(False).alias("Hợp lệ"),
            pl.lit(True).alias("Chương trình mới")
        ])
        .drop(["SOBAODANH_right", "is_eligible"])
    )

    print(
        f"""
        Đã ghi thành công:
        - Số dòng: {df_final.select(pl.len()).collect().item()}
        - Số cột: {len(df_final.collect_schema())}
        """
    )

    return df_final





def tien_xu_ly_bang_diem_phu(file_phu: str = None):
    if not file_phu: 
        return

    data = read_dataframe(file_phu)

    if isinstance(data, dict):
        data = pd.concat(
            data.values(),
            ignore_index=True
        )

    df_phu = (
        pl.LazyFrame(data)
        .select(["SOBAODANH"])
        .with_columns([
            pl.col("SOBAODANH").cast(pl.String).str.zfill(8), 
            pl.lit(False).alias("Chương trình mới")
        ])
    )

    return df_phu




def full_processing(year: int):

    pipeline_start = time.perf_counter()

    # ========================================================
    # Khởi tạo
    # ========================================================

    logger = setup_logging(year)

    if str(year) not in BANG_QUY_DOI_FILE:
        logger.error(
            f"Không tìm thấy cấu hình dữ liệu cho năm {year}."
        )
        return 1

    file_mapping = BANG_QUY_DOI_FILE[str(year)]
    file_chinh = file_mapping["File chính"]
    file_phu = file_mapping.get("File phụ")

    total_steps = 4 if file_phu else 3
    step = 0

    # ========================================================
    # Bước 1 — Xử lý bảng điểm chính
    # ========================================================

    step += 1
    step_start = time.perf_counter()

    log_step(
        logger,
        step,
        total_steps,
        "Đang xử lý dữ liệu bảng điểm chính",
        file_chinh,
    )

    DF_CHINH = tien_xu_ly_bang_diem_chinh(
        file_chinh,
        year,
    )

    DF_CHINH.collect().write_parquet(
        f"./output/bang_diem/bang_diem-{year}.parquet",
        compression="zstd",
        compression_level=19,
        use_pyarrow=True,
    )

    log_success(
        logger,
        time.perf_counter() - step_start,
    )

    # ========================================================
    # Bước 2 — Xác định tổ hợp khả dĩ
    # ========================================================

    step += 1
    step_start = time.perf_counter()

    log_step(
        logger,
        step,
        total_steps,
        "Đang xác định tổ hợp khả dĩ",
    )

    DF_DIEM_TO_HOP = xac_dinh_to_hop_kha_di(
        DF_CHINH,
    )

    log_success(
        logger,
        time.perf_counter() - step_start,
    )

    # ========================================================
    # Bước 3 — Xử lý bảng điểm phụ
    # ========================================================

    if file_phu:

        step += 1
        step_start = time.perf_counter()

        log_step(
            logger,
            step,
            total_steps,
            "Đang xử lý dữ liệu bảng điểm phụ",
            file_phu,
        )

        DF_PHU = tien_xu_ly_bang_diem_phu(
            file_phu,
        )

        DF_DIEM_TO_HOP = (
            DF_DIEM_TO_HOP
            .join(
                DF_PHU,
                on="SOBAODANH",
                how="full",
            )
            .with_columns([
                pl.coalesce(
                    [
                        "SOBAODANH",
                        "SOBAODANH_right",
                    ]
                ).alias("SOBAODANH"),

                pl.col("Chương trình mới")
                    .fill_null(False),
            ])
            .drop("SOBAODANH_right")
        )

        log_success(
            logger,
            time.perf_counter() - step_start,
        )

    # ========================================================
    # Bước cuối — Lưu bảng điểm tổ hợp
    # ========================================================

    step += 1
    step_start = time.perf_counter()

    log_step(
        logger,
        step,
        total_steps,
        "Đang lưu bảng điểm tổ hợp",
    )

    (
        DF_DIEM_TO_HOP
        .select([
            "SOBAODANH",
            "Tổ hợp",
            "Tổng điểm",
            "Hợp lệ",
            "Chương trình mới",
        ])
        .collect()
        .write_parquet(
            f"./output/bang_diem_to_hop/bang_diem_to_hop-{year}.parquet",
            compression="zstd",
            compression_level=19,
            use_pyarrow=True,
        )
    )

    log_success(
        logger,
        time.perf_counter() - step_start,
    )

    # ========================================================
    # Hoàn tất
    # ========================================================

    log_pipeline_success(
        logger,
        time.perf_counter() - pipeline_start,
    )

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-y",
        "--year",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    raise SystemExit(
        full_processing(args.year)
    )