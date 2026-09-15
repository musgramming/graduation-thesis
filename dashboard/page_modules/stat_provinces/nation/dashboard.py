from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from .list_of_id import pid


# ============================================================
# KPI
# ============================================================

kpi_layout = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Div(
                                "ĐIỂM TRUNG BÌNH",
                                className="text-muted small fw-semibold",
                            ),

                            html.Div(
                                id=pid("nation-mean"),
                                className="display-6 fw-bold",
                            ),

                            html.Div(
                                "Điểm trung bình toàn quốc",
                                className="text-muted small",
                            ),
                        ]
                    )
                ],
                className="h-100 shadow-sm",
            ),
            xs=12,
        ),
    ],
    className="g-3",
)


# ============================================================
# Statistics
# ============================================================

statistics_layout = dbc.Card(
    [
        dbc.CardHeader(
            "Các giá trị thống kê",
            className="fw-semibold",
        ),

        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span("Trung bình"),
                        html.Strong(
                            id=pid("nation-stat-mean"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Trung vị"),
                        html.Strong(
                            id=pid("nation-stat-median"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Q1 - Q3"),
                        html.Strong(
                            id=pid("nation-stat-quartiles"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Độ lệch chuẩn"),
                        html.Strong(
                            id=pid("nation-stat-std"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Độ xiên"),
                        html.Strong(
                            id=pid("nation-stat-skew"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2",
                ),
            ]
        ),
    ],
    className="h-100 shadow-sm",
)


# ============================================================
# Histogram
# ============================================================

histogram_layout = dbc.Card(
    [
        dbc.CardHeader(
            "Phân phối điểm",
            className="fw-semibold",
        ),

        dbc.CardBody(
            dcc.Graph(
                id=pid("nation-histogram"),
                figure={},
                config={
                    "displayModeBar": False,
                },
            )
        ),
    ],
    className="h-100 shadow-sm",
)


# ============================================================
# Bản đồ
# ============================================================

map_layout = dbc.Card(
    [
        dbc.CardHeader(
            "Phân bố điểm trung bình theo tỉnh thành",
            className="fw-semibold",
        ),

        dbc.CardBody(
            dcc.Graph(
                id=pid("nation-map"),
                figure={},
                config={
                    "displayModeBar": False,
                },
                style={
                    "height": "600px",
                },
            )
        ),
    ],
    className="h-100 shadow-sm",
)


# ============================================================
# Bảng tỉnh thành
# ============================================================

province_table_layout = dbc.Card(
    [
        dbc.CardHeader(
            "Thống kê các tỉnh thành",
            className="fw-semibold",
        ),

        dbc.CardBody(
            dash_table.DataTable(
                id=pid("nation-province-table"),
                columns=[
                    {
                        "name": "Xếp hạng",
                        "id": "Xếp hạng",
                    },
                    {
                        "name": "Tỉnh thành",
                        "id": "Tỉnh thành",
                    },
                    {
                        "name": "Điểm trung bình",
                        "id": "Điểm trung bình",
                    },
                    {
                        "name": "Trung vị",
                        "id": "Trung vị",
                    },
                ],
                data=[],
                sort_action="native",
                page_action="native",
                page_size=34,
                style_table={
                    "overflowX": "auto",
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "8px",
                },
                style_header={
                    "fontWeight": "600",
                },
            )
        ),
    ],
    className="h-100 shadow-sm",
)


# ============================================================
# Dashboard
# ============================================================

dashboard_layout = html.Div(
    [
        dcc.Loading(
            children=[
                html.Div(
                    [
                        kpi_layout,

                        html.Div(
                            className="my-4",
                        ),

                        # Histogram + statistics
                        dbc.Row(
                            [
                                dbc.Col(
                                    histogram_layout,
                                    xs=12,
                                    lg=8,
                                ),

                                dbc.Col(
                                    statistics_layout,
                                    xs=12,
                                    lg=4,
                                ),
                            ],
                            className="g-3",
                        ),

                        html.Div(
                            className="my-4",
                        ),

                        # Map + province table
                        dbc.Row(
                            [
                                dbc.Col(
                                    map_layout,
                                    xs=12,
                                    lg=6,
                                ),

                                dbc.Col(
                                    province_table_layout,
                                    xs=12,
                                    lg=6,
                                ),
                            ],
                            className="g-3",
                        ),
                    ],
                    id=pid("nation-dashboard-result"),
                    className="opacity-50",
                ),
            ],

            type="circle",

            overlay_style={
                "visibility": "visible",
                "filter": "blur(3px)",
            },

            custom_spinner=html.Div(
                [
                    dbc.Spinner(
                        color="success",
                        type="border",
                        size="lg",
                    ),

                    html.H5(
                        "Đang phân tích",
                        className="mt-3",
                    ),
                ],
                className="d-flex flex-column align-items-center",
            ),
        ),
    ]
)
