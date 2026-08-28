from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.naming import naming_without_sbd
from utils.persistent import make_persistent
from data import BANG_CHON_MON


def input_num(id: str, **kwargs):
    """
    Tạo ô nhập điểm số.

    Giá trị được lưu trong session để giữ lại khi người dùng
    chuyển đổi hoặc tương tác với trang.
    """
    return dbc.Input(
        id=naming_without_sbd(id),
        type="number",
        min=0,
        max=10,
        value=0,
        step=0.01,
        className="text-center shadow-sm border-primary-subtle",
        persistence=True,
        persistence_type="session",
        persisted_props=["value"],
        **kwargs,
    )


# ---------------------------------------------------------------------------
# LEFT PANEL
# ---------------------------------------------------------------------------
left_layout = html.Div(
    [
        # BƯỚC 1: NHẬP ĐIỂM
        dbc.Card(
            [
                dbc.CardHeader(
                    html.Div(
                        [
                            html.I(className="bi bi-pencil-fill me-2"),
                            "Điểm dự kiến của bạn",
                        ]
                    ),
                    className="fw-bold bg-primary text-white",
                ),
                dbc.CardBody(
                    [
                        # Năm xét tuyển
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Năm xét tuyển",
                                    width=12,
                                    md=6,
                                    className="small fw-bold",
                                ),
                                dbc.Col(
                                    make_persistent(
                                        dbc.Input(
                                            id=naming_without_sbd("year"),
                                            type="number",
                                            min=2025,
                                            step=1,
                                            value=2025,
                                            className="text-center",
                                        )
                                    ),
                                    width=12,
                                    md=6,
                                ),
                            ],
                            className="mb-3 g-2 align-items-center",
                        ),

                        html.Hr(className="my-3"),

                        # Khu vực nhập điểm
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label(
                                                "Toán",
                                                className="fw-bold mb-0",
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            input_num("math"),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2 align-items-center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label(
                                                "Văn",
                                                className="fw-bold mb-0",
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            input_num("literature"),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2 align-items-center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            make_persistent(
                                                dcc.Dropdown(
                                                    options=BANG_CHON_MON,
                                                    value="Lí",
                                                    id=naming_without_sbd("mon-1"),
                                                    clearable=False,
                                                    className="small",
                                                )
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            input_num("diem-mon-1"),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2 align-items-center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            make_persistent(
                                                dcc.Dropdown(
                                                    id=naming_without_sbd("mon-2"),
                                                    options=[
                                                        x
                                                        for x in BANG_CHON_MON
                                                        if x["value"] != "Lí"
                                                    ],
                                                    value="Hóa",
                                                    clearable=False,
                                                    placeholder="Chọn môn 2",
                                                    className="small",
                                                )
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            input_num("diem-mon-2"),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-4 align-items-center",
                                ),
                            ],
                            className="px-1",
                        ),

                        dbc.Button(
                            "Tính toán điểm tổ hợp",
                            id=naming_without_sbd("build-combs"),
                            color="primary",
                            disabled=True,
                            className="w-100 fw-bold shadow-sm py-2",
                        ),
                    ]
                ),
            ],
            className="border-0 shadow-sm mb-3",
        ),

        # Thông báo lỗi
        html.Div(
            id=naming_without_sbd("error"),
            className="mb-3",
        ),

        # BƯỚC 2: XÂY DỰNG KỊCH BẢN
        dbc.Card(
            [
                dbc.CardHeader(
                    html.Div(
                        [
                            html.I(
                                className="bi bi-gear-wide-connected me-2"
                            ),
                            "Xây dựng kịch bản",
                        ]
                    ),
                    className="fw-bold bg-dark text-white",
                ),
                dbc.CardBody(
                    [
                        # Chọn tổ hợp & điểm
                        html.Div(
                            [
                                html.Label(
                                    "Tổ hợp khả dĩ",
                                    className="small fw-bold mb-1",
                                ),
                                make_persistent(
                                    dcc.Dropdown(
                                        id=naming_without_sbd("your-comb"),
                                        options=[],
                                        value=None,
                                        clearable=False,
                                        placeholder="Chọn tổ hợp...",
                                        disabled=False,
                                        className="mb-3",
                                    )
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "Điểm tổ hợp của bạn",
                                            className="small text-muted d-block",
                                        ),
                                        make_persistent(
                                            dbc.Input(
                                                id=naming_without_sbd("your-score"),
                                                value="",
                                                readonly=True,
                                                className=(
                                                    "h4 fw-bold text-primary "
                                                    "text-center bg-transparent "
                                                    "border-0"
                                                ),
                                            )
                                        ),
                                    ],
                                    className=(
                                        "p-2 mb-3 bg-light rounded-3 "
                                        "border-dashed text-center"
                                    ),
                                ),
                            ]
                        ),

                        make_persistent(
                            dcc.Store(
                                id=naming_without_sbd("stored-results"),
                                storage_type="memory",
                            )
                        ),

                        # Điểm sàn
                        html.Label(
                            "Thiết lập điểm sàn",
                            className="fw-bold small mb-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    make_persistent(
                                        dbc.Input(
                                            id=naming_without_sbd(
                                                "floor-score-input"
                                            ),
                                            type="number",
                                            min=15,
                                            max=30,
                                            step=0.05,
                                            value=15,
                                            className="text-center shadow-sm",
                                        )
                                    ),
                                    width=12,
                                    md=4,
                                ),
                                dbc.Col(
                                    make_persistent(
                                        dcc.Slider(
                                            id=naming_without_sbd("floor-score"),
                                            min=15,
                                            max=30,
                                            step=0.05,
                                            value=15,
                                            marks={
                                                i: str(i)
                                                for i in range(15, 31, 5)
                                            },
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "bottom",
                                            },
                                            className="mt-2",
                                        )
                                    ),
                                    width=12,
                                    md=8,
                                ),
                            ],
                            className="mb-4 align-items-center g-2",
                        ),

                        # Danh sách tổ hợp so sánh.
                        # Component dcc.Dropdown bên trong được tạo động
                        # bởi callback khi đã có tổ hợp chính.
                        html.Div(
                            [
                                html.Label(
                                    "Tổ hợp so sánh",
                                    className="small fw-bold",
                                ),
                                html.Div(
                                    id=naming_without_sbd(
                                        "combs-list-container"
                                    ),
                                    className=(
                                        "mb-4 p-2 bg-white rounded border "
                                        "min-vh-10"
                                    ),
                                ),
                            ]
                        ),

                        dbc.Button(
                            "Chạy kịch bản phân tích",
                            id=naming_without_sbd("run-scenario"),
                            color="success",
                            # disabled=True,
                            className="w-100 py-2 fw-bold shadow",
                        ),
                    ]
                ),
            ],
            id=naming_without_sbd("scenario"),
            style={"display": "none"},
            className="border-0 shadow-sm",
        ),
    ],
    className="sticky-top",
    style={"top": "1rem"},
)


# ---------------------------------------------------------------------------
# PAGE LAYOUT
# ---------------------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    left_layout,
                    width=12,
                    md=4,
                    className="px-1",
                ),
                dbc.Col(
                    dcc.Loading(
                        id=naming_without_sbd("loading-main"),
                        type="circle",
                        children=html.Div(
                            id=naming_without_sbd("right-content"),
                            className="h-100",
                        ),
                    ),
                    width=12,
                    md=8,
                    className="px-1",
                ),
            ],
            className="mt-3 mt-md-4 g-4",
        )
    ],
    fluid=True,
    className="p-0 px-3 px-md-5 pb-5 bg-light",
)