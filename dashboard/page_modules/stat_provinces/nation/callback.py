from __future__ import annotations

import time
import traceback

import polars as pl
import plotly.express as px

from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from data import BAN_DO_HANH_CHINH_GEOJSON
from .services import calculate_nation_analysis
from .list_of_id import pid





def _format_number(
    value,
    digits: int = 2,
) -> str:
    if value is None:
        return "--"
    return f"{value:.{digits}f}"





def _build_histogram(histogram: pl.DataFrame):
    """
    Histogram đã được aggregate bằng Polars.
    Chỉ truyền vài chục bin sang Plotly.
    """
    customdata = list(
        zip(
            histogram["bin_start"].to_list(),
            histogram["bin_end"].to_list(),
        )
    )

    fig = px.bar(
        x=histogram["score"].to_list(),
        y=histogram["count"].to_list(),
        labels={
            "x": "Điểm",
            "y": "Số thí sinh",
        },
    )

    fig.update_traces(
        customdata=customdata,
        hovertemplate=(
            "Khoảng điểm: "
            "%{customdata[0]:.2f}"
            " - "
            "%{customdata[1]:.2f}"
            "<br>"
            "Số thí sinh: %{y:,}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        title=None,
        xaxis_title="Điểm",
        yaxis_title="Số thí sinh",
        margin={
            "l": 40,
            "r": 20,
            "t": 20,
            "b": 40,
        },
        bargap=0.05,
    )

    fig.update_xaxes(
        range=[0, 10],
        dtick=1,
    )

    return fig






def _build_province_map(
    province_statistics: pl.DataFrame,
):
    map_df = province_statistics.to_pandas()

    fig = px.choropleth(
        map_df,
        geojson=BAN_DO_HANH_CHINH_GEOJSON,
        locations="_province_name",
        featureidkey="properties.ten_tinh",
        color="mean",
        color_continuous_scale=[
            [0.00, "#F1F5F9"],
            [0.20, "#DBEAFE"],
            [0.40, "#93C5FD"],
            [0.60, "#60A5FA"],
            [0.80, "#2563EB"],
            [1.00, "#1D4ED8"],
        ],
        projection="mercator",

        # Tên tỉnh dùng làm tiêu đề hover
        hover_name="_province_name",

        # Dữ liệu bổ sung cho hover
        custom_data=[
            "_province_name",
            "median",
            "count",
        ],
    )

    # =========================================================
    # HOVER
    # =========================================================
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b>"
            "<br>"
            "<span style='color:#64748B'>Điểm trung bình</span>"
            "  <b>%{z:.2f}</b>"
            "<br>"
            "<span style='color:#64748B'>Trung vị</span>"
            "  <b>%{customdata[1]:.2f}</b>"
            "<br>"
            "<span style='color:#64748B'>Số thí sinh</span>"
            "  <b>%{customdata[2]:,}</b>"
            "<extra></extra>"
        ),
        marker={
            "line": {
                "color": "rgba(255,255,255,0.9)",
                "width": 0.8,
            }
        },
    )

    # =========================================================
    # GEO
    # =========================================================
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )

    # =========================================================
    # LAYOUT
    # =========================================================
    fig.update_layout(
        title=None,

        # Nền trong suốt để hòa với Card
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        margin={
            "l": 10,
            "r": 10,
            "t": 10,
            "b": 10,
        },

        # Font tổng thể
        font={
            "family": "Inter, system-ui, -apple-system, BlinkMacSystemFont, "
                       "'Segoe UI', sans-serif",
            "size": 13,
            "color": "#334155",
        },

        # Colorbar
        coloraxis_colorbar={
            "title": {
                "text": "Điểm TB",
                "font": {
                    "size": 12,
                    "color": "#475569",
                },
            },
            "tickfont": {
                "size": 11,
                "color": "#64748B",
            },
            "thickness": 12,
            "len": 0.55,
            "x": 0.98,
            "xanchor": "right",
            "y": 0.5,
            "outlinewidth": 0,
            "bgcolor": "rgba(255,255,255,0.75)",
        },

        # Hover box
        hoverlabel={
            "bgcolor": "white",
            "bordercolor": "#E2E8F0",
            "font": {
                "family": "Inter, system-ui, -apple-system, "
                           "BlinkMacSystemFont, 'Segoe UI', sans-serif",
                "size": 13,
                "color": "#0F172A",
            },
            "align": "left",
        },

        # Không cần toolbar
        dragmode=False,
    )

    return fig





@callback(
    Output(pid("nation-mean"), "children"),
    Output(pid("nation-stat-mean"), "children"),
    Output(pid("nation-stat-median"), "children"),
    Output(pid("nation-stat-quartiles"), "children"),
    Output(pid("nation-stat-std"), "children"),
    Output(pid("nation-stat-skew"), "children"),
    Output(pid("nation-histogram"), "figure"),
    Output(pid("nation-map"), "figure"),
    Output(pid("nation-province-table"), "data"),
    Output(pid("nation-dashboard-result"), "className"),

    Input(pid("nation-button"), "n_clicks"),

    State(pid("nation-subject"), "value"),
    State(pid("nation-year"), "value"),
    State(pid("nation-options"), "value"),

    prevent_initial_call=True,
)
def update_nation_dashboard(
    n_clicks,
    subject,
    year,
    options,
):
    """
    Tính toán và cập nhật dashboard Cả nước.
    """

    if not n_clicks:
        raise PreventUpdate

    if subject is None or year is None:
        raise PreventUpdate

    options = options or []

    include_zero = "include_zero" in options
    include_failed = "include_failed" in options

    try:
        start_time = time.perf_counter()

        # =========================================================
        # PHÂN TÍCH
        # =========================================================

        result = calculate_nation_analysis(
            year=str(year),
            subject=subject,
            include_zero=include_zero,
            include_failed=include_failed,
        )

        statistics = result["statistics"]
        province_statistics = result["province_statistics"]
        histogram = result["histogram"]

        # =========================================================
        # STATISTICS
        # =========================================================

        mean = statistics["mean"]

        nation_mean = _format_number(mean)
        stat_mean = nation_mean

        stat_median = _format_number(
            statistics["median"]
        )

        stat_quartiles = (
            f"{_format_number(statistics['q1'])}"
            f" - "
            f"{_format_number(statistics['q3'])}"
        )

        stat_std = _format_number(
            statistics["std"]
        )

        stat_skew = _format_number(
            statistics["skew"]
        )

        # =========================================================
        # HISTOGRAM
        # =========================================================

        histogram_figure = _build_histogram(
            histogram
        )

        # =========================================================
        # MAP
        # =========================================================

        province_map = _build_province_map(
            province_statistics
        )

        # =========================================================
        # TABLE
        # =========================================================

        province_table = (
            province_statistics
            .select(
                [
                    pl.col("rank").alias("Hạng"),
                    pl.col("_province_name").alias("Tỉnh thành"),
                    pl.col("mean")
                    .cast(pl.Decimal(4, 2))
                    .alias("Trung bình"),
                    pl.col("median")
                    .cast(pl.Decimal(4, 2))
                    .alias("Trung vị"),
                ]
            )
            .to_dicts()
        )



        end_time = time.perf_counter()
        print(f"Thời gian chạy truy vấn theo cả nước: {(end_time - start_time):.4} s")


        # =========================================================
        # RETURN
        # =========================================================

        return (
            nation_mean,
            stat_mean,
            stat_median,
            stat_quartiles,
            stat_std,
            stat_skew,
            histogram_figure,
            province_map,
            province_table,
            "opacity-100",
        )

    except Exception:
        print("--- LỖI XẢY RA TRONG CALLBACK ---")
        traceback.print_exc()
        print("---------------------------------")

        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )