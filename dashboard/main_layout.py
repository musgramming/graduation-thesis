import dash
from dash import html, page_container, callback, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc





# =========================================================
#                       CONSTANTS
# =========================================================

APP_TITLE = "Phân tích Dữ liệu thi Tốt nghiệp THPT"
APP_BADGE = "Đồ án tốt nghiệp"





# =========================================================
#                       STYLES
# =========================================================

STYLES = {
    "APP": {
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "backgroundColor": "#f8f9fa",
        "userSelect": "none",
    },
    "HEADER": {
        "minHeight": "72px",
        "backgroundColor": "#ffffff",
        "borderBottom": "1px solid #e9ecef",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.03)",
        "display": "flex",
        "alignItems": "center",
        "padding": "0 1rem",
        "position": "sticky",
        "top": "0",
        "zIndex": 1030,
    },
    "MAIN": {
        "flex": "1",
        "overflow": "auto",
        "padding": "1.5rem 0",
    },
    "FOOTER": {
        "backgroundColor": "#212529",
        "borderTop": "1px solid #343a40",
        "padding": "0.9rem 0",
    },
    "MENU_BUTTON": {
        "width": "42px",
        "height": "42px",
    },
    "SIDEBAR": {
        "width": "280px",
    },
}





# =========================================================
#                    NAVIGATION HELPERS
# =========================================================

def get_navigation():
    """
    Tạo danh sách điều hướng từ Dash Page Registry.
    """
    # Lấy danh sách các trang đã được đăng ký
    pages = sorted(
        dash.page_registry.values(),
        key=lambda page: page.get("order", 999),
    )

    navigation = []

    # Nếu chưa có trang nào được đăng ký (phòng hờ lỗi load), hiển thị thông báo nhẹ
    if not pages:
        return html.Div("Chưa có trang nào được cấu hình.", className="text-muted small p-2")

    for page in pages:
        # Bỏ qua trang not_found nếu không muốn hiện trên menu (tùy chọn)
        if page.get("path") == "/not-found":
            continue
            
        navigation.append(
            dbc.NavLink(
                [
                    html.I(className="bi bi-chevron-right me-2"),
                    html.Span(page.get("name", "Unnamed")),
                ],
                href=page.get("path"),
                active="exact",
                className="mb-1 rounded py-2 px-3",
                id={
                    "type": "sidebar-link", 
                    "index": page.get("path")
                }
            )
        )

    return navigation





# =========================================================
#                       SIDEBAR
# =========================================================

sidebar = dbc.Offcanvas(
    [
        html.Div(
            [
                html.H5(
                    "Điều hướng",
                    className="fw-bold mb-1",
                ),
                html.Small(
                    "Các chức năng của hệ thống",
                    className="text-muted",
                ),
            ],
            className="mb-4",
        ),
        # Container chứa menu động
        html.Div(id="sidebar-navigation-container")
    ],
    id="app-sidebar",
    title="Menu",
    is_open=False,
    placement="start",
    scrollable=True,
    backdrop=True, 
    keyboard=True,  
)





# =========================================================
#                      SIDEBAR CALLBACK
# =========================================================

@callback(
    Output("sidebar-navigation-container", "children"),
    Input("app-sidebar", "is_open"),
)
def update_sidebar_navigation(is_open):
    """
    Tự động cập nhật danh sách menu kèm theo style giao diện Bootstrap khi mở sidebar.
    """
    if not is_open:
        return dash.no_update
        
    pages = sorted(
        dash.page_registry.values(),
        key=lambda page: page.get("order", 999),
    )

    navigation = []
    for page in pages:
        if page.get("path") == "/not-found":
            continue
            
        navigation.append(
            dbc.NavLink(
                [
                    html.I(className="bi bi-chevron-right me-2"),
                    html.Span(page.get("name", "Unnamed")),
                ],
                href=page.get("path"),
                active="exact",
                className="mb-1 rounded py-2 px-3",
            )
        )

    # Đưa vào dbc.Nav để giữ chuẩn giao diện thanh menu dọc (vertical, pills)
    return dbc.Nav(
        navigation,
        vertical=True,
        pills=True,
    )





# =========================================================
#                        HEADER
# =========================================================

header = html.Header(
    dbc.Container(
        [
            # Menu button
            dbc.Button(
                html.Img(
                    src="/assets/images/menu.jpg",
                    style={
                        "height": "32px",
                        "width": "32px",
                        "objectFit": "contain",
                    },
                ),
                id="sidebar-toggle",
                color="link",
                className="p-0 me-3 d-flex align-items-center",
            ),

            # Title
            html.Div(
                [
                    html.H2(
                        "Phân tích Dữ liệu thi Tốt nghiệp THPT",
                        className="mb-0 fw-bold text-primary",
                        style={
                            "fontSize": "1.45rem",
                            "letterSpacing": "1px",
                        },
                    ),

                    html.Span(
                        "Đồ án tốt nghiệp",
                        className="badge rounded-pill ms-3",
                        style={
                            "backgroundColor": "#e7f1ff",
                            "color": "#0d6efd",
                            "fontWeight": "500",
                            "padding": "0.45rem 0.8rem",
                        },
                    ),
                ],
                className="d-flex align-items-center flex-wrap",
            ),

            # Home
            html.A(
                html.Img(
                    src="/assets/images/home.png",
                    style={
                        "height": "34px",
                        "width": "auto",
                    },
                ),
                href="/",
                className="ms-auto d-flex align-items-center",
            ),
        ],
        fluid=True,
        className="d-flex align-items-center",
    ),
    style=STYLES["HEADER"],
)





# =========================================================
#                          MAIN
# =========================================================

main = html.Main(
    dbc.Container(
        html.Div(
            page_container,
            className="animate__animated animate__fadeIn",
        ),
        fluid=True,
        className="px-md-4",
    ),
    style=STYLES["MAIN"],
)





# =========================================================
#                         FOOTER
# =========================================================

footer = html.Footer(
    dbc.Container(
        html.P(
            [
                "© 2026 Developed by ",
                html.Strong(
                    "Mus",
                    className="text-white",
                ),
                " | Information Systems",
            ],
            className="mb-0 text-center small text-white-50",
        ),
        fluid=True,
    ),
    style=STYLES["FOOTER"],
)





# =========================================================
#                      SIDEBAR CALLBACK
# =========================================================

# Cập nhật lại callback xử lý sidebar để nó tự đóng khi:
# 1. Bấm nút toggle mở/đóng menu
# 2. Hoặc khi người dùng bấm vào bất kỳ đường dẫn nào trên menu để chuyển trang
@callback(
    Output("app-sidebar", "is_open"),
    [
        Input("sidebar-toggle", "n_clicks"),                        # Lắng nghe sự kiện click vào các NavLink nằm trong menu điều hướng
        Input({"type": "sidebar-link", "index": ALL}, "n_clicks"),
    ],
    [
        State("app-sidebar", "is_open"),
    ],
    prevent_initial_call=True,
)
def toggle_sidebar(n_toggle, link_clicks, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
        
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Nếu bấm nút toggle thì đảo trạng thái (mở -> đóng, đóng -> mở)
    if "sidebar-toggle" in triggered_id:
        return not is_open
        
    # Nếu bấm vào bất kỳ đường dẫn trang nào trong sidebar thì luôn đóng lại (False)
    return False





# =========================================================
#                       APP LAYOUT
# =========================================================

app_layout = html.Div(
    [
        html.Noscript(
            html.Div(
                [
                    html.H3(
                        "YÊU CẦU JAVASCRIPT",
                        className="text-danger fw-bold",
                    ),
                    html.P(
                        "Vui lòng kích hoạt JavaScript "
                        "để sử dụng hệ thống.",
                        className="text-muted",
                    ),
                ],
                className="text-center mt-5",
            )
        ),

        html.Div(
            id="protected-content",
            children=[
                sidebar,
                header,
                main,
                footer,
            ],
            style=STYLES["APP"],
        ),
    ]
)