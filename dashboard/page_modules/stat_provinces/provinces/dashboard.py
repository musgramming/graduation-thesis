from dash import html, dcc
import dash_bootstrap_components as dbc

from .list_of_id import pid





# =========================================================
#                         KPI
# =========================================================

kpi_layout = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Div(
                                "TOP TOÀN QUỐC",
                                className="text-muted small fw-semibold",
                            ),
                            html.Div(
                                id=pid("province-rank"),
                                className="display-6 fw-bold",
                            ),
                            html.Div(
                                "Dựa trên điểm trung bình",
                                className="text-muted small",
                            ),
                        ]
                    )
                ],
                className="h-100 shadow-sm",
            ),
            width=6,
        ),

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
                                id=pid("province-mean"),
                                className="display-6 fw-bold",
                            ),
                            html.Div(
                                "Điểm trung bình",
                                className="text-muted small",
                            ),
                        ]
                    )
                ],
                className="h-100 shadow-sm",
            ),
            width=6,
        ),
    ],
    className="g-3",
)


# =========================================================
#                    STATISTICS TABLE
# =========================================================

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
                            id=pid("stat-mean"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Trung vị"),
                        html.Strong(
                            id=pid("stat-median"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Q1 - Q3"),
                        html.Strong(
                            id=pid("stat-quartiles"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),

                html.Div(
                    [
                        html.Span("Độ lệch chuẩn"),
                        html.Strong(
                            id=pid("stat-std"),
                            children="--",
                        ),
                    ],
                    className="d-flex justify-content-between py-2 border-bottom",
                ),
            
                html.Div(
                    [
                        html.Span("Độ xiên"),
                        html.Strong(
                            id=pid("stat-skew"),
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


# =========================================================
#                         HISTOGRAM
# =========================================================

histogram_layout = dbc.Card(
    [
        dbc.CardHeader(
            "Phân phối điểm",
            className="fw-semibold",
        ),

        dbc.CardBody(
            dcc.Graph(
                id=pid("province-histogram"),
                figure={},
                config={
                    "displayModeBar": False,
                },
            )
        ),
    ],
    className="h-100 shadow-sm",
)


# =========================================================
#                       DASHBOARD
# =========================================================

dashboard_layout = html.Div(
    [
        dcc.Loading(
            children = [
                html.Div(
                    [
                        kpi_layout,

                        html.Div(className="my-4"),

                        dbc.Row(
                            [
                                dbc.Col(
                                    histogram_layout,
                                    width=8,
                                ),

                                dbc.Col(
                                    statistics_layout,
                                    width=4,
                                ),
                            ],
                            className="g-3",
                        ),
                    ],
                    id=pid("dashboard-result"),
                    className="opacity-50",
                )
            ], 
            type = "circle", 
            overlay_style = {
                "visibility" : "visible", 
                "filter" : "blur(3px)"
            }, 
            custom_spinner =html.Div(
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
            )
        )
    ]
)
