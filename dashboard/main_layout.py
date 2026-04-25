import dash
from dash import html, page_container
import dash_bootstrap_components as dbc



# Tách biệt Styles để dễ quản lý
STYLES = {
    "OUTER_CONTAINER": {
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "backgroundColor": "#f8f9fa", # Màu nền xám nhạt hiện đại
        "userSelect": "none"
    },
    "HEADER": "d-flex align-items-center justify-content-center bg-white border-bottom shadow-sm px-4",
    "MAIN": "flex-grow-1 overflow-auto p-4",
    "FOOTER": "bg-dark text-white-50 py-3 text-center fs-6 border-top"
}



# 1. Header tinh tế hơn
header = html.Header(
    dbc.Container(
        [
            html.H2("Phân tích Dữ liệu THPTQG 2025", 
                    className="m-0 fw-bold text-primary", 
                    style={"letterSpacing": "1.5px", "fontSize": "1.5rem"}),
            html.Span("Đồ án tốt nghiệp", className="badge bg-soft-primary text-primary ms-3 d-none d-sm-inline")
        ],
        fluid=True,
        className="d-flex align-items-center justify-content-between"
    ),
    className=STYLES["HEADER"],
    style={"minHeight": "70px"}
)



# 2. Phần hiển thị nội dung chính
main = html.Main(
    dbc.Container(
        [
            # Thêm hiệu ứng fade-in nhẹ cho page_container qua CSS nếu muốn
            html.Div(page_container, className="animate__animated animate__fadeIn")
        ],
        fluid=True,
        className="py-3"
    ),
    className=STYLES["MAIN"]
)



# 3. Footer chuyên nghiệp
footer = html.Footer(
    html.Div([
        html.P([
            "© 2026 Developed by ",
            html.Strong("Mus", className="text-white"),
            " | Information Systems"
        ], className="mb-0 small")
    ]),
    className=STYLES["FOOTER"]
)



# Layout tổng thể
app_layout = html.Div([
    # Phần dành cho No-JS
    html.Noscript(
        html.Div([
            html.H1("YÊU CẦU JAVASCRIPT", style={"color": "#dc3545"}),
            html.P("Vui lòng kích hoạt JavaScript để sử dụng hệ thống.")
        ], className="text-center mt-5")
    ),
    
    # Nội dung chính
    html.Div(
        id="protected-content",
        children=[
            header,
            main,
            footer
        ],
        style=STYLES["OUTER_CONTAINER"]
    )
])
