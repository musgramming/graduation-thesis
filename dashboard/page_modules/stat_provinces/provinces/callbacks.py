from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate

from .list_of_id import pid
from .services import calculate_province_analysis, build_histogram_figure

from utils.check_performance import export_performance
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
        Output(pid("province-mean"), "className"),
        Output(pid("stat-count"), "children"),
        Output(pid("stat-mean"), "children"),
        Output(pid("stat-median"), "children"),
        Output(pid("stat-quartiles"), "children"),
        Output(pid("stat-std"), "children"),
        Output(pid("stat-skew"), "children"),
        Output(pid("stat-ge-9"), "children"),
        Output(pid("stat-9-0"), "children"),
        Output(pid("stat-9-25"), "children"),
        Output(pid("stat-9-5"), "children"),
        Output(pid("stat-9-75"), "children"),
        Output(pid("stat-10-0"), "children"),
        Output(pid("stat-failed"), "children"),
        Output(pid("stat-below-5"), "children"),
        Output(pid("stat-zero"), "children"),
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
@export_performance
def update_province_dashboard(
    n_clicks,
    subject,
    year,
    province,
    options,
):
    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not n_clicks:
        raise PreventUpdate

    if any(
        value is None
        for value in (subject, year, province)
    ):
        raise PreventUpdate

    options = options or []

    include_zero = "include_zero" in options
    include_failed = "include_failed" in options

    # ---------------------------------------------------------
    # CALCULATION
    # ---------------------------------------------------------

    result = calculate_province_analysis(
        year=year,
        subject=subject,
        province=province,
        include_zero=include_zero,
        include_failed=include_failed,
    )

    statistics = result["statistics"]

    # ---------------------------------------------------------
    # FORMAT HELPERS
    # ---------------------------------------------------------

    def fmt(value, spec=".2f"):
        return format(value, spec) if value is not None else "--"

    def fmt_int(value):
        return fmt(value, ",")

    # ---------------------------------------------------------
    # RANK
    # ---------------------------------------------------------

    rank = result["rank"]
    total_provinces = result["total_provinces"]

    rank_text = (
        f"#{rank} / {total_provinces}"
        if rank is not None
        else "--"
    )

    # ---------------------------------------------------------
    # BASIC STATISTICS
    # ---------------------------------------------------------

    count_text = fmt_int(statistics["count"])
    mean_text = fmt(statistics["mean"])
    median_text = fmt(statistics["median"])
    std_text = fmt(statistics["std"])
    skew_text = fmt(statistics["skew"])

    # ---------------------------------------------------------
    # QUARTILES
    # ---------------------------------------------------------

    q1 = statistics["q1"]
    q3 = statistics["q3"]

    quartiles_text = (
        f"{q1:.2f} – {q3:.2f}"
        if q1 is not None and q3 is not None
        else "--"
    )

    # ---------------------------------------------------------
    # HIGH SCORES
    # ---------------------------------------------------------

    ge_9_text = fmt_int(statistics["ge_9"])
    score_9_0_text = fmt_int(statistics["score_9_0"])
    score_9_25_text = fmt_int(statistics["score_9_25"])
    score_9_5_text = fmt_int(statistics["score_9_5"])
    score_9_75_text = fmt_int(statistics["score_9_75"])
    score_10_0_text = fmt_int(statistics["score_10_0"])

    # ---------------------------------------------------------
    # LOW / RISK SCORES
    # ---------------------------------------------------------

    failed_text = fmt_int(statistics["score_failed"])
    below_5_text = fmt_int(statistics["score_below_5"])
    zero_text = fmt_int(statistics["score_zero"])

    # ---------------------------------------------------------
    # MEAN STYLE
    # ---------------------------------------------------------

    mean = statistics["mean"]

    if mean is None:
        mean_class = "h4 fw-bold text-muted mb-0 mt-1"
    elif mean >= 6:
        mean_class = "h4 fw-bold text-success mb-0 mt-1"
    elif mean >= 5:
        mean_class = "h4 fw-bold text-warning mb-0 mt-1"
    else:
        mean_class = "h4 fw-bold text-danger mb-0 mt-1"

    # ---------------------------------------------------------
    # HISTOGRAM
    # ---------------------------------------------------------

    figure = build_histogram_figure(
        result["histogram"],
        subject,
    )

    # ---------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------

    return (
        rank_text,
        mean_text,
        mean_class,
        count_text,
        mean_text,
        median_text,
        quartiles_text,
        std_text,
        skew_text,
        ge_9_text,
        score_9_0_text,
        score_9_25_text,
        score_9_5_text,
        score_9_75_text,
        score_10_0_text,
        failed_text,
        below_5_text,
        zero_text,
        figure,
        "",
    )