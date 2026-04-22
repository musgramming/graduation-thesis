from dash import callback, html, register_page, dcc, Input, Output, State, MATCH, dash_table, no_update
from dash import callback_context as ctx
import dash_bootstrap_components as dbc
import polars as pl
from data import TO_HOP, BANG_CHON_MON
from utils.build_script import display_graph_and_table
from utils.naming import naming_without_sbd



register_page(
    __name__,
    path="/dss_without_sbd",
    redirect_from=["/dss-without-sbd"],
    title="Xây dựng kịch bản",
    description="Trang này cho phép nhập điểm của mình để tính toán kịch bản cho hợp lý"
)



def input_num(id : str, **kwargs):
    """
    Tạo ô nhập liệu cho số
    """
    return dbc.Input(
        id = naming_without_sbd(id),
        type = "number",
        min = 0,
        max = 10,
        value = 0,
        **kwargs
    )




left_layout = html.Div([
    # Chỗ cho nhập điểm
    dbc.Card([
        dbc.CardHeader(
            html.H3("Nhập điểm dự kiến của bạn")
        ),
        dbc.CardBody([
            dbc.Container([
                # Nhập năm
                html.Label("Nhập năm"),
                dbc.Input(
                    id = naming_without_sbd("year"),
                    type = "number",
                    min = 2025, 
                    max = 2025,
                    value = 2025
                )
            ]),

            dbc.Container([
                # Hàng cho môn Toán
                dbc.Row([
                    dbc.Col(html.Label("Toán"), width=6),
                    dbc.Col(input_num("math"), width=6),
                ], className="mb-2"),
                
                # Hàng cho môn Văn
                dbc.Row([
                    dbc.Col(html.Label("Văn"), width=6),
                    dbc.Col(input_num("literature"), width=6),
                ], className="mb-2"),

                # Hàng cho môn tự chọn 1
                dbc.Row([
                    dbc.Col(dcc.Dropdown(options=BANG_CHON_MON, value="Lý", id=naming_without_sbd("mon-1")), width=6),
                    dbc.Col(input_num("diem-mon-1"), width=6),
                ], className="mb-2"),

                # Hàng cho môn tự chọn 2
                dbc.Row([
                    dbc.Col(dcc.Dropdown(id = naming_without_sbd("mon-2")), width=6),
                    dbc.Col(input_num("diem-mon-2"), width=6),
                ], className="mb-2"),
            ]),

            html.Div(
                dbc.Button(
                    children = "Tính toán điểm tổ hợp",
                    id = naming_without_sbd("build-combs")
                )
            )
        ])  
    ]),


    html.Br(),
    html.Div(id = naming_without_sbd("error")),
    html.Br(),

    ## Xây dựng kịch bản
    dbc.Card([
        dbc.CardHeader(
            html.H4("Xây dựng kịch bản")
        ),

        dbc.CardBody([
            dbc.Container([
                # Chọn tổ hợp
                dbc.Row([
                    dbc.Col("Tổ hợp khả dĩ: ", width = 5),
                    dbc.Col(
                        dcc.Dropdown(id = naming_without_sbd("your-comb")), width = 7
                    )
                ]),

                # Show điểm tổ hợp
                dbc.Row([
                    dbc.Col("Điểm tổ hợp: ", width = 5),
                    dbc.Col(
                        dbc.Input(
                            id=naming_without_sbd("your-score"),
                            readonly=True, # Người dùng chỉ xem, không sửa được
                            plaintext=False, # Để False nếu muốn nó có khung như ô Input
                            className="bg-light"
                        ), width = 7
                    )
                ]),

                dcc.Store(id=naming_without_sbd("stored-results")),

                # Chọn điểm sàn
                dbc.Row([
                    dbc.Col([
                        html.Label("Điểm sàn: "),
                        dbc.Input(
                            id=naming_without_sbd("floor-score-input"), 
                            type="number", 
                            step=0.05,
                            style={"width": "100px", "display": "inline-block", "marginLeft": "10px"}
                        )
                    ], width=5),
                    dbc.Col([
                        dcc.Slider(
                            id=naming_without_sbd("floor-score"),
                            min=15,
                            step=0.05, # Để khớp với độ chi tiết của điểm thi
                            marks={i: str(i) for i in range(15, 31, 3)},
                            tooltip={"always_visible": False, "placement": "bottom"}
                        )
                    ], width=7)
                ], className="mb-4"),

                # Danh sách tổ hợp
                dbc.Row([
                    dbc.Col("Danh sách tổ hợp", width = 5),
                    dbc.Col(
                        html.Div(id=naming_without_sbd("combs-list-container"))
                    )
                ]),

                html.Div(
                    dbc.Button(
                        "Chạy kịch bản phân tích",
                        id=naming_without_sbd("run-scenario"),
                        color="success",
                        className="w-100"
                    )
                )
            ])
        ])
    ], id = naming_without_sbd("scenario"), style={"display": "none"})
])



right_layout = html.Div(id=naming_without_sbd("right-content"))



layout = dbc.Container([
    dbc.Row([
        dbc.Col(left_layout, align = "center", width = 4),
        dbc.Col(right_layout, align = "center", width = 8)
    ])
])






# ------------------------------------------------------------------
#                              CALLBACK 
# ------------------------------------------------------------------

# CALLBACK 1: Khi chọn môn 1 thì môn 2 không trùng môn 1
@callback(
    [
        Output(naming_without_sbd("mon-2"), "options"),
        Output(naming_without_sbd("mon-2"), "value")
    ],
    [
        Input(naming_without_sbd("mon-1"), "value")        
    ]
)
def choose_mon_2(mon_1 : str):
    options = [col for col in BANG_CHON_MON if col["value"] != mon_1]
    return options, options[0]["value"]





# CALLBACK 2: Khi chưa nhấn nút tính điểm tổ hợp
@callback(
    Output(naming_without_sbd("build-combs"), "disabled"), # Tác động vào thuộc tính disabled
    [
        Input(naming_without_sbd("math"), "value"),        # Sửa thành math cho khớp với id ở layout
        Input(naming_without_sbd("literature"), "value"),  # Sửa thành literature cho khớp
        Input(naming_without_sbd("diem-mon-1"), "value"),
        Input(naming_without_sbd("diem-mon-2"), "value")
    ]
)
def validate_btn(toan, van, mon_1, mon_2):
    # Nếu bất kỳ ô nào trống (None)
    if any(s is None for s in [toan, van, mon_1, mon_2]):
        return True
    
    # Kiểm tra điểm ngoài khoảng 0-10
    if any(not (0 <= s <= 10) for s in [toan, van, mon_1, mon_2]) or any(s <= 1 for s in [toan, van, mon_1, mon_2]):
        return True

    return False # Mở nút cho phép bấm





# CALLBACK 3: Activate chỗ cho phép nhập thông số

@callback(
    [
        Output(naming_without_sbd("scenario"), "style"),
        Output(naming_without_sbd("error"), "children"),
        Output(naming_without_sbd("your-comb"), "options"),
        Output(naming_without_sbd("your-comb"), "value"),
        Output(naming_without_sbd("stored-results"), "data"), # Lưu toàn bộ dict vào đây
    ],
    Input(naming_without_sbd("build-combs"), "n_clicks"),
    [
        State(naming_without_sbd("math"), "value"),
        State(naming_without_sbd("literature"), "value"),
        State(naming_without_sbd("mon-1"), "value"),
        State(naming_without_sbd("diem-mon-1"), "value"),
        State(naming_without_sbd("mon-2"), "value"),
        State(naming_without_sbd("diem-mon-2"), "value")
    ],
    prevent_initial_call=True
)
def calculate_and_store(n_clicks, toan, van, mon_1, diem_mon_1, mon_2, diem_mon_2):
    if not n_clicks:
        return {"display": "none"}, None, [], None, None

    # 1. Kiểm tra điểm liệt
    user_map = {
        "Toán": float(toan or 0), 
        "Văn": float(van or 0), 
        mon_1: float(diem_mon_1 or 0), 
        mon_2: float(diem_mon_2 or 0)
    }
    if any(s <= 1 for s in user_map.values()):
        return {"display": "none"}, dbc.Alert("Phát hiện điểm liệt (<= 1)!", color="danger"), [], None, None

    # 2. Xử lý LazyFrame
    list_mon = list(user_map.keys())

    try:
        results = (
            TO_HOP
            .with_columns([
                # Gom 3 cột môn của 1 tổ hợp thành 1 danh sách (List)
                pl.concat_list(["Môn 1", "Môn 2", "Môn 3"]).alias("mon_set")
            ])
            .filter(
                # KIỂM TRA TẬP CON: Tất cả môn trong tổ hợp phải nằm trong túi điểm của Mus
                pl.col("mon_set").list.eval(pl.element().is_in(list_mon)).list.all()
            )
            .with_columns([
                # Tính điểm dựa trên mapping user_map
                (pl.col("Môn 1").replace(user_map).cast(pl.Float64) +
                 pl.col("Môn 2").replace(user_map).cast(pl.Float64) +
                 pl.col("Môn 3").replace(user_map).cast(pl.Float64)).alias("score")
            ])
            .filter(pl.col("score") >= 15) # Lọc điểm sàn cơ bản
            .collect()
        )
    except Exception as e:
        return {"display": "none"}, html.P(f"Lỗi: {e}"), [], None, None

    if results.height == 0:
        return {"display": "none"}, dbc.Alert("Không có tổ hợp >= 15đ", color="warning"), [], None, None

    # 3. Chuyển kết quả thành list dict để lưu vào Store
    data_to_store = results.to_dicts()

    # Tận dụng cột "Tên tổ hợp" Mus đã tạo sẵn ở file data.py để làm label
    options = [
        {
            "label": r["Tên tổ hợp"], # Label sẽ là: A01 (Toán, Lí, Anh)
            "value": r["Tổ hợp"]      # Value vẫn giữ là mã gốc (A01) để các logic sau không bị gãy
        } 
        for r in data_to_store
    ]
    
    return {"display": "block"}, None, options, options[0]["value"], data_to_store





# CALLBACK 4: Phản hồi tức thì

@callback(
    Output(naming_without_sbd("your-score"), "value"), # ĐỔI ĐÂY
    Input(naming_without_sbd("your-comb"), "value"),
    State(naming_without_sbd("stored-results"), "data"),
    prevent_initial_call=True
)
def update_score_display(selected_comb, stored_data):
    if not selected_comb or not stored_data:
        return ""
    
    # Tra cứu trong data đã store (không cần đụng tới Polars nữa)
    for item in stored_data:
        if item["Tổ hợp"] == selected_comb:
            return f"{item['score']:.2f} điểm"
    return "N/A"





@callback(
    Output(naming_without_sbd("combs-list-container"), "children"),
    Input(naming_without_sbd("your-comb"), "value"),
    State(naming_without_sbd("stored-results"), "data"),
    prevent_initial_call=True
)
def render_scenario_dropdown(main_comb, stored_data):
    if not main_comb or not stored_data:
        return None
    
    options = [{"label": item["Tên tổ hợp"], "value": item["Tổ hợp"]} for item in TO_HOP.collect().to_dicts()]
    
    return dcc.Dropdown(
        options=options,
        value=[main_comb],
        multi=True,
        clearable=True,
        id=naming_without_sbd("combs-list"), 
    )





# CALLBACK 5B: Bảo vệ tổ hợp gốc
@callback(
    Output(naming_without_sbd("combs-list"), "value"),
    Input(naming_without_sbd("combs-list"), "value"),
    State(naming_without_sbd("your-comb"), "value"),
    prevent_initial_call=True
)
def protect_original_comb_logic(selected_values, original_comb):
    if not selected_values or original_comb not in selected_values:
        if not selected_values:
            return [original_comb]
        
        return [original_comb] + selected_values
    
    return selected_values



# CALLBACK 6: Tính toán điểm sàn với ngưỡng:
# min = max(15, điểm sàn)
# max = min(30, điểm sàn)
@callback(
    [
        Output(naming_without_sbd("floor-score"), "max"),
        Output(naming_without_sbd("floor-score"), "value"),
        Output(naming_without_sbd("floor-score-input"), "max"),
        Output(naming_without_sbd("floor-score-input"), "value"),
    ],
    Input(naming_without_sbd("your-score"), "value"),
    prevent_initial_call=True
)
def update_slider_limits(score_text):
    if not score_text:
        return 30, 15, 30, 15
    
    try:
        current_score = float(score_text.split()[0])
        new_max = min(current_score, 30.0)
    except:
        new_max = 30.0

    return new_max, 15.0, new_max, 15.0





# CALLBACK 7: Đồng bộ 2 chiều giữa Slider điểm sàn và Input điểm sàn
@callback(
    [
        Output(naming_without_sbd("floor-score"), "value", allow_duplicate=True),
        Output(naming_without_sbd("floor-score-input"), "value", allow_duplicate=True)
    ],
    [
        Input(naming_without_sbd("floor-score"), "value"),
        Input(naming_without_sbd("floor-score-input"), "value")
    ],
    prevent_initial_call=True
)
def sync_slider_and_input(slider_val, input_val):
    triggered_id = ctx.triggered_id
    
    # Nếu đang kéo Slider -> cập nhật Input
    if triggered_id == naming_without_sbd("floor-score"):
        return no_update, slider_val
    
    # Nếu đang gõ Input -> cập nhật Slider
    if triggered_id == naming_without_sbd("floor-score-input"):
        return input_val, no_update
        
    return no_update, no_update




# CALLBACK chính: 
@callback(
    Output(naming_without_sbd("right-content"), "children"),
    Input(naming_without_sbd("run-scenario"), "n_clicks"), # Lắng nghe nút mới
    [
        State(naming_without_sbd("your-score"), "value"),
        State(naming_without_sbd("year"), "value"),
        State(naming_without_sbd("floor-score"), "value"), # Lúc này Slider trả về số thực
        State(naming_without_sbd("combs-list"), "value"),
        State(naming_without_sbd("stored-results"), "data")
    ],
    prevent_initial_call=True
)
def display_analysis_without_sbd(n, main_score_text, year, floor_score, selected_combs, stored_data):
    # Nếu chưa bấm nút hoặc chưa có dữ liệu thì không làm gì
    if not n or not main_score_text or not selected_combs:
        return no_update

    try:
        # Xử lý lấy điểm số thực tế từ chuỗi "27.50 điểm"
        score_val = float(main_score_text.split()[0])
        
        # floor_score giờ là giá trị từ Slider (float)
        f_score = float(floor_score)

        return display_graph_and_table(
            year=int(year),
            self_score=score_val,
            floor_score=f_score,
            combs=selected_combs,
            mode="raw-score"
        )
    except Exception as e:
        return dbc.Alert(f"Lỗi: {str(e)}", color="danger")    


