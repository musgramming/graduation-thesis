import dash
from dash import html, page_container
import dash_bootstrap_components as dbc


# =========================================================
#                         STYLES
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
        "boxShadow": "0 2px 8px rgba(0,0,0,0.03)",
        "display": "flex",
        "alignItems": "center",
        "padding": "0 1rem",
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
}



# =========================================================
#                         HEADER
# =========================================================

header = html.Header(
    dbc.Container(
        [
            # Left side
            html.Div(
                [
                    html.H2(
                        "Phân tích Dữ liệu THPTQG 2025",
                        className="mb-0 fw-bold text-primary",
                        style={
                            "fontSize": "1.45rem",
                            "letterSpacing": "1px",
                        }
                    ),

                    html.Span(
                        "Đồ án tốt nghiệp",
                        className="badge rounded-pill ms-3",
                        style={
                            "backgroundColor": "#e7f1ff",
                            "color": "#0d6efd",
                            "fontWeight": "500",
                            "padding": "0.45rem 0.8rem",
                        }
                    ),
                ],
                className="d-flex align-items-center flex-wrap"
            ),

            # Right side
            html.A(
                html.Img(
                    src="/assets/images/home.png",
                    style={
                        "height": "34px",
                        "width": "auto",
                        "cursor": "pointer",
                        "transition": "0.2s ease",
                    }
                ),
                href="/",
                className="ms-auto d-flex align-items-center text-decoration-none"
            ),
        ],
        fluid=True,
        className="d-flex align-items-center justify-content-between"
    ),
    style=STYLES["HEADER"]
)



# =========================================================
#                         MAIN
# =========================================================

main = html.Main(
    dbc.Container(
        html.Div(
            page_container,
            className="animate__animated animate__fadeIn"
        ),
        fluid=True,
        className="px-md-4"
    ),
    style=STYLES["MAIN"]
)



# =========================================================
#                         FOOTER
# =========================================================

footer = html.Footer(
    dbc.Container(
        html.P(
            [
                "© 2026 Developed by ",
                html.Strong("Mus", className="text-white"),
                " | Information Systems"
            ],
            className="mb-0 text-center small text-white-50"
        ),
        fluid=True
    ),
    style=STYLES["FOOTER"]
)



# =========================================================
#                      APP LAYOUT
# =========================================================

app_layout = html.Div(
    [
        html.Noscript(
            html.Div(
                [
                    html.H3(
                        "YÊU CẦU JAVASCRIPT",
                        className="text-danger fw-bold"
                    ),
                    html.P(
                        "Vui lòng kích hoạt JavaScript để sử dụng hệ thống.",
                        className="text-muted"
                    )
                ],
                className="text-center mt-5"
            )
        ),

        html.Div(
            id="protected-content",
            children=[
                header,
                main,
                footer
            ],
            style=STYLES["APP"]
        )
    ]
)
