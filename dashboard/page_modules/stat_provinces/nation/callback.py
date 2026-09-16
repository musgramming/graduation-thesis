from __future__ import annotations

import json

from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import polars as pl

from data import BAN_DO_HANH_CHINH

from .services import calculate_nation_analysis
from .list_of_id import pid


def _format_number(
    value,
    digits: int = 2,
) -> str:
    """
    Format số để hiển thị trên dashboard.
    """

    if value is None:
        return "--"

    return f"{value:.{digits}f}"


def _build_histogram(
    histogram
):
    """
    Vẽ histogram từ bảng bin đã được Polars tính sẵn.

    Không truyền toàn bộ danh sách điểm sang Plotly.
    """

    x_values = histogram["score"].to_list()
    counts = histogram["count"].to_list()
    bin_starts = histogram["bin_start"].to_list()
    bin_ends = histogram["bin_end"].to_list()

    customdata = [
        [
            start,
            end,
        ]
        for start, end in zip(
            bin_starts,
            bin_ends,
        )
    ]

    fig = px.bar(
        x=x_values,
        y=counts,
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
        margin=dict(
            l=40,
            r=20,
            t=20,
            b=40,
        ),
        bargap=0.05,
    )

    fig.update_xaxes(
        range=[0, 10],
        dtick=1,
    )

    return fig





def _build_province_map(
    province_statistics,
):
    """
    Tạo bản đồ choropleth theo điểm trung bình tỉnh.

    GeoJSON:
        properties.ten_tinh

    Data:
        _province_name
    """

    geojson = json.loads(
        BAN_DO_HANH_CHINH.to_json()
    )

    map_df = province_statistics.to_pandas()

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="_province_name",
        featureidkey="properties.ten_tinh",
        color="mean",
        color_continuous_scale="Viridis",
        projection="mercator",
        hover_name="_province_name",
        hover_data={
            "_province_name": False,
            "mean": ":.2f",
            "median": ":.2f",
            "count": ":,",
        },
        labels={
            "mean": "Điểm TB",
            "median": "Trung vị",
            "count": "Số thí sinh",
        },
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
    )

    fig.update_layout(
        title=None,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0,
        ),
        coloraxis_colorbar=dict(
            title="Điểm TB",
        ),
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
    Tính toán và cập nhật toàn bộ dashboard Cả nước.
    """

    if not n_clicks:
        raise PreventUpdate

    if subject is None or year is None:
        raise PreventUpdate

    options = options or []

    include_zero = "include_zero" in options
    include_failed = "include_failed" in options

    # =========================================================
    # CHẠY PHÂN TÍCH
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
    # KPI
    # =========================================================
    nation_mean = _format_number(
        statistics["mean"]
    )

    # =========================================================
    # STATISTICS
    # =========================================================
    stat_mean = _format_number(
        statistics["mean"]
    )

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
        histogram=histogram,
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
    #
    # Giữ key nội bộ:
    # rank
    # _province_name
    # mean
    # median
    #
    # DataTable sẽ chịu trách nhiệm hiển thị tên tiếng Việt.
    #
    province_table = (
        province_statistics
        .select(
            [
                "rank",
                "_province_name",
                "mean",
                "median",
            ]
        )
        .with_columns(
            [
                pl.col("mean").round(2),
                pl.col("median").round(2),
            ]
        )
        .to_dicts()
    )

    # =========================================================
    # HIỂN THỊ DASHBOARD
    # =========================================================
    dashboard_class = "opacity-100"

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
        dashboard_class,
    )