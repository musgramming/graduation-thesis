import random
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
        min = 0, max = 10, value = 0,
        step = 0.01,
        className = "text-center shadow-sm border-primary-subtle",
        **kwargs
    )




left_layout = html.Div([
    # BƯỚC 1: NHẬP ĐIỂM
    dbc.Card([
        dbc.CardHeader(
            html.Div([html.I(className="bi bi-pencil-fill me-2"), "Điểm dự kiến của bạn"]),
            className="fw-bold bg-primary text-white"
        ),
        dbc.CardBody([
            # Năm xét tuyển (Làm gọn)
            dbc.Row([
                dbc.Label("Năm xét tuyển", width=6, className="small fw-bold"),
                dbc.Col(
                    dbc.Input(id=naming_without_sbd("year"), type="number", min=2025, max=2025, value=2025, className="text-center"), 
                    width=6
                ),
            ], className="mb-3 g-2 align-items-center"),

            html.Hr(className="my-3"),

            # Khu vực nhập điểm
            html.Div([
                dbc.Row([
                    dbc.Col(html.Label("Toán", className="fw-bold mb-0"), width=6),
                    dbc.Col(input_num("math"), width=6),
                ], className="mb-2 align-items-center"),
                
                dbc.Row([
                    dbc.Col(html.Label("Văn", className="fw-bold mb-0"), width=6),
                    dbc.Col(input_num("literature"), width=6),
                ], className="mb-2 align-items-center"),

                dbc.Row([
                    dbc.Col(dcc.Dropdown(options=BANG_CHON_MON, value="Lý", id=naming_without_sbd("mon-1"), clearable=False), width=6),
                    dbc.Col(input_num("diem-mon-1"), width=6),
                ], className="mb-2 align-items-center"),

                dbc.Row([
                    dbc.Col(dcc.Dropdown(id=naming_without_sbd("mon-2"), placeholder="Chọn môn 2", clearable=False), width=6),
                    dbc.Col(input_num("diem-mon-2"), width=6),
                ], className="mb-4 align-items-center"),
            ], className="px-1"),

            dbc.Button(
                "Tính toán điểm tổ hợp", 
                id=naming_without_sbd("build-combs"),
                color="primary", className="w-100 fw-bold shadow-sm py-2"
            )
        ])  
    ], className="border-0 shadow-sm mb-3"),

    html.Div(id=naming_without_sbd("error"), className="mb-2"),

    # BƯỚC 2: XÂY DỰNG KỊCH BẢN (Ẩn cho đến khi tính xong)
    dbc.Card([
        dbc.CardHeader(
            html.Div([html.I(className="bi bi-gear-wide-connected me-2"), "Xây dựng kịch bản"]),
            className="fw-bold bg-dark text-white"
        ),

        dbc.CardBody([
            # Chọn tổ hợp & Điểm
            html.Div([
                html.Label("Tổ hợp khả dĩ", className="small fw-bold"),
                dcc.Dropdown(id=naming_without_sbd("your-comb"), className="mb-3"),

                html.Div([
                    html.Span("Điểm tổ hợp của bạn", className="small text-muted d-block"),
                    dbc.Input(
                        id=naming_without_sbd("your-score"),
                        readonly=True,
                        className="h4 fw-bold text-primary text-center bg-transparent border-0"
                    ),
                ], className="p-2 mb-3 bg-light rounded-3 border-dashed text-center"),
            ]),

            dcc.Store(id=naming_without_sbd("stored-results")),

            # Chọn điểm sàn (Kết hợp Input và Slider)
            html.Label("Thiết lập điểm sàn", className="fw-bold small mb-2"),
            dbc.Row([
                dbc.Col(
                    dbc.Input(id=naming_without_sbd("floor-score-input"), type="number", step=0.05, className="text-center shadow-sm"),
                    width=4
                ),
                dbc.Col(
                    dcc.Slider(
                        id=naming_without_sbd("floor-score"),
                        min=15, max=30, step=0.05,
                        marks={i: str(i) for i in range(15, 31, 5)},
                        className="mt-2"
                    ), width=8
                )
            ], className="mb-4 align-items-center g-2"),

            # Danh sách tổ hợp
            html.Div([
                html.Label("Tổ hợp so sánh", className="small fw-bold"),
                html.Div(id=naming_without_sbd("combs-list-container"), className="mb-4 p-2 bg-white rounded border min-vh-10")
            ]),

            dbc.Button(
                "Chạy kịch bản phân tích",
                id=naming_without_sbd("run-scenario"),
                color="success", className="w-100 py-2 fw-bold shadow"
            )
        ])
    ], id=naming_without_sbd("scenario"), style={"display": "none"}, className="border-0 shadow-sm")
], className="sticky-top", style={"top": "1rem"})



right_layout = html.Div(id=naming_without_sbd("right-content"))



layout = dbc.Container([
    dbc.Row([
        # Cột trái (Nhập liệu)
        dbc.Col(left_layout, width=12, md=4, className="px-1"),
        
        # Cột phải (Kết quả đồ thị/bảng)
        dbc.Col(
            dcc.Loading(
                id="loading-main",
                type="circle",
                children=html.Div(id=naming_without_sbd("right-content"), className="h-100")
            ), 
            width=12, md=8, className="px-1"
        )
    ], className="mt-3 mt-md-4 g-4")
], fluid=True, className="p-0 px-md-5 pb-5 bg-light")





# ------------------------------------------------------------------
#                              CALLBACK 
# ------------------------------------------------------------------

# CALLBACK 0: Chọn ngẫu nhiên môn 1
@callback(
    Output(naming_without_sbd("mon_1"), "value"),
    Input(naming_without_sbd("mon-1"), "id")
)
def chon_mon_1(_):
    """Khởi tạo ngẫu nhiên môn tự chọn đầu tiên.

    Sử dụng thuật toán random.choice để chọn một môn học từ danh mục cho trước,
    giúp cải thiện trải nghiệm người dùng bằng cách cung cấp dữ liệu mẫu ngay khi load.

    Args:
        _: Giá trị ID của thành phần (không sử dụng, dùng để trigger lúc khởi tạo).

    Returns:
        str: Tên môn học được chọn ngẫu nhiên (ví dụ: 'Vật lý', 'Hóa học').
    """
    danh_sach_mon = [m["value"] for m in BANG_CHON_MON]
    
    return random.choice(danh_sach_mon)





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
    """Duy trì tính toàn vẹn dữ liệu (Data Integrity) giữa các lựa chọn môn học.

    Đảm bảo môn tự chọn thứ 2 không trùng với môn thứ 1, ngăn chặn việc tạo ra
    các tổ hợp môn không hợp lệ trong hệ thống.

    Args:
        mon_1 (str): Tên môn học đã chọn ở ô thứ nhất.

    Returns:
        tuple: (list, str) Danh sách các tùy chọn còn lại và giá trị mặc định cho môn thứ 2.
    """
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
    """Trình xác thực trạng thái sẵn sàng của hệ thống (System Readiness Validator).

    Kiểm tra điều kiện biên cho dữ liệu đầu vào. Nút tính toán chỉ được kích hoạt
    khi tất cả các trường điểm được nhập đầy đủ và không vi phạm quy tắc điểm liệt (<= 1.0).

    Args:
        toan (float): Điểm môn Toán.
        van (float): Điểm môn Ngữ văn.
        mon_1 (float): Điểm môn tự chọn 1.
        mon_2 (float): Điểm môn tự chọn 2.

    Returns:
        bool: True nếu nút bị vô hiệu hóa (dữ liệu lỗi), False nếu sẵn sàng tính toán.
    """
    if any(s is None for s in [toan, van, mon_1, mon_2]):
        return True
    
    if any(not (0 <= s <= 10) for s in [toan, van, mon_1, mon_2]) or any(s <= 1 for s in [toan, van, mon_1, mon_2]):
        return True

    return False





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
    """Engine xử lý cốt lõi sử dụng Polars LazyFrame để tính toán tổ hợp.

    Thực hiện ánh xạ điểm người dùng vào danh mục tổ hợp quốc gia thông qua:
    1. Subset Filtering: Tìm các tổ hợp là tập con của 4 môn thi.
    2. Vectorized Computation: Tính tổng điểm trên toàn bộ tập dữ liệu bằng Polars.
    3. Memory Caching: Lưu trữ kết quả vào dcc.Store để tối ưu hóa hiệu năng cho các tác vụ sau.

    Args:
        n_clicks (int): Số lần nhấn nút.
        ... (các State): Điểm số và tên môn học từ UI.

    Returns:
        tuple: Các thuộc tính giao diện và dữ liệu JSON cho Store.
    """
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
                pl.concat_list(["Môn 1", "Môn 2", "Môn 3"]).alias("mon_set")
            ])
            .filter(
                pl.col("mon_set").list.eval(pl.element().is_in(list_mon)).list.all()
            )
            .with_columns([
                (
                    pl.col("Môn 1").replace(user_map).cast(pl.Float64) +
                    pl.col("Môn 2").replace(user_map).cast(pl.Float64) +
                    pl.col("Môn 3").replace(user_map).cast(pl.Float64)
                ).alias("score")
            ])
            .filter(pl.col("score") >= 15)
            .collect()
        )
    except Exception as e:
        return {"display": "none"}, html.P(f"Lỗi: {e}"), [], None, None

    if results.height == 0:
        return {"display": "none"}, dbc.Alert("Không có tổ hợp >= 15đ", color="warning"), [], None, None

    data_to_store = results.to_dicts()

    options = [
        {
            "label": r["Tên tổ hợp"], 
            "value": r["Tổ hợp"]    
        } 
        for r in data_to_store
    ]
    
    return {"display": "block"}, None, options, options[0]["value"], data_to_store





# CALLBACK 4: Phản hồi tức thì
@callback(
    Output(naming_without_sbd("your-score"), "value"),
    Input(naming_without_sbd("your-comb"), "value"),
    State(naming_without_sbd("stored-results"), "data"),
    prevent_initial_call=True
)
def update_score_display(selected_comb, stored_data):
    """Cập nhật hiển thị điểm số tức thì (Real-time Score Rendering).

    Thực hiện tra cứu nhanh điểm số từ bộ nhớ đệm (dcc.Store) thay vì tính toán lại từ đầu.
    Giúp tối ưu hóa trải nghiệm người dùng (UX) và giảm tải tài nguyên cho Server.

    Args:
        selected_comb (str): Mã tổ hợp người dùng vừa chọn từ Dropdown.
        stored_data (list[dict]): Danh sách kết quả tính toán đã lưu trữ dưới dạng JSON.

    Returns:
        str: Chuỗi văn bản hiển thị điểm số (định dạng 2 chữ số thập phân).
    """
    if not selected_comb or not stored_data:
        return ""
    
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
    """Khởi tạo giao diện so sánh đa kịch bản (Multi-scenario UI Initialization).

    Tạo động một Multi-Dropdown cho phép người dùng chọn thêm các tổ hợp khác
    để so sánh vị thế với tổ hợp chính ban đầu.

    Args:
        main_comb (str): Tổ hợp mục tiêu được chọn làm mốc so sánh.
        stored_data (list[dict]): Dữ liệu các tổ hợp khả thi đã được xử lý.

    Returns:
        dcc.Dropdown: Component Dropdown với các tùy chọn tổ hợp lấy từ DB.
    """
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
    """Thực thi quy tắc nghiệp vụ bảo vệ dữ liệu gốc (Business Rule Enforcement).

    Đảm bảo tổ hợp chính luôn hiện diện trong danh sách so sánh, ngăn chặn sai sót
    về logic khi người dùng tương tác xóa các thẻ (tags) trên UI.

    Args:
        selected_values (list[str]): Danh sách các tổ hợp hiện đang được chọn.
        original_comb (str): Tổ hợp mốc (Pivot) bắt buộc phải có.

    Returns:
        list[str]: Danh sách tổ hợp đã được chuẩn hóa, luôn bao gồm original_comb.
    """
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
    """Tự động cấu hình giới hạn Search Space cho tham số điểm sàn.

    Dựa trên điểm thực tế của người dùng để thu hẹp ngưỡng Max của Slider.
    Điều này ngăn chặn việc thực hiện các truy vấn vô nghĩa (điểm sàn > điểm thực tế)
    và tối ưu hóa giao diện điều khiển.

    Args:
        score_text (str): Văn bản hiển thị điểm số (ví dụ: "27.50 điểm").

    Returns:
        tuple: (max_val, default_val, max_val_input, default_val_input).
    """
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
    """Thực thi cơ chế Two-way Data Binding giữa Slider và Input Number.

    Sử dụng Dash Callback Context (ctx) để xác định nguồn trigger, đảm bảo giá trị
    giữa thanh kéo trực quan và ô nhập số chính xác luôn đồng nhất.

    Args:
        slider_val (float): Giá trị từ thanh kéo Slider.
        input_val (float): Giá trị từ ô nhập số.

    Returns:
        tuple: Cặp giá trị đã được đồng bộ hóa.
    """
    triggered_id = ctx.triggered_id
    
    if triggered_id == naming_without_sbd("floor-score"):
        return no_update, slider_val
    
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
    """Điều phối và khởi tạo Dashboard phân tích chuyên sâu.

    Hàm này đóng vai trò Controller trong mô hình MVC, thực hiện việc parse dữ liệu
    từ tầng View, kết nối với module 'display_graph_and_table' để tạo ra các 
    báo cáo trực quan (biểu đồ Plotly và bảng Polars).

    Args:
        n (int): Số lần trigger từ nút bấm thực thi.
        main_score_text (str): Điểm tổ hợp chính (dạng văn bản).
        year (int): Năm khảo thí cần so sánh.
        floor_score (float): Ngưỡng điểm sàn do người dùng thiết lập.
        selected_combs (list[str]): Danh sách các tổ hợp cần đưa vào phân tích.
        stored_data (list[dict]): Dữ liệu thô đã được xử lý trước đó.

    Returns:
        dash.development.base_component.Component: Container chứa các biểu đồ và bảng kết quả.
    """
    if not n or not main_score_text or not selected_combs:
        return no_update

    try:
        score_val = float(main_score_text.split()[0])
        
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


