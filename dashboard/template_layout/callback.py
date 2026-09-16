from dash import callback, Output, Input, State, no_update, ALL
from dash import callback_context as ctx
from .services import build_sidebar_nav


@callback(
    Output("sidebar-navigation-container", "children"),
    Input("app-sidebar", "is_open"),
)
def update_sidebar_navigation(is_open):
    """
    Cập nhật lại menu khi sidebar mở ra để đồng bộ trạng thái active của trang hiện tại.
    """
    if not is_open:
        return no_update
        
    return build_sidebar_nav()





@callback(
    Output("app-sidebar", "is_open"),
    [
        Input("sidebar-toggle", "n_clicks"),
        Input({"type": "sidebar-link", "index": ALL}, "n_clicks"),
    ],
    [
        State("app-sidebar", "is_open"),
    ],
    prevent_initial_call=True,
)
def toggle_sidebar(n_toggle, link_clicks, is_open):
    if not ctx.triggered:
        return is_open
        
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if "sidebar-toggle" in triggered_id:
        return not is_open
        
    return False
