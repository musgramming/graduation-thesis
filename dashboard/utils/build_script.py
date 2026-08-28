from typing import Literal

from dash import html, dcc, dash_table
import plotly.graph_objects as go
import plotly.express as px
import polars as pl
import dash_bootstrap_components as dbc

from data import BANG_DIEM_TO_HOP
from .graph import build_strict_graph





def filter_raw_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Trích xuất dữ liệu điểm thô dựa trên các tiêu chí lọc.

    Phương pháp này giữ nguyên giá trị thực tế của kỳ thi, phục vụ cho việc
    tra cứu vị thế trực tiếp mà không qua biến đổi thống kê.

    Args:
        year (int): Năm dữ liệu cần truy vấn.
        floor_score (float): Ngưỡng điểm sàn thiết lập bởi người dùng.
        combs (list[str]): Danh sách mã các tổ hợp cần lọc.

    Returns:
        pl.LazyFrame: Một bản kế hoạch truy vấn Polars đã được lọc theo điều kiện.
    """
    return BANG_DIEM_TO_HOP[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) &
        (pl.col("Tổng điểm") >= floor_score) &
        (pl.col("Hợp lệ") == True)
    ).with_columns(
        pl.col("Tổng điểm").alias("Điểm quy đổi")
    )





def filter_z_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Chuẩn hóa dữ liệu bằng phương pháp Z-Score (Standardization).

    Mục đích: Đưa các tổ hợp môn khác nhau về cùng một phân phối chuẩn (Mean=0, Std=1),
    sau đó tái quy đổi về thang điểm 30. Giúp so sánh công bằng giữa các tổ hợp
    có độ khó/phổ điểm khác nhau.

    Quy trình:
        1. Tính Mean và Standard Deviation cho từng tổ hợp.
        2. Tính toán Z-score: z = (x - mean) / std.
        3. Feature Scaling: Ép dãn giá trị Z về thang [0, 30] dựa trên Min/Max Z.

    Args:
        year (int): Năm dữ liệu.
        floor_score (float): Điểm sàn quy đổi.
        combs (list[str]): Danh sách tổ hợp.

    Returns:
        pl.LazyFrame: Dữ liệu đã chuẩn hóa theo phân phối xác suất.
    """
    df = BANG_DIEM_TO_HOP[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) & 
        (pl.col("Hợp lệ") == True)
    )
    
    # Bước 1: Tính Mean và Std theo từng tổ hợp
    stats = df.group_by("Tổ hợp").agg([
        pl.col("Tổng điểm").mean().alias("mean"),
        pl.col("Tổng điểm").std().alias("std")
    ])
    
    # Bước 2: Tính Z-value
    df_z = df.join(stats, on="Tổ hợp").with_columns(
        pl.when(pl.col("std") > 0)
        .then(
            (pl.col("Tổng điểm") - pl.col("mean")) / 
            pl.col("std")
        )
        .otherwise(0.0)
        .alias("z_val")
    )

    # Bước 3: Ép về thang [0, 30] dựa trên Min/Max thực tế của từng tổ hợp
    # Điều này đảm bảo 'Top 1' của mọi tổ hợp đều đạt 30 điểm trên Dashboard
    min_max_z = df_z.group_by("Tổ hợp").agg([
        pl.col("z_val").min().alias("z_min"),
        pl.col("z_val").max().alias("z_max")
    ])
    
    return (
        df_z.join(min_max_z, on="Tổ hợp")
        .with_columns(
            pl.when(pl.col("z_max") > pl.col("z_min"))
            .then(
                (pl.col("z_val") - pl.col("z_min")) / 
                (pl.col("z_max") - pl.col("z_min")) * 30
            )
            .otherwise(15.0)
            .alias("Điểm quy đổi")
        )
        .filter(pl.col("Điểm quy đổi") >= floor_score)
        .drop(["mean", "std", "z_val", "z_min", "z_max"])
    )





def filter_robust_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Chuẩn hóa dữ liệu bằng phương pháp Robust Scaling.

    Mục đích: Loại bỏ ảnh hưởng của các giá trị ngoại lai (outliers) và các phổ điểm
    bị lệch (skewed distribution). Sử dụng Trung vị (Median) và Khoảng biến thiên
    tứ phân vị (IQR) thay vì Mean/Std để đảm bảo tính ổn định.

    Công thức quy đổi: r = (x - Median) / (Q3 - Q1).

    Args:
        year (int): Năm dữ liệu.
        floor_score (float): Điểm sàn quy đổi.
        combs (list[str]): Danh sách tổ hợp.

    Returns:
        pl.LazyFrame: Dữ liệu đã được loại bỏ nhiễu từ các điểm số cực đoan.
    """
    df = BANG_DIEM_TO_HOP[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) & 
        (pl.col("Hợp lệ") == True)
    )
    
    # Bước 1: Tính Median, Q1, Q3
    stats = df.group_by("Tổ hợp").agg([
        pl.col("Tổng điểm").median().alias("median"),
        pl.col("Tổng điểm").quantile(0.25).alias("q1"),
        pl.col("Tổng điểm").quantile(0.75).alias("q3")
    ])
    
    # Bước 2: Tính Robust value (r_val)
    df_robust = df.join(stats, on="Tổ hợp").with_columns(
        pl.when(pl.col("q3") > pl.col("q1"))
        .then((pl.col("Tổng điểm") - pl.col("median")) / (pl.col("q3") - pl.col("q1")))
        .otherwise(0.0)
        .alias("r_val")
    )
    
    # Bước 3: Tìm r_min, r_max để ép về thang 30
    # Điều này giúp Dashboard giữ được sự tương quan khi so sánh các khối lệch phổ điểm
    r_limit = df_robust.group_by("Tổ hợp").agg([
        pl.col("r_val").min().alias("r_min"),
        pl.col("r_val").max().alias("r_max")
    ])
    
    return (
        df_robust.join(r_limit, on="Tổ hợp")
        .with_columns(
            pl.when(pl.col("r_max") > pl.col("r_min"))
            .then(
                (pl.col("r_val") - pl.col("r_min")) / 
                (pl.col("r_max") - pl.col("r_min")) * 30
            ).otherwise(15.0)
            .alias("Điểm quy đổi")
        )
        .filter(pl.col("Điểm quy đổi") >= floor_score)
        .drop(["median", "q1", "q3", "r_val", "r_min", "r_max"])
    )




def transform_scores(year: int, combs: list[str], mode: str) -> pl.LazyFrame:
    """Hàm điều phối (Dispatcher) cho các phương thức quy đổi điểm số.

    Sử dụng các hằng số ANCHOR (15.0) và SCALE_FACTOR (5.0) để duy trì đặc tính
    phân phối của dữ liệu trong khi vẫn giữ kết quả nằm trong khung điểm 0-30
    quen thuộc với người dùng.

    Args:
        year (int): Năm khảo thí.
        combs (list[str]): Danh sách tổ hợp môn.
        mode (str): Chế độ quy đổi ('raw-score', 'z-score', 'robust').

    Returns:
        pl.LazyFrame: LazyFrame chứa cột 'Điểm quy đổi' đã được xử lý theo mode.
        
    Note:
        Sử dụng phương pháp .clip(0, 30) để đảm bảo tính an toàn dữ liệu đầu ra.
    """
    lf = BANG_DIEM_TO_HOP[year].filter(pl.col("Tổ hợp").is_in(combs))
    
    # Hằng số quy đổi để giữ thang 0-30 nhưng không làm mất đặc tính phân phối
    # Giả sử: Mean/Median nằm ở 15 điểm, mỗi 1 Std/IQR dãn ra 5 điểm
    ANCHOR = 15.0
    SCALE_FACTOR = 5.0 

    if mode == "raw-score":
        return lf.with_columns(pl.col("Tổng điểm").alias("Điểm quy đổi"))

    elif mode == "z-score":
        stats = lf.group_by("Tổ hợp").agg([
            pl.col("Tổng điểm").mean().alias("mean"),
            pl.col("Tổng điểm").std().alias("std")
        ])
        return (
            lf.join(stats, on="Tổ hợp").with_columns(
                (ANCHOR + (
                    (pl.col("Tổng điểm") - pl.col("mean")) / 
                    pl.col("std")
                ) * SCALE_FACTOR)
                .clip(0, 30) # Đảm bảo không vượt quá thang điểm
                .round(3)
                .alias("Điểm quy đổi")
            )
        )

    elif mode == "robust":
        stats = lf.group_by("Tổ hợp").agg([
            pl.col("Tổng điểm").median().alias("median"),
            pl.col("Tổng điểm").quantile(0.25).alias("q1"),
            pl.col("Tổng điểm").quantile(0.75).alias("q3")
        ])
        return (
            lf.join(stats, on="Tổ hợp")
            .with_columns(
                pl.when(pl.col("q3") > pl.col("q1"))
                .then(
                    ANCHOR + (
                        (pl.col("Tổng điểm") - pl.col("median")) / 
                        (pl.col("q3") - pl.col("q1"))
                    ) * SCALE_FACTOR
                )
                .otherwise(ANCHOR)
                .clip(0, 30)
                .round(3)
                .alias("Điểm quy đổi")
            )
        )

    return lf





def display_graph_and_table(
    year: int, 
    self_score : float, 
    floor_score : float, 
    combs : list[str], 
    mode : Literal["raw-score", "z-score", "robust"]
) -> html.Div:
    """
    Xây dựng dashboard phân tích vị thế thí sinh.

    Dashboard gồm 4 tầng:

    1. Context
       - Kỳ thi
       - Tổ hợp
       - Điểm cá nhân
       - Điểm sàn
       - Phương pháp chuẩn hóa

    2. Position
       - Điểm cá nhân
       - Vị thế tổng quát
       - Vị thế trong nhóm đạt điểm sàn

    3. Distribution
       - Phổ điểm toàn cảnh
       - Vùng cạnh tranh quanh điểm cá nhân
       - Vùng điểm sàn

    4. Reference
       - Top 20 thí sinh
    """

    # ================================================================
    # 1. PREPARATION
    # ================================================================

    if not combs:
        return dbc.Alert(
            "Vui lòng chọn ít nhất một tổ hợp môn.",
            color="warning",
            className="mb-0",
        )

    lf_transformed = transform_scores(
        year,
        combs,
        mode,
    )

    # Lấy điểm quy đổi cao nhất của mỗi thí sinh
    lf_final = (
        lf_transformed
        .group_by("SOBAODANH")
        .agg([
            pl.col("Điểm quy đổi").max().alias("Điểm quy đổi"),
            pl.col("Tổ hợp")
            .get(pl.col("Điểm quy đổi").arg_max())
            .alias("Tổ hợp_chọn"),
        ])
    )

    df_result = lf_final.collect()

    if df_result.is_empty():
        return dbc.Alert(
            "Không tìm thấy dữ liệu phù hợp với bộ lọc hiện tại.",
            color="warning",
            className="mb-0",
        )



    # ================================================================
    # 2. POSITION METRICS
    # ================================================================

    total_count = df_result.height

    # ------------------------------------------------
    # Vị thế tổng quát
    # ------------------------------------------------

    overall_rank = (
        df_result
        .filter(pl.col("Điểm quy đổi") > self_score)
        .height
        + 1
    )

    overall_pr = (
        (1 - overall_rank / total_count) * 100
        if total_count > 0
        else 0
    )

    # ------------------------------------------------
    # Vị thế trong nhóm đạt điểm sàn
    # ------------------------------------------------

    df_on_floor = df_result.filter(
        pl.col("Điểm quy đổi") >= floor_score
    )

    total_on_floor = df_on_floor.height

    if total_on_floor > 0 and self_score >= floor_score:

        floor_rank = (
            df_on_floor
            .filter(pl.col("Điểm quy đổi") > self_score)
            .height
            + 1
        )

        floor_pr = (
            (1 - floor_rank / total_on_floor) * 100
        )

    else:
        floor_rank = None
        floor_pr = None



    # ================================================================
    # 3. LOCAL DISTRIBUTIONS
    # ================================================================

    df_comp = df_result.filter(
        (pl.col("Điểm quy đổi") >= self_score - 1)
        & (pl.col("Điểm quy đổi") <= self_score + 1)
    )

    df_safety = df_result.filter(
        (pl.col("Điểm quy đổi") >= floor_score - 1)
        & (pl.col("Điểm quy đổi") <= floor_score + 1)
    )

    # ------------------------------------------------
    # Top 20
    # ------------------------------------------------

    df_top20 = (
        df_result
        .sort(
            "Điểm quy đổi",
            descending=True,
        )
        .head(20)
        .rename({
            "Điểm quy đổi": "Điểm",
            "Tổ hợp_chọn": "Tổ hợp",
        })
    )



    # ================================================================
    # 4. FIGURE — OVERALL DISTRIBUTION
    # ================================================================

    fig_overall = px.histogram(
        df_result.to_pandas(),
        x="Điểm quy đổi",
        title=None,
        hover_data={
            "Điểm quy đổi": False,
        },
    )

    fig_overall.update_traces(
        xbins=dict(
            start=0,
            end=30.2,
            size=0.25,
        ),
        hovertemplate=(
            "<b>Mức điểm: %{x}</b><br>"
            "Số lượng: %{y} thí sinh"
            "<extra></extra>"
        ),
    )

    fig_overall.add_vline(
        x=floor_score,
        line_dash="dash",
        annotation_text="Điểm sàn",
        annotation_position="top left",
    )

    fig_overall.add_vline(
        x=self_score,
        line_dash="dash",
        annotation_text="Điểm của bạn",
        annotation_position="top right",
    )

    fig_overall.update_xaxes(
        range=[0, 30.5],
        constrain="domain",
        nticks=10,
        title="Điểm",
    )

    fig_overall.update_yaxes(
        title="Số thí sinh",
    )

    build_strict_graph(fig_overall)



    # ================================================================
    # 5. FIGURE — COMPETITION ZOOM
    # ================================================================

    if df_comp.is_empty():

        fig_comp = go.Figure()

        fig_comp.add_annotation(
            text="Không có thí sinh trong vùng điểm này.",
            showarrow=False,
        )

    else:

        fig_comp = px.histogram(
            df_comp.to_pandas(),
            x="Điểm quy đổi",
            title=None,
        )

        fig_comp.update_traces(
            xbins=dict(
                size=0.2,
            ),
            hovertemplate=(
                "<b>Mức điểm: %{x}</b><br>"
                "Số lượng: %{y} thí sinh"
                "<extra></extra>"
            ),
        )

        fig_comp.add_vline(
            x=self_score,
            line_dash="dot",
            annotation_text="Bạn",
            annotation_position="top",
        )

        fig_comp.update_xaxes(
            title="Điểm quy đổi",
        )

        fig_comp.update_yaxes(
            title="Số thí sinh",
        )

    build_strict_graph(fig_comp)



    # ================================================================
    # 6. FIGURE — FLOOR ZOOM
    # ================================================================

    if df_safety.is_empty():

        fig_safety = go.Figure()

        fig_safety.add_annotation(
            text="Không có thí sinh trong vùng điểm sàn.",
            showarrow=False,
        )

    else:

        fig_safety = px.histogram(
            df_safety.to_pandas(),
            x="Điểm quy đổi",
            title=None,
        )

        fig_safety.update_traces(
            xbins=dict(
                size=0.2,
            ),
            hovertemplate=(
                "<b>Mức điểm: %{x}</b><br>"
                "Số lượng: %{y} thí sinh"
                "<extra></extra>"
            ),
        )

        fig_safety.add_vline(
            x=floor_score,
            line_dash="dot",
            annotation_text="Điểm sàn",
            annotation_position="top",
        )

        fig_safety.update_xaxes(
            title="Điểm quy đổi",
        )

        fig_safety.update_yaxes(
            title="Số thí sinh",
        )

    build_strict_graph(fig_safety)



    # ================================================================
    # 7. CONTEXT HEADER
    # ================================================================

    comb_text = ", ".join(combs)

    header = dbc.Card(
        dbc.CardBody([
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                "Phân tích vị thế",
                                className="fw-bold mb-1",
                            ),
                            html.P(
                                f"Kỳ thi tốt nghiệp THPT năm {year}",
                                className="text-muted mb-0",
                            ),
                        ],
                    ),

                    dbc.Badge(
                        mode.upper(),
                        color="secondary",
                        className="px-3 py-2",
                    ),
                ],
                className=(
                    "d-flex justify-content-between "
                    "align-items-start"
                ),
            ),

            html.Hr(),

            dbc.Row([
                dbc.Col([
                    html.Small(
                        "TỔ HỢP PHÂN TÍCH",
                        className="text-muted fw-bold",
                    ),
                    html.Div(
                        comb_text,
                        className="fw-semibold",
                    ),
                ], xs=12, md=4),

                dbc.Col([
                    html.Small(
                        "ĐIỂM CỦA BẠN",
                        className="text-muted fw-bold",
                    ),
                    html.Div(
                        f"{self_score:.2f}",
                        className="fw-bold",
                    ),
                ], xs=6, md=4),

                dbc.Col([
                    html.Small(
                        "ĐIỂM SÀN",
                        className="text-muted fw-bold",
                    ),
                    html.Div(
                        f"{floor_score:.2f}",
                        className="fw-bold",
                    ),
                ], xs=6, md=4),
            ]),
        ]),
        className="shadow-sm border-0 mb-4",
    )



    # ================================================================
    # 8. KPI CARDS
    # ================================================================

    overall_rank_text = f"#{overall_rank:,}"

    if floor_rank is None:
        floor_rank_text = "—"
        floor_pr_text = "Không áp dụng"
    else:
        floor_rank_text = f"#{floor_rank:,}"
        floor_pr_text = f"PR {floor_pr:.2f}%"

    kpi_cards = dbc.Row([

        # ------------------------------------------------------------
        # Điểm
        # ------------------------------------------------------------

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-bullseye me-2"
                            ),
                            "ĐIỂM CỦA BẠN",
                        ],
                        className=(
                            "text-muted small fw-bold mb-2"
                        ),
                    ),

                    html.Div(
                        f"{self_score:.2f}",
                        className=(
                            "display-6 fw-bold text-center"
                        ),
                    ),

                    html.Div(
                        "điểm",
                        className=(
                            "text-muted text-center small"
                        ),
                    ),
                ])
            ], className="shadow-sm border-0 h-100"),
            xs=12,
            md=4,
            className="mb-3",
        ),

        # ------------------------------------------------------------
        # Overall position
        # ------------------------------------------------------------

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-bar-chart-line me-2"
                            ),
                            "VỊ THẾ TỔNG QUÁT",
                        ],
                        className=(
                            "text-muted small fw-bold mb-2"
                        ),
                    ),

                    html.Div(
                        overall_rank_text,
                        className=(
                            "display-6 fw-bold text-center"
                        ),
                    ),

                    html.Div(
                        f"PR {overall_pr:.2f}% "
                        f"· {total_count:,} thí sinh",
                        className=(
                            "text-muted text-center small"
                        ),
                    ),
                ])
            ], className="shadow-sm border-0 h-100"),
            xs=12,
            md=4,
            className="mb-3",
        ),

        # ------------------------------------------------------------
        # Floor position
        # ------------------------------------------------------------

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div(
                        [
                            html.I(
                                className="bi bi-shield-check me-2"
                            ),
                            "VỊ THẾ TRÊN SÀN",
                        ],
                        className=(
                            "text-muted small fw-bold mb-2"
                        ),
                    ),

                    html.Div(
                        floor_rank_text,
                        className=(
                            "display-6 fw-bold text-center"
                        ),
                    ),

                    html.Div(
                        floor_pr_text,
                        className=(
                            "text-muted text-center small"
                        ),
                    ),
                ])
            ], className="shadow-sm border-0 h-100"),
            xs=12,
            md=4,
            className="mb-3",
        ),

    ], className="mb-4")



    # ================================================================
    # 9. INSIGHT
    # ================================================================

    if self_score < floor_score:

        insight_text = (
            f"Điểm của bạn ({self_score:.2f}) đang thấp hơn "
            f"điểm sàn ({floor_score:.2f}). "
            "Vị thế trong nhóm đạt điểm sàn chưa được tính."
        )

        insight_color = "warning"

    else:

        insight_text = (
            f"Điểm của bạn ({self_score:.2f}) đang cao hơn "
            f"điểm sàn ({floor_score:.2f}). "
            f"Bạn đang ở khoảng PR {overall_pr:.2f}% "
            "trong phạm vi dữ liệu phân tích."
        )

        insight_color = "info"

    insight = dbc.Alert(
        [
            html.Div(
                [
                    html.I(
                        className="bi bi-lightbulb me-2"
                    ),
                    html.Strong("Nhận định"),
                ],
                className="mb-1",
            ),
            html.Div(insight_text),
        ],
        color=insight_color,
        className="mb-4",
    )



    # ================================================================
    # 10. OVERALL DISTRIBUTION
    # ================================================================

    overall_section = dbc.Card([
        dbc.CardBody([

            html.H5(
                [
                    html.I(
                        className="bi bi-bar-chart-line me-2"
                    ),
                    "Phổ điểm toàn cảnh",
                ],
                className="fw-bold mb-1",
            ),

            html.P(
                "Phân bố điểm của toàn bộ thí sinh trong "
                "phạm vi phân tích.",
                className="text-muted small mb-3",
            ),

            dcc.Graph(
                figure=fig_overall,
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "responsive": True,
                },
                style={
                    "height": "450px",
                },
            ),

        ])
    ], className="shadow-sm border-0 mb-4")



    # ================================================================
    # 11. LOCAL ANALYSIS
    # ================================================================

    competition_card = dbc.Card([
        dbc.CardBody([

            html.H5(
                [
                    html.I(
                        className="bi bi-search me-2"
                    ),
                    "Vùng cạnh tranh",
                ],
                className="fw-bold mb-1",
            ),

            html.P(
                "Phân bố thí sinh trong khoảng ±1 điểm "
                "quanh điểm của bạn.",
                className="text-muted small mb-3",
            ),

            dcc.Graph(
                figure=fig_comp,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
                style={
                    "height": "350px",
                },
            ),

        ])
    ], className="shadow-sm border-0 h-100")

    safety_card = dbc.Card([
        dbc.CardBody([

            html.H5(
                [
                    html.I(
                        className="bi bi-shield-check me-2"
                    ),
                    "Vùng điểm sàn",
                ],
                className="fw-bold mb-1",
            ),

            html.P(
                "Phân bố thí sinh trong khoảng ±1 điểm "
                "quanh điểm sàn.",
                className="text-muted small mb-3",
            ),

            dcc.Graph(
                figure=fig_safety,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
                style={
                    "height": "350px",
                },
            ),

        ])
    ], className="shadow-sm border-0 h-100")

    local_analysis = dbc.Row([

        dbc.Col(
            competition_card,
            xs=12,
            lg=6,
            className="mb-4",
        ),

        dbc.Col(
            safety_card,
            xs=12,
            lg=6,
            className="mb-4",
        ),

    ])



    # ================================================================
    # 12. TOP 20
    # ================================================================

    top20_table = dbc.Card([
        dbc.CardHeader(
            [
                html.I(
                    className="bi bi-trophy me-2"
                ),
                "Top 20 thí sinh",
            ],
            className="fw-bold",
        ),

        dbc.CardBody(
            dash_table.DataTable(
                data=df_top20.to_dicts(),
                columns=[
                    {
                        "name": column,
                        "id": column,
                    }
                    for column in df_top20.columns
                ],
                style_table={
                    "overflowX": "auto",
                },
                style_cell={
                    "minWidth": "70px",
                    "width": "100px",
                    "maxWidth": "160px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "fontSize": "12px",
                    "padding": "8px",
                    "textAlign": "center",
                },
                style_header={
                    "fontWeight": "bold",
                    "textAlign": "center",
                },
                page_action="none",
            ),
            className="p-2",
        ),
    ], className="shadow-sm border-0 mb-4")



    # ================================================================
    # 13. FINAL DASHBOARD
    # ================================================================

    return html.Div([
        header,
        kpi_cards,
        insight,
        overall_section,
        html.Div(
            [
                html.H4(
                    "Phân tích chi tiết",
                    className="fw-bold mb-3",
                ),
                local_analysis,
            ]
        ),

        html.Div(
            [
                html.H4(
                    "Dữ liệu tham chiếu",
                    className="fw-bold mb-3",
                ),
                top20_table,
            ]
        ),

    ])