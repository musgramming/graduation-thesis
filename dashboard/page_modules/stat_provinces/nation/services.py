from __future__ import annotations

from functools import lru_cache
import polars as pl

from data import (
    BANG_DIEM,
    BANG_QUY_DOI_TINH_THANH,
)


HISTOGRAM_BINS = 40
SCORE_MIN = 0.0
SCORE_MAX = 10.0


def _prepare_score_data(
    year: str,
    subject: str,
    include_zero: bool,
    include_failed: bool,
) -> pl.LazyFrame:
    """
    Chuẩn bị LazyFrame điểm thi đã:
    - chọn đúng năm
    - thêm mã tỉnh từ SOBAODANH
    - đổi mã tỉnh -> tên tỉnh hiện tại
    - lọc điểm null
    - lọc điểm 0 nếu cần
    - lọc thí sinh trượt nếu cần
    """

    year = str(year)

    if year not in BANG_DIEM:
        raise ValueError(f"Không có dữ liệu điểm cho năm {year}")

    if year not in BANG_QUY_DOI_TINH_THANH:
        raise ValueError(f"Không có bảng mã tỉnh cho năm {year}")

    mapping = BANG_QUY_DOI_TINH_THANH[year]

    if not mapping:
        raise ValueError(f"Bảng mã tỉnh năm {year} đang rỗng")

    lf = BANG_DIEM[year]

    # SOBAODANH có dạng mã tỉnh + số báo danh
    lf = lf.with_columns(
        pl.col("SOBAODANH")
        .str.slice(0, 2)
        .alias("_province_code")
    )

    # Tạo bảng:
    #
    # _province_code | _province_name
    # 08             | Lào Cai
    # 13             | Lào Cai
    #
    # Việc này rất quan trọng đối với dữ liệu 2025,
    # vì nhiều mã cũ có thể thuộc cùng một tỉnh hiện tại.
    mapping_df = pl.DataFrame(
        {
            "_province_code": list(mapping.keys()),
            "_province_name": list(mapping.values()),
        }
    ).lazy()

    lf = lf.join(
        mapping_df,
        on="_province_code",
        how="left",
    )

    # Chỉ lấy những cột cần thiết.
    lf = lf.select(
        [
            "SOBAODANH",
            subject,
            "is_eligible",
            "_province_name",
        ]
    )

    # Không tính những dòng không xác định được tỉnh.
    lf = lf.filter(
        pl.col("_province_name").is_not_null()
    )

    # Điểm null không thể tham gia thống kê.
    lf = lf.filter(
        pl.col(subject).is_not_null()
    )

    # Loại điểm 0 nếu người dùng không cho phép tính.
    if not include_zero:
        lf = lf.filter(
            pl.col(subject) != 0
        )

    # is_eligible:
    # True  = đủ điều kiện
    # False = trượt
    #
    # Nếu không cho phép tính cả người trượt,
    # chỉ giữ những người đủ điều kiện.
    if not include_failed:
        lf = lf.filter(
            pl.col("is_eligible") == True
        )

    return lf


def _calculate_statistics(
    df: pl.DataFrame,
    subject: str,
) -> dict:
    """
    Tính các thống kê toàn quốc từ DataFrame đã collect.

    Không đọc lại Parquet.
    """
    result = (
        df.select(
            [
                pl.col(subject).mean().alias("mean"),
                pl.col(subject).median().alias("median"),
                pl.col(subject).quantile(0.25).alias("q1"),
                pl.col(subject).quantile(0.75).alias("q3"),
                pl.col(subject).std().alias("std"),
                pl.col(subject).skew().alias("skew"),
                pl.len().alias("count"),
            ]
        )
        .row(0, named=True)
    )

    return {
        "mean": result["mean"],
        "median": result["median"],
        "q1": result["q1"],
        "q3": result["q3"],
        "std": result["std"],
        "skew": result["skew"],
        "count": result["count"],
    }


def _calculate_province_statistics(
    df: pl.DataFrame,
    subject: str,
) -> pl.DataFrame:
    """
    Tính thống kê theo tỉnh.

    Group theo _province_name thay vì _province_code
    để xử lý đúng trường hợp nhiều mã tỉnh cũ
    được sáp nhập thành một tỉnh hiện tại.
    """

    return (
        df.group_by("_province_name")
        .agg(
            [
                pl.col(subject)
                .mean()
                .alias("mean"),

                pl.col(subject)
                .median()
                .alias("median"),

                pl.len()
                .alias("count"),
            ]
        )
        .sort(
            "mean",
            descending=True,
            nulls_last=True,
        )
        .with_row_index(
            "rank",
            offset=1,
        )
    )


def _calculate_histogram(
    df: pl.DataFrame,
    subject: str,
    bins: int = HISTOGRAM_BINS,
) -> pl.DataFrame:
    """
    Tính histogram ngay bằng Polars.

    Điểm được chia thành các khoảng đều nhau từ 0 -> 10.
    Kết quả chỉ còn khoảng 40 dòng thay vì phải gửi hơn
    một triệu điểm sang Plotly.
    """
    bin_width = (SCORE_MAX - SCORE_MIN) / bins

    histogram = (
        df.select(
            pl.col(subject).alias("score")
        )
        .with_columns(
            (
                (
                    (pl.col("score") - SCORE_MIN)
                    / bin_width
                )
                .floor()
                .cast(pl.Int32)
                .clip(0, bins - 1)
            ).alias("_bin")
        )
        .group_by("_bin")
        .agg(
            pl.len().alias("count")
        )
    )

    # Tạo đầy đủ các bin kể cả những bin có count = 0.
    all_bins = pl.DataFrame(
        {
            "_bin": list(range(bins)),
        }
    )

    histogram = (
        all_bins
        .join(
            histogram,
            on="_bin",
            how="left",
        )
        .with_columns(
            pl.col("count")
            .fill_null(0)
            .cast(pl.Int64),

            (
                pl.lit(SCORE_MIN)
                + (
                    pl.col("_bin") + 0.5
                ) * bin_width
            ).alias("score"),

            (
                pl.lit(SCORE_MIN)
                + pl.col("_bin") * bin_width
            ).alias("bin_start"),

            (
                pl.lit(SCORE_MIN)
                + (
                    pl.col("_bin") + 1
                ) * bin_width
            ).alias("bin_end"),
        )
        .sort("_bin")
    )

    return histogram





@lru_cache(maxsize=32)
def calculate_nation_analysis(
    year: str,
    subject: str,
    include_zero: bool = True,
    include_failed: bool = True,
) -> dict:
    """
    Chạy toàn bộ phân tích cả nước.

    Điểm tối ưu chính:
    ------------------
    Parquet -> LazyFrame -> FILTER/JOIN -> collect() đúng 1 lần
                                      |
                                      +-> statistics
                                      +-> province statistics
                                      +-> histogram

    Như vậy không phải scan Parquet 3 lần như phiên bản cũ.
    """
    year = str(year)

    lf = _prepare_score_data(
        year=year,
        subject=subject,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    # =========================================================
    # COLLECT DUY NHẤT MỘT LẦN
    # =========================================================
    df = lf.collect()

    if df.is_empty():
        raise ValueError(
            "Không có dữ liệu phù hợp với các điều kiện đã chọn."
        )

    # Sau khi collect, tất cả các phép tính phía dưới đều
    # chạy trên DataFrame trong memory, không đọc lại Parquet.
    statistics = _calculate_statistics(
        df=df,
        subject=subject,
    )

    province_statistics = _calculate_province_statistics(
        df=df,
        subject=subject,
    )

    histogram = _calculate_histogram(
        df=df,
        subject=subject,
    )

    return {
        "year": year,
        "subject": subject,
        "statistics": statistics,
        "province_statistics": province_statistics,
        "histogram": histogram,
    }