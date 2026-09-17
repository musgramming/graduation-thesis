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
            [
                html.I(className="bi bi-filter-circle me-2 text-primary"),
                html.Span("Bắt buộc", className="fw-semibold")
            ],
            className="bg-white border-bottom py-3",
        ),

        dbc.CardBody(
            [
                dbc.Label(
                    "Môn học",
                    html_for="province-subject",
                    className="small fw-medium text-secondary",
                ),
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
                    className="small fw-medium text-secondary",
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
                    className="small fw-medium text-secondary",
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
            style={"overflow": "visible"} 
        ),
    ],
    # Thêm bo góc mềm mại border-0 và bóng nhẹ shadow-sm
    className="mb-3 shadow-sm border-0 rounded-4",
    style={
        "zIndex": 10, 
        "position": "relative", 
        "overflow": "visible"
    }
)




# =========================================================
#                    OPTIONAL CONTROLS
# =========================================================

optional_part = dbc.Card(
    [
        dbc.CardHeader(
            [
                html.I(className="bi bi-sliders me-2 text-secondary"),
                html.Span("Tùy chọn", className="fw-semibold")
            ],
            className="bg-white border-bottom py-3",
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
                    className="small text-secondary",
                ),
            ],
        ),
    ],
    className="shadow-sm border-0 rounded-4 mb-4",
    style={
        "zIndex": 1, 
        "position": "relative"
    }
)


# =========================================================
#                    CONTROL LAYOUT
# =========================================================

control_layout = html.Div(
    [
        html.Div(
            [
                html.I(className="bi bi-gear-fill me-2 text-primary"),
                html.H5("Thiết lập", className="fw-bold mb-0 text-dark", style={"display": "inline-block"})
            ],
            className="d-flex align-items-center mb-3 px-1"
        ),

        compulsory_part,

        optional_part,

        dbc.Button(
            [
                html.I(className="bi bi-calculator me-2"),
                "Tính toán"
            ],
            id=pid("province-button"),
            color="primary",
            className="w-100 py-2 fw-semibold shadow-sm rounded-pill",
        ),
    ]
)