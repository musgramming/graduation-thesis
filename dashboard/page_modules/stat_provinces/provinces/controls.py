from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

from data import (
    BANG_CHON_MON_DROPDOWN,
    BANG_QUY_DOI_TINH_THANH,
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

        dbc.CardBody(
            [
                dbc.Label(
                    "Môn học",
                    html_for="province-subject",
                ),

                dcc.Dropdown(
                    id=pid("province-subject"),
                    options=BANG_CHON_MON_DROPDOWN,
                    value="Toán",
                    clearable=False,
                    searchable=True,
                ),

                dbc.Label(
                    "Năm",
                    html_for="province-year",
                    className="mt-3",
                ),

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
                ),

                dbc.Label(
                    "Tỉnh thành",
                    html_for="province-name",
                    className="mt-3",
                ),

                dcc.Dropdown(
                    id=pid("province-name"),
                    options=[],
                    value=None,
                    clearable=False,
                    searchable=True,
                ),
            ],
        ),
    ],
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

        html.Div(className="my-3"),

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





@callback(
    Output(pid("province-name"), "options"),
    Output(pid("province-name"), "value"),
    Input(pid("province-year"), "value"),
    State(pid("province-name"), "value"),
    State(pid("province-name"), "options"),
)
def update_province_options(year, current_province, current_options):

    if year is None:
        return [], None

    year = str(year)

    # Lấy tên tỉnh đang được chọn từ options của năm trước
    current_province_name = next(
        (
            option["label"]
            for option in (current_options or [])
            if option["value"] == current_province
        ),
        None,
    )

    province_options = [
        {
            "label": name,
            "value": code,
        }
        for code, name
        in BANG_QUY_DOI_TINH_THANH[year].items()
    ]

    # Tìm mã của cùng tỉnh trong năm mới
    new_province_code = next(
        (
            code
            for code, name
            in BANG_QUY_DOI_TINH_THANH[year].items()
            if name == current_province_name
        ),
        None,
    )

    # Không tìm thấy → Hà Nội
    if new_province_code is None:
        new_province_code = next(
            (
                code
                for code, name
                in BANG_QUY_DOI_TINH_THANH[year].items()
                if name == "Hà Nội"
            ),
            None,
        )

    return province_options, new_province_code