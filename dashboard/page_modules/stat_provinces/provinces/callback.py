from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate

from .list_of_id import pid
from .services import calculate_province_analysis, build_histogram_figure
from data import BANG_QUY_DOI_TINH_THANH
from utils.exception import todo, unimplemented, unreachable


@callback(
    Output(pid("province-name"), "options"),
    Output(pid("province-name"), "value"),
    Input(pid("province-year"), "value"),
    State(pid("province-name"), "value"),
    State(pid("province-name"), "options"),
)
def update_province_options(year, current_province, current_options):

    if year is None:
        return [], None

    year = str(year)

    # Lấy tên tỉnh đang được chọn từ options của năm trước
    current_province_name = next(
        (
            option["label"]
            for option in (current_options or [])
            if option["value"] == current_province
        ),
        None,
    )

    province_options = [
        {
            "label": name,
            "value": code,
        }
        for code, name
        in BANG_QUY_DOI_TINH_THANH[year].items()
    ]

    # Tìm mã của cùng tỉnh trong năm mới
    new_province_code = next(
        (
            code
            for code, name
            in BANG_QUY_DOI_TINH_THANH[year].items()
            if name == current_province_name
        ),
        None,
    )

    # Không tìm thấy → Hà Nội
    if new_province_code is None:
        new_province_code = next(
            (
                code
                for code, name
                in BANG_QUY_DOI_TINH_THANH[year].items()
                if name == "Hà Nội"
            ),
            None,
        )

    return province_options, new_province_code





@callback(
    [
        Output(pid("province-rank"), "children"),
        Output(pid("province-mean"), "children"),
        Output(pid("stat-mean"), "children"),
        Output(pid("stat-median"), "children"),
        Output(pid("stat-quartiles"), "children"),
        Output(pid("stat-std"), "children"),
        Output(pid("stat-skew"), "children"),
        Output(pid("province-histogram"), "figure"),
        Output(pid("dashboard-result"), "className"),
    ],

    Input(pid("province-button"), "n_clicks"),

    [
        State(pid("province-subject"), "value"),
        State(pid("province-year"), "value"),
        State(pid("province-name"), "value"),
        State(pid("province-options"), "value"),
    ], 
    prevent_initial_call=True,
)
def update_province_dashboard(
    n_clicks,
    subject,
    year,
    province,
    options,
):
    if not n_clicks:
        raise PreventUpdate

    if (
        subject is None
        or year is None
        or province is None
    ):
        raise PreventUpdate

    options = options or []

    include_zero = (
        "include_zero" in options
    )

    include_failed = (
        "include_failed" in options
    )

    # =========================================
    # SERVER-SIDE CALCULATION
    # =========================================

    result = calculate_province_analysis(
        year=year,
        subject=subject,
        province=province,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    statistics = result["statistics"]

    rank = result["rank"]
    total_provinces = result["total_provinces"]

    histogram = result["histogram"]

    # =========================================
    # FORMAT STATISTICS
    # =========================================

    mean = statistics["mean"]
    median = statistics["median"]
    q1 = statistics["q1"]
    q3 = statistics["q3"]
    std = statistics["std"]
    skew = statistics["skew"]

    rank_text = (
        f"#{rank} / {total_provinces}"
        if rank is not None
        else "--"
    )

    mean_text = (
        f"{mean:.2f}"
        if mean is not None
        else "--"
    )

    median_text = (
        f"{median:.2f}"
        if median is not None
        else "--"
    )

    quartiles_text = (
        f"{q1:.2f} – {q3:.2f}"
        if q1 is not None and q3 is not None
        else "--"
    )

    std_text = (
        f"{std:.2f}"
        if std is not None
        else "--"
    )

    skew_text = (
        f"{skew:.2f}"
        if skew is not None
        else "--"
    )

    # =========================================
    # HISTOGRAM
    # =========================================

    figure = build_histogram_figure(
        histogram,
        subject,
    )

    # =========================================
    # RETURN
    # =========================================

    return (
        rank_text,
        mean_text,

        mean_text,
        median_text,
        quartiles_text,
        std_text,
        skew_text,

        figure,

        "",
    )