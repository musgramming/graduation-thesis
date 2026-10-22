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
    Chuẩn bị LazyFrame tối thiểu cần thiết cho dashboard.

    Sau khi filter xong, DataFrame cuối chỉ giữ:
        - subject
        - _province_name

    Không giữ lại SOBAODANH hoặc is_eligible vì các cột này
    không còn được sử dụng trong các bước tính toán phía sau.
    """

    year = str(year)

    if year not in BANG_DIEM:
        raise ValueError(
            f"Không có dữ liệu điểm cho năm {year}"
        )

    if year not in BANG_QUY_DOI_TINH_THANH:
        raise ValueError(
            f"Không có bảng mã tỉnh cho năm {year}"
        )

    mapping = BANG_QUY_DOI_TINH_THANH[year]

    if not mapping:
        raise ValueError(
            f"Bảng mã tỉnh năm {year} đang rỗng"
        )

    # ---------------------------------------------------------
    # Chỉ đọc đúng những cột cần thiết từ Parquet.
    # ---------------------------------------------------------

    lf = BANG_DIEM[year].select(
        [
            "SOBAODANH",
            subject,
            "is_eligible",
        ]
    )

    # ---------------------------------------------------------
    # Mã tỉnh nằm ở 2 ký tự đầu của SOBAODANH.
    # ---------------------------------------------------------

    lf = lf.with_columns(
        pl.col("SOBAODANH")
        .str.slice(0, 2)
        .alias("_province_code")
    )

    # ---------------------------------------------------------
    # Mapping mã tỉnh cũ -> tên tỉnh hiện tại.
    #
    # Ví dụ:
    # 08 -> Lào Cai
    # 13 -> Lào Cai
    # ---------------------------------------------------------

    mapping_df = pl.LazyFrame(
        {
            "_province_code": list(mapping.keys()),
            "_province_name": list(mapping.values()),
        }
    )

    lf = lf.join(
        mapping_df,
        on="_province_code",
        how="left",
    )

    # ---------------------------------------------------------
    # Filter.
    #
    # Làm filter trước khi collect để giảm dữ liệu phải đưa
    # vào RAM.
    # ---------------------------------------------------------

    lf = lf.filter(
        pl.col("_province_name").is_not_null()
    )

    lf = lf.filter(
        pl.col(subject).is_not_null()
    )

    if not include_zero:
        lf = lf.filter(
            pl.col(subject) != 0
        )

    if not include_failed:
        lf = lf.filter(
            pl.col("is_eligible")
        )

    # ---------------------------------------------------------
    # QUAN TRỌNG:
    #
    # Sau toàn bộ filter, bỏ:
    #   SOBAODANH
    #   is_eligible
    #   _province_code
    #
    # DataFrame collect cuối cùng chỉ còn 2 cột.
    # ---------------------------------------------------------

    return lf.select(
        [
            subject,
            "_province_name",
        ]
    )


def _calculate_statistics(
    df: pl.DataFrame,
    subject: str,
) -> dict:
    """
    Tính thống kê toàn quốc từ DataFrame đã collect.
    """

    result = (
        df.select(
            [
                pl.col(subject)
                .mean()
                .alias("mean"),

                pl.col(subject)
                .median()
                .alias("median"),

                pl.col(subject)
                .quantile(0.25)
                .alias("q1"),

                pl.col(subject)
                .quantile(0.75)
                .alias("q3"),

                pl.col(subject)
                .std()
                .alias("std"),

                pl.col(subject)
                .skew()
                .alias("skew"),

                pl.len()
                .alias("count"),
            ]
        )
        .row(
            0,
            named=True,
        )
    )

    return result


def _calculate_province_statistics(
    df: pl.DataFrame,
    subject: str,
) -> pl.DataFrame:
    """
    Tính thống kê theo tỉnh hiện tại.
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
    Tính histogram bằng Polars.

    Chỉ trả về khoảng 40 dòng.
    """

    bin_width = (
        SCORE_MAX - SCORE_MIN
    ) / bins

    histogram = (
        df.select(
            pl.col(subject).alias("score")
        )
        .with_columns(
            (
                (
                    (
                        pl.col("score")
                        - SCORE_MIN
                    )
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

    # ---------------------------------------------------------
    # Đảm bảo có đủ 40 bin.
    # ---------------------------------------------------------

    all_bins = pl.DataFrame(
        {
            "_bin": range(bins),
        }
    )

    return (
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





@lru_cache(maxsize=8)
def calculate_nation_analysis(
    year: str,
    subject: str,
    include_zero: bool = True,
    include_failed: bool = True,
) -> dict:
    year = str(year)

    # 1. Lấy LazyFrame cơ sở đã qua filter (chưa collect!)
    lf = _prepare_score_data(
        year=year,
        subject=subject,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    # 2. Xây dựng các Lazy Query tổng hợp (chỉ gom nhóm, không giữ dữ liệu thô)
    
    # Thống kê toàn quốc (Trả về 1 dòng duy nhất)
    lf_stats = lf.select([
        pl.col(subject).mean().alias("mean"),
        pl.col(subject).median().alias("median"),
        pl.col(subject).quantile(0.25).alias("q1"),
        pl.col(subject).quantile(0.75).alias("q3"),
        pl.col(subject).std().alias("std"),
        pl.col(subject).skew().alias("skew"),
        pl.len().alias("count"),
    ])

    # Thống kê theo tỉnh (Trả về đúng 63 dòng)
    lf_province = (
        lf.group_by("_province_name")
        .agg([
            pl.col(subject).mean().alias("mean"),
            pl.col(subject).median().alias("median"),
            pl.len().alias("count"),
        ])
        .sort("mean", descending=True, nulls_last=True)
        .with_row_index("rank", offset=1)
    )

    # Thống kê Histogram (Trả về đúng 40 dòng bin)
    bin_width = (SCORE_MAX - SCORE_MIN) / HISTOGRAM_BINS
    lf_hist = (
        lf.select(pl.col(subject).alias("score"))
        .with_columns(
            ((pl.col("score") - SCORE_MIN) / bin_width)
            .floor().cast(pl.Int32).clip(0, HISTOGRAM_BINS - 1)
            .alias("_bin")
        )
        .group_by("_bin")
        .agg(pl.len().alias("count"))
    )

    # 3. COLLECT ĐỒNG THỜI CÁC BẢNG KẾT QUẢ SIÊU NHỎ NÀY BẰNG pl.collect_all
    df_stats, province_statistics, histogram_raw = pl.collect_all([
        lf_stats, 
        lf_province, 
        lf_hist
    ])

    statistics = df_stats.row(0, named=True)

    all_bins = pl.DataFrame({"_bin": range(HISTOGRAM_BINS)})
    histogram = (
        all_bins
        .join(histogram_raw, on="_bin", how="left")
        .with_columns(
            pl.col("count").fill_null(0).cast(pl.Int64),
            (pl.lit(SCORE_MIN) + (pl.col("_bin") + 0.5) * bin_width).alias("score"),
            (pl.lit(SCORE_MIN) + pl.col("_bin") * bin_width).alias("bin_start"),
            (pl.lit(SCORE_MIN) + (pl.col("_bin") + 1) * bin_width).alias("bin_end"),
        )
        .sort("_bin")
    )

    return {
        "year": year,
        "subject": subject,
        "statistics": statistics,
        "province_statistics": province_statistics,
        "histogram": histogram,
    }