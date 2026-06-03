from dash import html, register_page
import dash_bootstrap_components as dbc


register_page(
    __name__,
    path="/",
    redirect_from=["/main_page"],
    title="Hệ thống Phân tích Phổ điểm THPTQG 2025",
    description="Phân tích vị thế điểm số và dự báo tổ hợp",
)


layout = html.Div([

    # =====================================================
    # HERO SECTION
    # =====================================================

    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        html.I(
                                            className="bi bi-bar-chart-line-fill text-primary",
                                            style={"fontSize": "5rem"}
                                        ),
                                        className="mb-4"
                                    ),

                                    html.H1(
                                        "Hệ thống Phân tích Phổ điểm THPTQG 2025",
                                        className="fw-bold display-5 mb-3"
                                    ),

                                    html.P(
                                        [
                                            "Nền tảng hỗ trợ ",
                                            html.Strong("phân tích vị thế điểm số"),
                                            ", đánh giá khả năng cạnh tranh và mô phỏng ",
                                            html.Strong("các kịch bản xét tuyển đại học"),
                                            " dựa trên dữ liệu thực tế năm 2025."
                                        ],
                                        className="lead text-secondary mb-3",
                                        style={
                                            "maxWidth": "900px",
                                            "margin": "0 auto"
                                        }
                                    ),

                                    html.P(
                                        "Được xây dựng nhằm hỗ trợ thí sinh, phụ huynh và cố vấn tuyển sinh "
                                        "trong việc ra quyết định chính xác, trực quan và hiệu quả hơn.",
                                        className="text-muted mb-4",
                                        style={
                                            "maxWidth": "800px",
                                            "margin": "0 auto"
                                        }
                                    ),

                                    html.Div(
                                        [
                                            dbc.Badge(
                                                "Dash + Plotly",
                                                color="primary",
                                                className="me-2 px-3 py-2 rounded-pill"
                                            ),

                                            dbc.Badge(
                                                "Polars + PyArrow",
                                                color="dark",
                                                className="me-2 px-3 py-2 rounded-pill"
                                            ),

                                            dbc.Badge(
                                                "Decision Support System",
                                                color="secondary",
                                                className="px-3 py-2 rounded-pill"
                                            ),
                                        ],
                                        className="mb-4"
                                    ),

                                    html.Div(
                                        [
                                            html.Small(
                                                [
                                                    "Developed by ",
                                                    html.Strong("Mus"),
                                                    " • Information Systems • Graduation Project"
                                                ],
                                                className="text-muted"
                                            )
                                        ]
                                    )
                                ],
                                className="text-center py-5"
                            )
                        ],
                        width=12
                    )
                ]
            )
        ],
        fluid=True,
        className="bg-white border-bottom"
    ),


    # =====================================================
    # FEATURES SECTION
    # =====================================================

    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                "Khám phá Hệ thống",
                                className="fw-bold text-center mb-2"
                            ),

                            html.P(
                                "Hai công cụ chính giúp phân tích phổ điểm và xây dựng chiến lược xét tuyển hiệu quả",
                                className="text-center text-muted mb-5"
                            ),
                        ],
                        width=12
                    )
                ]
            ),

            dbc.Row(
                [

                    # =========================================
                    # FEATURE 1
                    # =========================================

                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            html.I(
                                                className="bi bi-card-checklist text-primary",
                                                style={"fontSize": "3rem"}
                                            ),
                                            className="mb-3"
                                        ),

                                        html.H3(
                                            "Tra cứu theo SBD",
                                            className="fw-bold mb-3"
                                        ),

                                        html.P(
                                            "Phân tích dữ liệu thực tế của thí sinh năm 2025 thông qua số báo danh. "
                                            "Hệ thống tự động bóc tách tổ hợp môn, đánh giá vị thế điểm số "
                                            "và hỗ trợ ra quyết định xét tuyển.",
                                            className="text-secondary mb-4"
                                        ),

                                        dbc.Button(
                                            "Truy cập hệ thống 🔍",
                                            href="/dss_with_sbd",
                                            color="primary",
                                            className="w-100 py-2 fw-semibold shadow-sm",
                                            style={
                                                "borderRadius": "14px",
                                                "transition": "all 0.2s ease"
                                            }
                                        )
                                    ]
                                ),
                                className="h-100 border-0 shadow-sm rounded-4 p-3"
                            )
                        ],
                        md=6,
                        className="mb-4"
                    ),


                    # =========================================
                    # FEATURE 2
                    # =========================================

                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            html.I(
                                                className="bi bi-input-cursor-text text-success",
                                                style={"fontSize": "3rem"}
                                            ),
                                            className="mb-3"
                                        ),

                                        html.H3(
                                            "Giả lập kịch bản",
                                            className="fw-bold mb-3"
                                        ),

                                        html.P(
                                            "Cho phép người dùng tự nhập điểm dự kiến để mô phỏng nhiều "
                                            "phương án xét tuyển khác nhau, từ đó lựa chọn tổ hợp tối ưu "
                                            "và xây dựng chiến lược an toàn hơn.",
                                            className="text-secondary mb-4"
                                        ),

                                        dbc.Button(
                                            "Bắt đầu mô phỏng ⚡",
                                            href="/dss_without_sbd",
                                            color="success",
                                            className="w-100 py-2 fw-semibold shadow-sm",
                                            style={
                                                "borderRadius": "14px",
                                                "transition": "all 0.2s ease"
                                            }
                                        )
                                    ]
                                ),
                                className="h-100 border-0 shadow-sm rounded-4 p-3"
                            )
                        ],
                        md=6,
                        className="mb-4"
                    ),
                ],
                className="g-4"
            )
        ],
        className="py-5"
    )
])
