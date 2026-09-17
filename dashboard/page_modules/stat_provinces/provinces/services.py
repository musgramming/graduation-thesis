from __future__ import annotations

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
    lf: pl.LazyFrame,
    subject: str,
    include_zero: bool,
    include_failed: bool,
) -> pl.LazyFrame:
    """
    Áp dụng các điều kiện lọc chung.
    """

    # Không tính các bản ghi không có điểm môn đang xét
    lf = lf.filter(
        pl.col(subject).is_not_null()
    )

    # Mặc định chỉ tính thí sinh đủ điều kiện tốt nghiệp
    if not include_failed:
        lf = lf.filter(
            pl.col("is_eligible")
        )

    # Mặc định không tính điểm 0
    if not include_zero:
        lf = lf.filter(
            pl.col(subject) > 0
        )

    return lf



def build_statistics_query(
    province_lf: pl.LazyFrame,
    subject: str,
) -> pl.LazyFrame:
    """
    Tạo LazyFrame tính các giá trị thống kê
    cho tỉnh đang được chọn.
    """

    return province_lf.select(
        [
            pl.col(subject).count().alias("count"),

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

            # --- CÁC CHỈ SỐ BỔ SUNG ---
            # Số lượng bài >= 9.0
            pl.col(subject).filter(pl.col(subject) >= 9.0).count().alias("ge_9"),


            # Số lượng bài điểm cao
            pl.col(subject).filter((9.0 <= pl.col(subject)) & ((pl.col(subject) < 9.25))).count().alias("score_9_0"),
            pl.col(subject).filter((9.25 <= pl.col(subject)) & ((pl.col(subject) < 9.5))).count().alias("score_9_25"),
            pl.col(subject).filter((9.5 <= pl.col(subject)) & ((pl.col(subject) < 9.75))).count().alias("score_9_5"),
            pl.col(subject).filter((9.75 <= pl.col(subject)) & ((pl.col(subject) < 10))).count().alias("score_9_75"),
            pl.col(subject).filter(pl.col(subject) == 10.0).count().alias("score_10_0"),

            # --- NHÓM RỦI RO / ĐIỂM THẤP ---
            pl.col(subject).filter(pl.col(subject) <= 1.0).count().alias("score_failed"),     # Điểm liệt
            pl.col(subject).filter(pl.col(subject) < 5.0).count().alias("score_below_5"),     # Dưới trung bình
            pl.col(subject).filter(pl.col(subject) == 0.0).count().alias("score_zero"),       # Điểm 0 tuyệt đối
        ]
    )



def build_ranking_query(
    lf: pl.LazyFrame,
    subject: str,
) -> pl.LazyFrame:
    """
    Tính điểm trung bình của từng tỉnh/thành
    và xếp hạng toàn quốc.
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
    """
    Tính toàn bộ dữ liệu cần thiết cho dashboard.

    Chỉ thực hiện một lần collect().
    """

    # -----------------------------------------
    # Base LazyFrame
    # -----------------------------------------

    lf = add_province_code(
        BANG_DIEM[year]
    )

    # -----------------------------------------
    # Apply filters
    # -----------------------------------------

    lf = apply_score_filters(
        lf=lf,
        subject=subject,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    # -----------------------------------------
    # Dữ liệu tỉnh được chọn
    # -----------------------------------------

    province_lf = lf.filter(
        pl.col(PROVINCE_CODE_COLUMN) == province
    )

    # -----------------------------------------
    # Các query
    # -----------------------------------------

    statistics_query = build_statistics_query(
        province_lf,
        subject,
    )

    ranking_query = build_ranking_query(
        lf,
        subject,
    )

    histogram_query = build_histogram_query(
        province_lf,
        subject,
    )

    # -----------------------------------------
    # COLLECT
    # -----------------------------------------

    statistics, ranking, histogram = pl.collect_all(
        [
            statistics_query,
            ranking_query,
            histogram_query,
        ]
    )

    # -----------------------------------------
    # Statistics
    # -----------------------------------------

    statistics = statistics.row(
        0,
        named=True,
    )

    # -----------------------------------------
    # Ranking
    # -----------------------------------------

    selected_rank = (
        ranking
        .filter(
            pl.col(PROVINCE_CODE_COLUMN) == province
        )
    )

    if selected_rank.height:
        rank = int(
            selected_rank["rank"][0]
        )
    else:
        rank = None

    total_provinces = ranking.height

    # -----------------------------------------
    # Return
    # -----------------------------------------

    return {
        "statistics": statistics,
        "rank": rank,
        "total_provinces": total_provinces,
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