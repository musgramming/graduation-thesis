from dash import callback, html, register_page, dcc, Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import polars as pl
from data import BANG_DIEM, TO_HOP
from utils.build_script import display_graph_and_table
from utils.naming import naming_with_sbd
from utils.persistent import make_persistent



register_page(
    __name__,
    path="/dss_with_sbd",
    redirect_from=["/dss-with-sbd"],
    title="Dự báo thứ hạng",
    description="Trang này cho phép các sĩ tử nhập điểm của mình và so sánh điểm của mình so với cả nước"
)





# ----------------------------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------------------------

left_layout = html.Div([
    # CARD 1: KẾT QUẢ THI
    dbc.Card([
        dbc.CardHeader("Kết quả thi THPTQG của bạn", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            # SBD
            dbc.Row([
                dbc.Label("Số báo danh", width=4, className="small fw-bold"),
                dbc.Col([
                    make_persistent(
                        dbc.Input(
                            id=naming_with_sbd("sbd"), type="text", 
                            minlength=8, maxlength=8, placeholder="VD: 01000001",
                            className="shadow-sm"
                        )
                    ),
                    dbc.FormFeedback(id=naming_with_sbd("sbd-feedback"), type="invalid"),
                ], width=8),
            ], className="mb-3 align-items-center"),

            # Năm thi
            dbc.Row([
                dbc.Label("Năm thi", width=4, className="small fw-bold"),
                dbc.Col(
                    make_persistent(
                        dbc.Input(
                            id=naming_with_sbd("year"), type="number", 
                            min=2025, max=2025, value=2025,
                            className="shadow-sm"
                        )
                    ), width=8
                ),
            ], className="mb-4 align-items-center"),

            # Nút Tra cứu
            html.Div(
                dbc.Button(
                    [html.I(className="bi bi-search me-2"), "Tra cứu"], 
                    id=naming_with_sbd("search-info"), 
                    color="primary", className="w-100 shadow-sm fw-bold"
                ),
                className="mb-4"
            ),

            # Kết quả sau tra cứu
            html.Div([
                dbc.Row([
                    dbc.Label("Tổ hợp", width=4, className="small"),
                    dbc.Col([
                        make_persistent(
                            dcc.Dropdown(id=naming_with_sbd("comb"), placeholder="Chọn tổ hợp..."),
                        ),
                        html.Div(id=naming_with_sbd("status-output-2"), className="small mt-1")
                    ], width=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Label("Điểm", width=4, className="small"),
                    dbc.Col(
                        html.Div(id=naming_with_sbd("score"), className="h4 fw-bold text-primary mb-0"),
                        width=8
                    )
                ]),
            ], className="p-3 bg-light rounded-3 border border-dashed"),

            html.Div(id=naming_with_sbd("status-output"), className="mt-3")
        ]),
    ], className="shadow-sm border-0 mb-4"),



    # CARD 2: XÂY DỰNG KỊCH BẢN
    dbc.Card([
        dbc.CardHeader("Xây dựng kịch bản", className="fw-bold bg-dark text-white"),
        dbc.CardBody([
            dbc.Row([
                dbc.Label("Tổ hợp so sánh", width=4, className="small fw-bold"),
                dbc.Col(html.Div(id=naming_with_sbd("choosing-combs"), className="text-primary fw-bold"), width=8)
            ], className="mb-3"),

            dbc.Row([
                dbc.Label("Điểm sàn", width=4, className="small fw-bold"),
                dbc.Col(html.Div(id=naming_with_sbd("choosing-score"), className="text-primary fw-bold"), width=8)
            ], className="mb-3"),

            html.Hr(),

            html.Label("Phương pháp quy đổi:", className="fw-bold small mb-2 d-block"),
            make_persistent(
                dcc.RadioItems(
                    options=[
                        {"label": " Điểm thô", "value": "raw-score"},
                        {"label": " Z-Score", "value": "z-score"},
                        {"label": " Robust", "value": "robust"}
                    ],
                    value="raw-score",
                    id=naming_with_sbd("mode-selection"),
                    labelStyle={'display': 'inline-block', 'marginRight': '15px', 'fontSize': '14px'},
                    inputStyle={"marginRight": "5px"},
                    className="mb-4"
                )
            ),

            dbc.Button(
                [html.I(className="bi bi-lightning-fill me-2"), "Xây kịch bản"], 
                id=naming_with_sbd("analysis"), 
                color="success", className="w-100 shadow fw-bold py-2"
            ),
        ])
    ], className="shadow-sm border-0")
], className="sticky-top", style={"top": "1rem"}) 



right_layout = dbc.Card([
    dbc.CardHeader("Phân tích dữ liệu & Phổ điểm 2025", className="fw-bold bg-white text-primary"),
    dbc.CardBody([
        dcc.Loading(
            id=naming_with_sbd("loading-analysis"),
            type="circle",
            children=html.Div(
                id=naming_with_sbd("full-div"), 
                style={"minHeight": "500px"}
            ),
            color="#3498db"
        )
    ])
], className="shadow-sm border-0 h-100")



layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            left_layout, 
            width=12, 
            md=4, 
            className="mb-4 p-1"
        ),
        dbc.Col(
            right_layout, 
            width=12, 
            md=8, 
            className="p-1"
        )
    ], className="mt-4 g-4")
], fluid=True, className="p-0 px-3 px-md-5 pb-5 bg-light")





# ----------------------------------------------------------------------------------------
# CALLBACK
# ----------------------------------------------------------------------------------------
@callback(
    Output(naming_with_sbd("sbd"), "invalid"),
    Output(naming_with_sbd("sbd-feedback"), "children"),
    Input(naming_with_sbd("sbd"), "value")
)
def validate_sbd(val):
    """Xác thực định dạng số báo danh theo quy định của Bộ Giáo dục.

    Kiểm tra tính hợp lệ của SBD dựa trên mã tỉnh và cấu trúc chuỗi số. 
    Hỗ trợ hiển thị cảnh báo trực quan trên giao diện khi người dùng nhập sai.

    Args:
        val (str): Chuỗi số báo danh người dùng nhập vào.

    Returns:
        tuple: (Trạng thái invalid (bool), Thông điệp phản hồi (str)).
    """
    if not val: 
        return False, ""
    
    if not val.isdigit():
        return True, "❌ Chỉ được nhập số!"
    
    if len(val) < 8:
        return False, ""
    
    ma_tinh = int(val[:2])
    stt = int(val[2:])
    
    if not ((1 <= ma_tinh <= 19) or (21 <= ma_tinh <= 65)):
        return True, f"❌ Mã tỉnh {ma_tinh} không tồn tại!"
    
    if stt == 0:
        return True, f"❌ Số báo danh không tồn tại"
    
    return False, ""





@callback(
    [
        Output(naming_with_sbd("comb"), "options"),
        Output(naming_with_sbd("comb"), "value"),
        Output(naming_with_sbd("comb"), "style"),
        Output(naming_with_sbd("status-output-2"), "children"),
    ],
    [
        Input(naming_with_sbd("search-info"), "n_clicks")
    ],
    [
        State(naming_with_sbd("sbd"), "value"),
        State(naming_with_sbd("year"), "value")
    ],
    prevent_initial_call=True
)
def get_comb(n, sbd, year):
    """Truy vấn các tổ hợp môn xét tuyển hợp lệ từ cơ sở dữ liệu.

    Hàm thực hiện lọc dữ liệu theo SBD và Năm, sau đó thực hiện Left-Join với danh mục 
    TO_HOP để lấy tên đầy đủ của các khối xét tuyển mà thí sinh có đủ điều kiện.

    Args:
        n (int): Số lần nhấn nút tìm kiếm.
        sbd (str): Số báo danh cần truy vấn.
        year (int): Năm thi tương ứng với bảng dữ liệu.

    Returns:
        tuple: (Danh sách options, Giá trị mặc định, Style hiển thị, Thông báo trạng thái).
    """
    if not n or not sbd or not year:
        return [], None, {"display": "block"}, ""
    
    sbd_str = str(sbd).strip()
    year_int = int(year)

    STYLE_HIDDEN = {"display": "none"}
    STYLE_SHOW = {"display": "block"}

    if year_int not in BANG_DIEM:
        return [], None, STYLE_HIDDEN, [dbc.Alert("Dữ liệu năm này chưa có!", color="warning")]

    df_all = BANG_DIEM[year_int].filter(pl.col("SOBAODANH") == sbd_str).collect()

    # TRƯỜNG HỢP 1: Không tìm thấy SBD
    if df_all.is_empty():
        return [], None, STYLE_HIDDEN, [
            dbc.Alert(f"Không tìm thấy SBD {sbd_str}!", color="danger")
        ]

    # TRƯỜNG HỢP 2: Hợp lệ = False
    df_valid = df_all.filter(pl.col("Hợp lệ") == True)
    
    if df_valid.is_empty():
        return [], None, STYLE_HIDDEN, [
            dbc.Alert("Thông tin xét tuyển không khả dụng", color="warning", className="mb-1"),
            html.Small(
                "Lý do: Không tìm thấy dữ liệu tổ hợp hợp lệ (có thể do thiếu điểm môn thành phần hoặc chưa đủ điều kiện xét công nhận tốt nghiệp).", 
                className="text-muted"
            )
        ]

    # TRƯỜNG HỢP 3: Thành công
    final_df = (
        df_valid.lazy()
        .join(TO_HOP, on="Tổ hợp", how="left")
        .select(["Tổ hợp", "Tên tổ hợp"])
        .sort("Tổ hợp")
        .collect()
    )

    options = [
        {"label": row["Tên tổ hợp"], "value": row["Tổ hợp"]} 
        for row in final_df.to_dicts()
    ]
    
    first_value = options[0]["value"] if options else None
    
    return options, first_value, STYLE_SHOW, ""





@callback(
    Output(naming_with_sbd("search-info"), "disabled"),
    [
        Input(naming_with_sbd("sbd"), "value"),
        Input(naming_with_sbd("year"), "value")
    ]
)
def disable_button(sbd, year):
    """Kiểm soát trạng thái kích hoạt của nút truy vấn dữ liệu.

    Đảm bảo người dùng chỉ có thể nhấn nút khi đã nhập đủ thông tin cơ bản 
    và thông tin đó vượt qua các kiểm tra định dạng sơ bộ.

    Args:
        sbd (str): Số báo danh hiện tại trong ô nhập liệu.
        year (int): Năm thi đang được chọn.

    Returns:
        bool: Trạng thái vô hiệu hóa (True nếu chưa hợp lệ).
    """
    # Kiểm tra có cái gì nhập không
    if not sbd or not year:
        return True
    
    if len(sbd) != 8:
        return True

    # Kiểm tra năm
    if year < 2025:
        return True
    
    # Kiểm tra SBD
    ma_tinh = int(sbd[:2])
    stt = int(sbd[2:])
    if not (1 <= ma_tinh <= 19 or 21 <= ma_tinh <= 65) or (stt == 0):
        return True 
    
    return False





@callback(
    Output(naming_with_sbd("score"), "children"),
    [
        Input(naming_with_sbd("comb"), "value")
    ],
    [
        State(naming_with_sbd("sbd"), "value"),
        State(naming_with_sbd("year"), "value")
    ],
    prevent_initial_call=True
)
def update_score_display(selected_comb, sbd, year):
    """Truy xuất và hiển thị tổng điểm của tổ hợp môn được chọn.

    Dựa trên tổ hợp thí sinh chọn từ Dropdown, hàm sẽ lọc chính xác dòng dữ liệu 
    tương ứng để lấy ra 'Tổng điểm' đã được tính toán sẵn.

    Args:
        selected_comb (str): Mã tổ hợp (ví dụ: 'A00', 'B00').
        sbd (str): Số báo danh của thí sinh.
        year (int): Năm thi cần truy vấn.

    Returns:
        str: Chuỗi hiển thị điểm số (định dạng 2 chữ số thập phân).
    """
    # 1. Kiểm tra điều kiện đầu vào
    if not selected_comb or not sbd or not year:
        return "---"

    try:
        sbd_str = str(sbd).strip()
        year_int = int(year)

        # 2. Truy vấn lấy điểm của đúng tổ hợp đã chọn
        df_score = (
            BANG_DIEM[year_int]
            .filter(
                (pl.col("SOBAODANH") == sbd_str) & 
                (pl.col("Tổ hợp") == selected_comb)
            )
            .select("Tổng điểm")
            .collect()
        )

        if df_score.is_empty():
            return "Không tìm thấy điểm"

        # 3. Lấy giá trị điểm
        score_val = df_score.item()
        
        return f"{score_val:.2f} điểm"

    except Exception as e:
        print(f"Lỗi khi lấy điểm: {e}")
        return "Lỗi dữ liệu"





@callback(
    Output(naming_with_sbd("choosing-combs"), "children"),
    Input(naming_with_sbd("comb"), "value")
)
def choosing_combs(comb):
    """Tạo linh kiện Dropdown đa chọn để so sánh các tổ hợp khác.

    Khởi tạo danh sách tất cả các tổ hợp môn hiện có trong hệ thống, 
    mặc định chọn sẵn tổ hợp chính của thí sinh.

    Args:
        comb (str): Tổ hợp gốc của thí sinh được tìm thấy từ SBD.

    Returns:
        dcc.Dropdown: Linh kiện Dropdown đa chọn của Dash.
    """
    if not comb:
        return None
    
    return make_persistent(
        dcc.Dropdown(
            options = [
                {
                    "label": row["Tên tổ hợp"], 
                    "value": row["Tổ hợp"]
                } 
                for row in TO_HOP.collect().to_dicts()
            ],
            value=[comb],
            multi=True,
            clearable=True,
            id = naming_with_sbd("combs-script"),   
        )
    )





@callback(
    Output(naming_with_sbd("combs-script"), "value"),
    Input(naming_with_sbd("combs-script"), "value"),
    State(naming_with_sbd("comb"), "value"),
    prevent_initial_call=True
)
def protect_original_comb(selected_values, original_comb):
    """Ngăn chặn việc xóa tổ hợp gốc khỏi danh sách phân tích.

    Đây là ràng buộc nghiệp vụ nhằm đảm bảo báo cáo phân tích luôn chứa 
    tổ hợp mục tiêu chính của thí sinh.

    Args:
        selected_values (list): Danh sách các mã tổ hợp đang được chọn.
        original_comb (str): Tổ hợp bắt buộc phải hiện diện.

    Returns:
        list: Danh sách tổ hợp đã được chuẩn hóa (luôn chứa original_comb).
    """
    if not selected_values or original_comb not in selected_values:
        if not selected_values:
            return [original_comb]
        return [original_comb] + selected_values
    
    return selected_values





# Về điểm, min = 15, max = max(30, điểm người ta), nếu điểm < 15 thì báo lỗi
@callback(
    [
        Output(naming_with_sbd("choosing-score"), "children")
    ],
    Input(naming_with_sbd("score"), "children")
)
def choosing_floor_score(score_text):
    """Khởi tạo thanh trượt (Slider) chọn ngưỡng điểm sàn dự kiến.

    Giới hạn phạm vi của Slider từ mức sàn tối thiểu (15đ) đến mức điểm 
    thực tế của thí sinh để đảm bảo tính thực tế của báo cáo phân tích.

    Args:
        score_text (str): Văn bản hiển thị điểm số từ callback trước.

    Returns:
        list: Danh sách chứa linh kiện dcc.Slider hoặc Alert cảnh báo.
    """
    if not isinstance(score_text, str) or not score_text or not score_text[0].isdigit():
        return [None]
    
    parts = score_text.split()
    score_val = float(parts[0])
    
    if score_val < 15:
        return [
            dbc.Alert(
                "Điểm sàn tối thiểu từ 15.00 trở lên", 
                color="warning", 
                className="p-2 small"
            )
        ]

    max_val = min(30, score_val)

    # Bọc cái Component vào trong List
    return [
        make_persistent(
            dcc.Slider(
                id=naming_with_sbd("floor-score-slider"),
                min=15,
                max=max_val,
                step=0.1,
                value=15,
                marks={i: str(i) for i in range(15, int(max_val) + 1, 3)},
                tooltip={"always_visible": True, "placement": "bottom"}
            )
    )]





@callback(
    Output(naming_with_sbd("analysis"), "disabled"),
    [
        Input(naming_with_sbd("score"), "children"),
        Input(naming_with_sbd("choosing-combs"), "children"),
    ]
)
def toggle_analysis_button(score_text, combs_dropdown):
    
    if not score_text or score_text in ["---", "Không tìm thấy điểm"] or not combs_dropdown:
        return True
    
    return False





@callback(
    Output(naming_with_sbd("full-div"), "children"),
    Input(naming_with_sbd("analysis"), "n_clicks"),
    [
        State(naming_with_sbd("score"), "children"),
        State(naming_with_sbd("year"), "value"),
        State(naming_with_sbd("floor-score-slider"), "value"),
        State(naming_with_sbd("combs-script"), "value"),
        State(naming_with_sbd("mode-selection"), "value")
    ],
    prevent_initial_call=True
)
def analysis_callback(n, score_text, year, floor_score, combs, mode):
    """Điều phối và hiển thị kết quả phân tích đồ thị và bảng phổ điểm.

    Là callback trung tâm thực hiện chuyển đổi dữ liệu từ giao diện người dùng 
    vào hàm xử lý logic `display_graph_and_table`.

    Args:
        n (int): Trạng thái nhấn nút phân tích.
        score_text (str): Điểm của thí sinh (dạng text).
        year (int): Năm cần phân tích.
        floor_score (float): Ngưỡng điểm sàn dự kiến.
        combs (list): Danh sách các tổ hợp cần đưa vào so sánh.
        mode (str): Chế độ quy đổi điểm (raw, z-score, robust).

    Returns:
        dash.html.Div: Container chứa đồ thị và bảng dữ liệu chi tiết.
    """
    if not n or not score_text or not mode:
        return None
    
    try:
        score_val = float(score_text.split()[0])
        
        return display_graph_and_table(
            year=int(year),
            self_score=score_val,
            floor_score=float(floor_score),
            combs=combs,
            mode=mode
        )
    except Exception as e:
        print(f"Lỗi Callback: {e}")
        return dbc.Alert(f"Đã có lỗi xảy ra: {str(e)}", color="danger")





