from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.persistent import make_persistent
from .list_of_id import pid





# ---------------------------------------------------------------------------
# LEFT LAYOUT
# ---------------------------------------------------------------------------
left_layout = html.Div([

    # =======================================================================
    # CARD 1: KẾT QUẢ THI
    # =======================================================================
    dbc.Card([
        dbc.CardHeader(
            "Kết quả thi Tốt nghiệp THPT của bạn",
            className="fw-bold bg-primary text-white"
        ),

        dbc.CardBody([
            # ----------------------------------------------------------------
            # SBD
            # ----------------------------------------------------------------
            dbc.Row([
                dbc.Label(
                    "Số báo danh",
                    width=12,
                    md=4,
                    className="small fw-bold"
                ),

                dbc.Col([
                    make_persistent(
                        dbc.Input(
                            id=pid("sbd"),
                            type="text",
                            minlength=8,
                            maxlength=8,
                            inputMode="numeric",
                            placeholder="VD: 01000001",
                            className="shadow-sm"
                        )
                    ),

                    dbc.FormFeedback(
                        id=pid("sbd-feedback"),
                        type="invalid"
                    ),
                ], width=12, md=8),
            ], className="mb-3 align-items-center"),

            # ----------------------------------------------------------------
            # Năm thi
            # ----------------------------------------------------------------
            dbc.Row([
                dbc.Label(
                    "Năm thi",
                    width=12,
                    md=4,
                    className="small fw-bold"
                ),

                dbc.Col(
                    make_persistent(
                        dbc.Input(
                            id=pid("year"),
                            type="number",
                            min=2025,
                            step=1,
                            value=2025,
                            className="shadow-sm"
                        )
                    ),
                    width=12,
                    md=8
                ),
            ], className="mb-4 align-items-center"),

            # ----------------------------------------------------------------
            # Nút Tra cứu
            # ----------------------------------------------------------------
            html.Div(
                dbc.Button(
                    [
                        html.I(className="bi bi-search me-2"),
                        "Tra cứu"
                    ],
                    id=pid("search-info"),
                    color="primary",
                    className="w-100 shadow-sm fw-bold"
                ),
                className="mb-4"
            ),

            # ----------------------------------------------------------------
            # Kết quả sau tra cứu
            # ----------------------------------------------------------------
            html.Div([
                dbc.Row([
                    dbc.Label(
                        "Tổ hợp",
                        width=12,
                        md=4,
                        className="small"
                    ),

                    dbc.Col([
                        make_persistent(
                            dcc.Dropdown(
                                id=pid("comb"),
                                placeholder="Chọn tổ hợp...",
                                clearable=False
                            )
                        ),

                        html.Div(
                            id=pid("status-output-2"),
                            className="small mt-1"
                        )
                    ], width=12, md=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Label(
                        "Điểm",
                        width=12,
                        md=4,
                        className="small"
                    ),

                    dbc.Col(
                        html.Div(
                            id=pid("score"),
                            children="---",
                            className="h4 fw-bold text-primary mb-0"
                        ),
                        width=12,
                        md=8
                    )
                ]),
            ], className="p-3 bg-light rounded-3 border border-dashed"),
        ])
    ], className="shadow-sm border-0 mb-4"),





    # =======================================================================
    # CARD 2: XÂY DỰNG KỊCH BẢN
    # =======================================================================
    dbc.Card([
        dbc.CardHeader(
            "Xây dựng kịch bản",
            className="fw-bold bg-dark text-white"
        ),

        dbc.CardBody([
            # ----------------------------------------------------------------
            # Tổ hợp so sánh
            # ----------------------------------------------------------------
            dbc.Row([
                dbc.Label(
                    "Tổ hợp so sánh",
                    width=12,
                    md=4,
                    className="small fw-bold"
                ),

                dbc.Col(
                    dcc.Dropdown(
                        id=pid("combs-script"),
                        options=[],
                        value=[],
                        multi=True,
                        clearable=True,
                        disabled=True,
                        placeholder="Chọn tổ hợp để so sánh..."
                    ),
                    width=12,
                    md=8
                )
            ], className="mb-4"),

            # ----------------------------------------------------------------
            # Điểm sàn
            # ----------------------------------------------------------------
            dbc.Row([
                dbc.Col([
                    dbc.Label(
                        "Điểm sàn",
                        className="small fw-bold mb-2"
                    ),

                    dbc.InputGroup([
                        dbc.Input(
                            id=pid("floor-score-input"),
                            type="number",
                            min=15,
                            max=30,
                            step=0.05,
                            value=15,
                            className="shadow-sm",
                        ),

                        dbc.InputGroupText("điểm"),
                    ], className="mb-2"),

                    dcc.Slider(
                        id=pid("floor-score-slider"),
                        min=15,
                        max=30,
                        step=0.05,
                        value=15,
                        disabled=True,
                        marks={15: "15"},
                        tooltip={
                            "always_visible": True,
                            "placement": "bottom",
                        }
                    ),

                    dbc.Alert(
                        id=pid("floor-score-warning"),
                        is_open=False,
                        color="warning",
                        className="p-2 small mt-2 mb-0"
                    )
                ], width=12)
            ], className="mb-4"),

            html.Hr(),

            # ----------------------------------------------------------------
            # Phương pháp quy đổi
            # ----------------------------------------------------------------
            html.Label(
                "Phương pháp quy đổi:",
                className="fw-bold small mb-2 d-block"
            ),

            make_persistent(
                dcc.RadioItems(
                    options=[
                        {"label": " Điểm thô", "value": "raw-score"},
                        {"label": " Z-Score", "value": "z-score"},
                        {"label": " Robust", "value": "robust"}
                    ],
                    value="raw-score",
                    id=pid("mode-selection"),
                    labelStyle={
                        "display": "inline-block",
                        "marginRight": "15px",
                        "fontSize": "14px"
                    },
                    inputStyle={"marginRight": "5px"},
                    className="mb-4"
                )
            ),

            # ----------------------------------------------------------------
            # Nút xây kịch bản
            # ----------------------------------------------------------------
            dbc.Button(
                [
                    html.I(className="bi bi-lightning-fill me-2"),
                    "Xây kịch bản"
                ],
                id=pid("analysis"),
                color="success",
                disabled=True,
                className="w-100 shadow fw-bold py-2"
            ),
        ])
    ], className="shadow-sm border-0")
], className="sticky-top", style={"top": "1rem"})





# ---------------------------------------------------------------------------
# RIGHT LAYOUT
# ---------------------------------------------------------------------------
right_layout = dbc.Card([
    dbc.CardHeader(
        [
            html.Span(
                "Phân tích dữ liệu & Phổ điểm",
                className="fw-bold text-primary"
            )
        ],
        className="bg-white"
    ),

    dbc.CardBody([
        dcc.Loading(
            id=pid("loading-analysis"),
            type="circle",
            children=html.Div(
                [
                    dbc.Alert(
                        [
                            html.Div(
                                html.I(className="bi bi-bar-chart-line fs-2"),
                                className="mb-2"
                            ),

                            html.Div(
                                "Chưa có dữ liệu phân tích",
                                className="fw-bold mb-1"
                            ),

                            html.Small(
                                'Nhập số báo danh, chọn "Tra cứu", rồi nhấn nút "Xây dựng kịch bản" để bắt đầu.'
                            )
                        ],
                        color="light",
                        className="text-center border-0 py-5 mb-0"
                    )
                ],
                id=pid("full-div"),
                style={"minHeight": "500px"}
            )
        )
    ])
], className="shadow-sm border-0 h-100")





# ---------------------------------------------------------------------------
# PAGE LAYOUT
# ---------------------------------------------------------------------------
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            left_layout,
            width=12,
            md=4,
            className="mb-4 p-1"
        ),

        dbc.Col(
            right_layout,
            width=12,
            md=8,
            className="p-1"
        )
    ], className="mt-4 g-4")
], fluid=True, className="p-0 px-3 px-md-5 pb-5 bg-light")
