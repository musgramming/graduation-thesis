from dash import page_registry, html
import dash_bootstrap_components as dbc


def build_sidebar_nav():
    """
    Hàm duy nhất chịu trách nhiệm dựng danh sách điều hướng từ Dash Page Registry.
    Đảm bảo tính nhất quán về Pattern-Matching ID cho callback đóng mở sidebar.
    """
    pages = sorted(
        page_registry.values(),
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
                id={
                    "type": "sidebar-link", 
                    "index": page.get("path")
                }
            )
        )

    if not navigation:
        return html.Div("Chưa có trang nào được cấu hình.", className="text-muted small p-2")

    return dbc.Nav(
        navigation,
        vertical=True,
        pills=True,
    )