from dash import html, dcc
import dash_bootstrap_components as dbc

from data import BANG_CHON_MON_DROPDOWN, NAM
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

        dbc.CardBody(
            [
                dbc.Label(
                    "Môn học",
                    html_for="nation-subject",
                ),
                html.Div(
                    dcc.Dropdown(
                        id=pid("nation-subject"),
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
                    html_for="nation-year",
                ),
                html.Div(
                    dcc.Dropdown(
                        id=pid("nation-year"),
                        options=[
                            {
                                "label": year,
                                "value": year,
                            }
                            for year in NAM
                        ],
                        value="2026",
                        clearable=False,
                        searchable=False,
                        className="comb-dropdown",
                    ),
                    className="comb-dropdown-wrapper"
                ),
            ],
            # 1. Bật hiển thị tràn nội dung cho phần thân Card
            style={"overflow": "visible"} 
        ),
    ],
    # 2. Đưa z-index lên cao và bật overflow visible cho thẻ Card này
    className="mb-3 shadow-sm",
    style={
        "zIndex": 10, 
        "position": "relative", 
        "overflow": "visible"
    }
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
                    id=pid("nation-options"),
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
            id=pid("nation-button"),
            color="primary",
            className="w-100",
        ),
    ]
)