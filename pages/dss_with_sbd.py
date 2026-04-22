from dash import callback, html, register_page, dcc, Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import polars as pl
from data import BANG_DIEM, TO_HOP
from utils.build_script import display_graph_and_table
from utils.naming import naming_with_sbd



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
    dbc.Card([
        dbc.CardHeader("Kết quả thi THPTQG của bạn"),
        dbc.CardBody([
            # SBD
            dbc.Row([
                dbc.Label("Số báo danh", width=4),
                dbc.Col([
                    dbc.Input(id=naming_with_sbd("sbd"), type="text", minlength=8, maxlength=8, placeholder="VD: 01000001"),
                    dbc.FormFeedback(id=naming_with_sbd("sbd-feedback"), type="invalid"),
                ], width=8),
            ], className="mb-3 align-items-center"),


            # Năm thi
            dbc.Row([
                dbc.Label("Năm thi", width=4),
                dbc.Col(
                    dbc.Input(id=naming_with_sbd("year"), type="number", min=2025, max=2025, value=2025),
                    width=8
                ),
            ], className="mb-3 align-items-center"),


            # Nút bấm để tính thông tin về tổ hợp đó
            html.Div(
                dbc.Button(
                    "Tra cứu", 
                    id=naming_with_sbd("search-info"), 
                    color="primary",
                    className="px-4" # Thêm chút padding ngang cho nút cân đối
                ),
                className="d-flex justify-content-center mb-3" # Căn giữa nút hoàn hảo
            ),


            # Tổ hợp
            dbc.Row([
                dbc.Label("Tổ hợp", width=4),
                dbc.Col([
                    dcc.Dropdown(id=naming_with_sbd("comb"), placeholder="Chọn tổ hợp xét tuyển"),
                    html.Div(id = naming_with_sbd("status-output-2"))
                ]),
            ], className="mb-3"),


            # Điểm tổ hợp display
            dbc.Row([
                dbc.Label("Điểm", width=4),
                dbc.Col(
                    html.Div(id=naming_with_sbd("score"), className="fw-bold text-primary")
                )
            ]),


            html.Div(id=naming_with_sbd("status-output"), className="mt-3")
        ]),
    ]),


    html.Hr(),


    dbc.Card([
        dbc.CardHeader("Xây dựng kịch bản"),
        dbc.CardBody([
            dbc.Row([
                dbc.Label("Chọn danh sách tổ hợp", width = 4),
                dbc.Col([
                    html.Div(id=naming_with_sbd("choosing-combs"), className="fw-bold text-primary")
                ])
            ]),

            dbc.Row([
                dbc.Label("Chọn điểm sàn", width = 4),
                dbc.Col([
                    html.Div(id=naming_with_sbd("choosing-score"), className="fw-bold text-primary")
                ])
            ]),

            # Selection để xây dựng kịch bản, bao gồm
            # - Điểm thô
            # - Min-max
            # - Z-score
            # - PCT - Percentile Rank
            # - Percentile Equating
            html.Div([
                html.Label("Chọn phương pháp quy đổi: ", className="fw-bold"),
                dcc.RadioItems(
                    options=[
                        {"label": " Điểm thô", "value": "raw-score"},
                        {"label": " Min-Max", "value": "min-max"},
                        {"label": " Z-Score", "value": "z-score"},
                        {"label": " Robust", "value": "robust"}
                    ],
                    value="raw-score", # Mặc định chọn 1 cái, không để trong ngoặc vuông
                    id=naming_with_sbd("mode-selection"),
                    labelStyle={'display': 'block', 'marginBottom': '5px'}, # Hiển thị theo hàng dọc cho đẹp
                    inputStyle={"marginRight": "10px"} # Cách cái chữ ra một chút
                )
            ], className="mb-3"),

            # Nút bấm để tính thông tin về tổ hợp đó
            html.Div(
                dbc.Button(
                    "Xây kịch bản", 
                    id=naming_with_sbd("analysis"), 
                    color="primary",
                    className="px-4" # Thêm chút padding ngang cho nút cân đối
                ),
                className="d-flex justify-content-center mb-3" # Căn giữa nút hoàn hảo
            ),
        ])
    ], className="shadow-sm")
])


right_layout = dcc.Loading(
    id=naming_with_sbd("loading-analysis"),
    type="graph",
    children=html.Div(id=naming_with_sbd("full-div")),
    color="#3498db"
)


layout = dbc.Container([
    dbc.Row([
        dbc.Col(left_layout, width=12, md=4),
        dbc.Col(right_layout, width=12, md=8)
    ], className="mt-4")
], fluid=True, className="pb-5")





# ----------------------------------------------------------------------------------------
# CALLBACK
# ----------------------------------------------------------------------------------------
@callback(
    Output(naming_with_sbd("sbd"), "invalid"),
    Output(naming_with_sbd("sbd-feedback"), "children"),
    Input(naming_with_sbd("sbd"), "value")
)
def validate_sbd(val):
    if not val: return False, ""
    
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





# Lấy thông tin về tổ hợp
# Input:
# - SBD - naming_with_sbd("sbd")
# - Năm - naming_with_sbd("year")
# Output:
# - Danh sách tổ hợp khả dĩ - naming_with_sbd("comb")
@callback(
    [
        Output(naming_with_sbd("comb"), "options"),
        Output(naming_with_sbd("comb"), "value"),
        Output(naming_with_sbd("comb"), "style"), # Thay disabled bằng style
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
    
    # Trả về: options, giá trị mặc định, hiện dropdown, và xóa thông báo lỗi
    return options, first_value, STYLE_SHOW, ""





# Vô hiệu hóa nút bấm khi nhập chưa xong
@callback(
    Output(naming_with_sbd("search-info"), "disabled")
    ,
    [
        Input(naming_with_sbd("sbd"), "value"),
        Input(naming_with_sbd("year"), "value")
    ]
)
def disable_button(sbd, year):
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





# Lấy thông tin về điểm tổ hợp
# Input:
# - SBD - naming_with_sbd("sbd")
# - Năm - naming_with_sbd("year")
# - Tổ hợp khả dĩ - naming_with_sbd("comb")
# Output:
# - Danh sách tổ hợp khả dĩ - naming_with_sbd("score")
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
    # 1. Kiểm tra điều kiện đầu vào
    if not selected_comb or not sbd or not year:
        return "---"

    try:
        sbd_str = str(sbd).strip()
        year_int = int(year)

        # 2. Truy vấn lấy điểm của đúng tổ hợp đã chọn
        # Vì dữ liệu mỗi dòng là 1 tổ hợp, ta filter theo cả SBD và Tổ hợp
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
        
        # Trả về chuỗi định dạng đẹp để hiển thị vào html.Div
        return f"{score_val:.2f} điểm"

    except Exception as e:
        print(f"Lỗi khi lấy điểm: {e}")
        return "Lỗi dữ liệu"





# Chọn tổ hợp
# Input 
# - Tổ hợp của bạn đó (comb)
# Output
# - Danh sách tổ hợp (comb của bạn ấy luôn được chọn) - choosing-combs (Trả về dưới dạng dropdown)
@callback(
    Output(naming_with_sbd("choosing-combs"), "children"),
    Input(naming_with_sbd("comb"), "value")
)
def choosing_combs(comb):
    if not comb:
        return None
    
    return dcc.Dropdown(
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





# Khi xóa danh sách tổ hợp, trừ comb ban đầu thì còn lại bị xóa
@callback(
    Output(naming_with_sbd("combs-script"), "value"),
    Input(naming_with_sbd("combs-script"), "value"),
    State(naming_with_sbd("comb"), "value"),
    prevent_initial_call=True
)
def protect_original_comb(selected_values, original_comb):
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
    if not isinstance(score_text, str) or not score_text or not score_text[0].isdigit():
        return [None] # Trả về list chứa None
    
    parts = score_text.split()
    score_val = float(parts[0])
    
    if score_val < 15:
        return [dbc.Alert("Điểm sàn tối thiểu từ 15.00 trở lên", color="warning", className="p-2 small")]

    max_val = min(30, score_val)

    # Bọc cái Component vào trong List
    return [dcc.Slider(
        id=naming_with_sbd("floor-score-slider"),
        min=15,
        max=max_val,
        step=0.1,
        value=15,
        marks={i: str(i) for i in range(15, int(max_val) + 1, 3)},
        tooltip={"always_visible": True, "placement": "bottom"}
    )]





@callback(
    Output(naming_with_sbd("analysis"), "disabled"),
    [
        Input(naming_with_sbd("score"), "children"),
        Input(naming_with_sbd("choosing-combs"), "children"), # Kiểm tra xem Dropdown chọn khối đã hiện chưa
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
        State(naming_with_sbd("mode-selection"), "value") # Bây giờ 'mode' sẽ là string trực tiếp
    ],
    prevent_initial_call=True
)
def analysis_callback(n, score_text, year, floor_score, combs, mode):
    if not n or not score_text or not mode:
        return None
    
    try:
        # Tách lấy phần số từ chuỗi "27.50 điểm"
        score_val = float(score_text.split()[0])
        
        # Gọi hàm xử lý đồ thị
        return display_graph_and_table(
            year=int(year),
            self_score=score_val,
            floor_score=float(floor_score),
            combs=combs,
            mode=mode # Truyền trực tiếp vì RadioItems trả về string
        )
    except Exception as e:
        print(f"Lỗi Callback: {e}")
        return dbc.Alert(f"Đã có lỗi xảy ra: {str(e)}", color="danger")





