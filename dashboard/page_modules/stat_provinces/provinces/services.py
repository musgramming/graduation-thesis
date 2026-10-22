from __future__ import annotations
from functools import lru_cache

import polars as pl
import plotly.graph_objects as go

from data import BANG_DIEM


PROVINCE_CODE_COLUMN = "_province_code"


def add_province_code(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    """
    Extract mã tỉnh/thành từ 2 ký tự đầu của SOBAODANH.
    """
    return lf.with_columns(
        pl.col("SOBAODANH")
        .str.slice(0, 2)
        .alias(PROVINCE_CODE_COLUMN)
    )


def apply_score_filters(
    lf,
    subject,
    include_zero,
    include_failed,
):
    lf = lf.filter(pl.col(subject).is_not_null())

    if not include_failed:
        lf = lf.filter(pl.col("is_eligible"))

    if not include_zero:
        lf = lf.filter(pl.col(subject) > 0)

    return lf


def build_statistics_query(
    province_lf: pl.LazyFrame,
    subject: str,
) -> pl.LazyFrame:
    score = pl.col(subject)

    return province_lf.select([
        score.count().alias("count"),
        score.mean().alias("mean"),
        score.median().alias("median"),
        score.quantile(0.25).alias("q1"),
        score.quantile(0.75).alias("q3"),
        score.std().alias("std"),
        score.skew().alias("skew"),

        (score >= 9.0).sum().alias("ge_9"),
        ((score >= 9.0) & (score < 9.25)).sum().alias("score_9_0"),
        ((score >= 9.25) & (score < 9.5)).sum().alias("score_9_25"),
        ((score >= 9.5) & (score < 9.75)).sum().alias("score_9_5"),
        ((score >= 9.75) & (score < 10.0)).sum().alias("score_9_75"),
        (score == 10.0).sum().alias("score_10_0"),

        (score <= 1.0).sum().alias("score_failed"),
        (score < 5.0).sum().alias("score_below_5"),
        (score == 0.0).sum().alias("score_zero"),
    ])


def build_ranking_query(
    lf: pl.LazyFrame,
    subject: str,
) -> pl.LazyFrame:
    """
    Tính điểm trung bình của từng tỉnh/thành và xếp hạng toàn quốc.
    """
    return (
        lf
        .group_by(PROVINCE_CODE_COLUMN)
        .agg(
            pl.col(subject)
            .mean()
            .alias("mean")
        )
        .filter(
            pl.col("mean").is_not_null()
        )
        .with_columns(
            pl.col("mean")
            .rank(
                method="dense",
                descending=True,
            )
            .alias("rank")
        )
    )


# =====================================================================
# DÙNG LRU_CACHE ĐỂ GIỮ BẢNG XẾP HẠNG TRÊN RAM, TRÁNH QUÉT LẠI TRIỆU DÒNG
# =====================================================================
@lru_cache(maxsize=32)
def get_cached_ranking(year: int, subject: str, include_zero: bool, include_failed: bool) -> pl.DataFrame:
    lf = (
        BANG_DIEM[year]
        .select([
            "SOBAODANH",
            "is_eligible",
            subject,
        ])
    )
    lf = add_province_code(lf)
    lf = apply_score_filters(lf, subject, include_zero, include_failed)
    
    ranking_query = build_ranking_query(lf, subject)
    return ranking_query.collect()  # Kết quả trả về chỉ đúng 63 dòng (cực kỳ nhẹ)


HISTOGRAM_BIN_WIDTH = 0.25


def build_histogram_query(
    province_lf: pl.LazyFrame,
    subject: str,
) -> pl.LazyFrame:
    return (
        province_lf
        .select(
            (
                (
                    pl.col(subject)
                    / HISTOGRAM_BIN_WIDTH
                )
                .floor()
                * HISTOGRAM_BIN_WIDTH
            )
            .alias("bin")
        )
        .group_by("bin")
        .agg(
            pl.len().alias("count")
        )
        .sort("bin")
    )


def calculate_province_analysis(
    year: int,
    subject: str,
    province: str,
    include_zero: bool,
    include_failed: bool,
):
    lf = (
        BANG_DIEM[year]
        .select([
            "SOBAODANH",
            "is_eligible",
            subject,
        ])
    )

    lf = add_province_code(lf)

    lf = apply_score_filters(
        lf=lf,
        subject=subject,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    province_lf = lf.filter(
        pl.col(PROVINCE_CODE_COLUMN) == province
    )

    statistics_query = build_statistics_query(
        province_lf,
        subject,
    )

    histogram_query = build_histogram_query(
        province_lf,
        subject,
    )

    # 1. Chỉ collect thống kê riêng của tỉnh và histogram (rất nhỏ và nhanh)
    statistics, histogram = pl.collect_all([
        statistics_query,
        histogram_query,
    ])

    statistics = statistics.row(0, named=True)

    # 2. Lấy bảng xếp hạng từ RAM thông qua cache (không tốn tài nguyên quét lại)
    ranking = get_cached_ranking(year, subject, include_zero, include_failed)

    selected_rank = ranking.filter(
        pl.col(PROVINCE_CODE_COLUMN) == province
    )

    if selected_rank.height:
        rank = int(selected_rank["rank"][0])
    else:
        rank = None

    return {
        "statistics": statistics,
        "rank": rank,
        "total_provinces": ranking.height,
        "histogram": histogram,
    }


def build_histogram_figure(
    histogram: pl.DataFrame,
    subject: str,
):
    if histogram.height == 0:
        return go.Figure()

    x = histogram["bin"].to_list()
    y = histogram["count"].to_list()

    figure = go.Figure(
        go.Bar(
            x=x,
            y=y,
            width=0.24,
            hovertemplate=(
                "Điểm: %{x:.2f}"
                "<br>Số thí sinh: %{y:,}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        xaxis_title="Điểm",
        yaxis_title="Số thí sinh",
        bargap=0,
        margin={
            "l": 40,
            "r": 20,
            "t": 20,
            "b": 40,
        },
        hovermode="x",
    )

    figure.update_xaxes(
        range=[0, 10],
        dtick=1,
    )

    return figure