from dash import html, dcc
import dash_bootstrap_components as dbc

from data import (
    BANG_CHON_MON_DROPDOWN,
    BANG_DIEM
)

from .list_of_id import pid





# =========================================================
#                    COMPULSORY CONTROLS
# =========================================================

compulsory_part = dbc.Card(
    [
        dbc.CardHeader(
            "Bắt buộc",
            className="fw-semibold",
        ),

        # Thêm overflow-visible hoặc dùng chung cấu trúc CSS .card-body của bạn
        dbc.CardBody(
            [
                dbc.Label(
                    "Môn học",
                    html_for="province-subject",
                ),
                # Bọc dcc.Dropdown vào div có class wrapper để định vị menu tuyệt đối
                html.Div(
                    dcc.Dropdown(
                        id=pid("province-subject"),
                        options=BANG_CHON_MON_DROPDOWN,
                        value="Toán",
                        clearable=False,
                        searchable=True,
                        className="comb-dropdown",
                    ),
                    className="comb-dropdown-wrapper mb-3"
                ),

                dbc.Label(
                    "Năm",
                    html_for="province-year",
                ),
                html.Div(
                    dcc.Dropdown(
                        id=pid("province-year"),
                        options=[
                            {
                                "label": year,
                                "value": year,
                            }
                            for year
                            in sorted(
                                BANG_DIEM.keys(),
                                reverse=True,
                            )
                        ],
                        value="2026",
                        clearable=False,
                        searchable=False,
                        className="comb-dropdown",
                    ),
                    className="comb-dropdown-wrapper mb-3"
                ),

                dbc.Label(
                    "Tỉnh thành",
                    html_for="province-name",
                ),
                html.Div(
                    dcc.Dropdown(
                        id=pid("province-name"),
                        options=[],
                        value=None,
                        clearable=False,
                        searchable=True,
                        className="comb-dropdown",
                    ),
                    className="comb-dropdown-wrapper"
                ),
            ],
        ),
    ],
    className="mb-3" # Thêm khoảng cách nếu cần
)






# =========================================================
#                     OPTIONAL CONTROLS
# =========================================================

optional_part = dbc.Card(
    [
        dbc.CardHeader(
            "Tùy chọn",
            className="fw-semibold",
        ),

        dbc.CardBody(
            [
                dbc.Checklist(
                    id=pid("province-options"),
                    options=[
                        {
                            "label": "Cho phép tính đến điểm 0",
                            "value": "include_zero",
                        },
                        {
                            "label": "Cho phép tính đến các bạn trượt tốt nghiệp",
                            "value": "include_failed",
                        },
                    ],
                    value=[
                        "include_zero",
                        "include_failed",
                    ],
                    switch=True,
                ),
            ],
        ),
    ],
)





# =========================================================
#                     CONTROL LAYOUT
# =========================================================

control_layout = html.Div(
    [
        html.H5(
            "Thiết lập",
            className="fw-bold mb-3",
        ),

        compulsory_part,

        optional_part,

        html.Div(className="my-3"),

        dbc.Button(
            "Tính toán",
            id=pid("province-button"),
            color="primary",
            className="w-100",
        ),
    ]
)