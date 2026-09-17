from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc
from utils.exception import unreachable

from .list_of_id import pid

from .nation import (
    control_layout as nation_control_layout, 
    dashboard_layout as nation_dashboard_layout
)

from .provinces import (
    control_layout as provinces_control_layout,
    dashboard_layout as provinces_dashboard_layout,
)





layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Tabs(
                        children=[
                            dbc.Tab(
                                label="Thống kê theo cả nước",
                                tab_id="nation",
                            ),
                            dbc.Tab(
                                label="Thống kê theo tỉnh thành",
                                tab_id="provinces",
                            ),
                        ],
                        id=pid("type-of-tab"),
                        active_tab="nation",
                    ),
                    width=12,
                ),
            ],
            className="mb-3",
        ),

        dbc.Row(
            [
                dbc.Col(
                    html.Div(id=pid("controls")),
                    xs=12,
                    md=3,
                ),

                dbc.Col(
                    html.Div(id=pid("dashboard")),
                    xs=12,
                    md=9,
                    className="mt-3 mt-md-0",
                ),
            ],
        ),
    ],
    fluid=True,
)


@callback(
    [
        Output(pid("controls"), "children"),
        Output(pid("dashboard"), "children"),
    ],
    Input(pid("type-of-tab"), "active_tab"),
)
def use_tab(tab):
    match tab:
        case "provinces":
            return (
                provinces_control_layout,
                provinces_dashboard_layout,
            )

        case "nation":
            return (
                nation_control_layout,
                nation_dashboard_layout,
            )

        case _:
            unreachable("Không tới được đoạn này")

    unreachable("Không tới được đoạn này")