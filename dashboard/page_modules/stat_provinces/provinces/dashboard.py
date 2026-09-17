from dash import html, dcc
import dash_bootstrap_components as dbc

from .list_of_id import pid

from utils.graph import create_empty_figure





# =========================================================
# TẦNG 1: THÔNG TIN TỔNG QUAN (KPI VĨ MÔ)[cite: 5]
# =========================================================
tier_1_layout = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div("TOP TOÀN QUỐC", className="text-muted small fw-bold text-uppercase"),
                        html.Div(id=pid("province-rank"), className="h4 fw-bold text-primary mb-0 mt-1"),
                        html.Div("Dựa trên điểm trung bình", className="text-muted small"),
                    ]
                ),
                className="shadow-sm border-0 border-start border-primary border-4 h-100",
            ),
            width=6,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div("ĐIỂM TRUNG BÌNH", className="text-muted small fw-bold text-uppercase"),
                        html.Div(id=pid("province-mean"), className="h4 fw-bold text-success mb-0 mt-1"),
                        html.Div("Điểm trung bình toàn tỉnh", className="text-muted small"),
                    ]
                ),
                className="shadow-sm border-0 border-start border-success border-4 h-100",
            ),
            width=6,
        ),
    ],
    className="g-3 mb-4",
)





# =========================================================
# TẦNG 2: PHÂN TÍCH THEO NHÓM 1 & NHÓM 2
# =========================================================
tier_2_layout = dbc.Row(
    [
        # NHÓM 1: Số lượng bài >= 9 & Thống kê các bài điểm thấp
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        "📊 Nhóm 1: Tổng quan cực trị (Điểm cao ≥ 9 và Điểm thấp)", 
                        className="fw-bold bg-light text-dark py-2"
                    ),
                    dbc.CardBody(
                        [
                            # Số lượng bài >= 9
                            html.Div(
                                [
                                    html.Span("Tổng số bài thi đạt ≥ 9.0:", className="text-muted fw-semibold"),
                                    html.Strong(id=pid("stat-ge-9"), children="--", className="text-primary"),
                                ],
                                className="d-flex justify-content-between py-2 border-bottom",
                            ),
                            
                            # Tiêu đề con cho phần điểm thấp
                            html.Div("Thống kê bài điểm thấp / Rủi ro:", className="text-muted small fw-bold text-uppercase mt-2 mb-1"),
                            
                            html.Div(
                                [
                                    html.Span("• Điểm liệt (≤ 1.0):", className="text-muted"),
                                    html.Strong(id=pid("stat-failed"), children="--", className="text-danger"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("• Dưới trung bình (< 5.0):", className="text-muted"),
                                    html.Strong(id=pid("stat-below-5"), children="--", className="text-warning text-dark"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("• Điểm 0 tuyệt đối:", className="text-muted"),
                                    html.Strong(id=pid("stat-zero"), children="--", className="text-secondary"),
                                ],
                                className="d-flex justify-content-between py-1",
                            ),
                        ],
                        className="py-2",
                    ),
                ],
                className="shadow-sm border-0 h-100",
            ),
            lg=6,
            md=12,
            className="mb-3 mb-lg-0",
        ),

        # NHÓM 2: Đếm số lượng bài ở các mức điểm khác nhau (Mũi nhọn chi tiết)
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        "🎯 Nhóm 2: Chi tiết đếm số lượng theo mốc điểm cao", 
                        className="fw-bold bg-light text-primary py-2"
                    ),
                    dbc.CardBody(
                        [
                            html.Div("Số lượng bài thi tại từng mốc điểm mũi nhọn:", className="text-muted small mb-2"),
                            html.Div(
                                [
                                    html.Span("Mốc 9.0:", className="text-muted"),
                                    html.Strong(id=pid("stat-9-0"), children="--"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("Mốc 9.25:", className="text-muted"),
                                    html.Strong(id=pid("stat-9-25"), children="--"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("Mốc 9.5:", className="text-muted"),
                                    html.Strong(id=pid("stat-9-5"), children="--"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("Mốc 9.75:", className="text-muted"),
                                    html.Strong(id=pid("stat-9-75"), children="--"),
                                ],
                                className="d-flex justify-content-between py-1 border-bottom",
                            ),
                            html.Div(
                                [
                                    html.Span("Mốc 10.0 🔥:", className="text-success fw-semibold"),
                                    html.Strong(id=pid("stat-10-0"), children="--", className="text-success"),
                                ],
                                className="d-flex justify-content-between py-2 mt-1",
                            ),
                        ],
                        className="py-2",
                    ),
                ],
                className="shadow-sm border-0 h-100",
            ),
            lg=6,
            md=12,
        ),
    ],
    className="g-3 mb-4",
)





# =========================================================
# TẦNG 3: DASHBOARD TRỰC QUAN & THỐNG KÊ CƠ BẢN[cite: 5]
# =========================================================
tier_3_stats = dbc.Card(
    [
        dbc.CardHeader("Thống kê tổng quát phổ điểm", className="fw-bold bg-white py-3"),
        dbc.CardBody(
            [
                html.Div([html.Span("Tổng số thí sinh"), html.Strong(id=pid("stat-count"), children="--")], className="d-flex justify-content-between py-2 border-bottom"),
                html.Div([html.Span("Trung bình"), html.Strong(id=pid("stat-mean"), children="--")], className="d-flex justify-content-between py-2 border-bottom"),
                html.Div([html.Span("Trung vị"), html.Strong(id=pid("stat-median"), children="--")], className="d-flex justify-content-between py-2 border-bottom"),
                html.Div([html.Span("Q1 - Q3"), html.Strong(id=pid("stat-quartiles"), children="--")], className="d-flex justify-content-between py-2 border-bottom"),
                html.Div([html.Span("Độ lệch chuẩn"), html.Strong(id=pid("stat-std"), children="--")], className="d-flex justify-content-between py-2 border-bottom"),
                html.Div([html.Span("Độ xiên"), html.Strong(id=pid("stat-skew"), children="--")], className="d-flex justify-content-between py-2"),
            ]
        ),


        dbc.Tooltip(
            [
                html.B("Độ xiên (Skewness)"),
                html.Br(),
                "• Gần bằng 0: Phân phối đối xứng",
                html.Br(),
                "• Giá trị dương (> 0): Lệch phải",
                html.Br(),
                "• Giá trị âm (< 0): Lệch trái",
            ], 
            target = pid("stat-skew"), 
            placement = "top"
        )
    ],

    className="shadow-sm border-0 h-100",
)





tier_3_histogram = dbc.Card(
    [
        dbc.CardHeader("Biểu đồ phân phối điểm", className="fw-bold bg-white py-3"),
        dbc.CardBody(
            dcc.Graph(
                id=pid("province-histogram"),
                figure=create_empty_figure(""),
                config={"displayModeBar": False},
                style={"height": "380px"},
            ),
            className="p-2",
        ),
    ],
    className="shadow-sm border-0 h-100",
)





tier_3_layout = dbc.Row(
    [
        dbc.Col(tier_3_histogram, lg=8, md=12, className="mb-3 mb-lg-0"),
        dbc.Col(tier_3_stats, lg=4, md=12),
    ],
    className="g-3 align-items-stretch",
)





# =========================================================
# TỔNG HỢP DASHBOARD LAYOUT[cite: 5]
# =========================================================
dashboard_layout = html.Div(
    [
        dcc.Loading(
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Kết quả phân tích phổ điểm", className="fw-bold text-dark mb-1"),
                                html.P("Hệ thống thông tin chi tiết phân cấp theo cấp độ dữ liệu.", className="text-muted small mb-4"),
                            ]
                        ),
                        tier_1_layout,  # Tầng 1: Tổng quan vĩ mô[cite: 5]
                        tier_2_layout,  # Tầng 2: Mũi nhọn & Rủi ro[cite: 5]
                        tier_3_layout,  # Tầng 3: Biểu đồ & Thống kê cơ bản[cite: 5]
                    ],
                    id=pid("dashboard-result"),
                    className="opacity-50",
                )
            ],
            type="circle",
            overlay_style={"visibility": "visible", "filter": "blur(3px)"},
            custom_spinner=html.Div(
                [
                    dbc.Spinner(color="success", type="border", size="lg"),
                    html.H5("Đang phân tích...", className="mt-3 text-secondary"),
                ],
                className="d-flex flex-column align-items-center justify-content-center vh-50",
            ),
        )
    ],
    className="container-fluid px-0",
)