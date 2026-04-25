from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from utils.naming import naming_with_sbd, naming_without_sbd # Giả sử hàm naming của bạn ở đây

register_page(
    __name__,
    path="/",
    redirect_from=["/main_page"],
    title="Hệ thống Phân tích Phổ điểm THPTQG 2025",
    description="Phân tích vị thế điểm số và dự báo tổ hợp",
)



layout = html.Div([
    # --- PHẦN 1: GIỚI THIỆU BẢN THÂN (ABOUT ME) ---
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Avatar hoặc Icon cá nhân
                    html.Div(html.I(className="bi bi-person-workspace display-1 text-primary"), className="mb-4"),
                    html.H1("Hi, mình là Mus", className="fw-bold display-4"),
                    html.P([
                        "Sinh viên năm cuối ngành ", html.B("Hệ thống thông tin"), " (IS). ",
                        "Một người yêu sự chính xác của dữ liệu và sự tinh tế của âm nhạc cổ điển."
                    ], className="lead text-secondary"),
                    html.Div([
                        dbc.Badge("Data Visualization", color="primary", className="me-2 p-2"),
                        dbc.Badge("Polars Enthusiast", color="dark", className="p-2"),
                    ], className="mb-4"),
                ], className="text-center py-5")
            ])
        ])
    ], fluid=True, className="bg-white"),

    # --- PHẦN 2: GIỚI THIỆU 2 TÍNH NĂNG CHÍNH ---
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Khám phá Hệ thống", className="text-center fw-bold mb-5"), width=12),
            
            # TÍNH NĂNG 1: Tra cứu SBD
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="bi bi-card-checklist h1 text-primary"), className="mb-3"),
                        html.H3("Tra cứu theo SBD", className="fw-bold"),
                        html.P(
                            "Phân tích vị thế dựa trên dữ liệu thực tế của thí sinh năm 2025. "
                            "Hệ thống tự động bóc tách tổ hợp và tính toán điểm chuẩn xác."
                        ),
                        dbc.Button("Thử ngay 🔍", href="/dss_with_sbd", color="primary", className="mt-2 w-100 py-2")
                    ])
                ], className="h-100 border-0 shadow p-3 hover-shadow")
            ], md=6),

            # TÍNH NĂNG 2: Nhập điểm tay (Simulated Data)
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="bi bi-input-cursor-text h1 text-success"), className="mb-3"),
                        html.H3("Giả lập kịch bản", className="fw-bold"),
                        html.P(
                            "Tự nhập các đầu điểm mong muốn để xem dự báo vị thế. "
                            "Công cụ đắc lực để so sánh các tổ hợp môn khác nhau."
                        ),
                        dbc.Button("Trải nghiệm ⚡", href="/dss_without_sbd", color="success", className="mt-2 w-100 py-2")
                    ])
                ], className="h-100 border-0 shadow p-3 hover-shadow")
            ], md=6),
        ], className="g-4 mb-5")
    ], className="py-5 bg-light"),
])
