from dash import html, dcc, callback, Input, Output, State, no_update, clientside_callback, ClientsideFunction
import polars as pl
import dash_bootstrap_components as dbc

from data import TO_HOP
from utils.build_script import display_graph_and_table
from utils.persistent import make_persistent

from .list_of_id import pid




# ============================================================================
# CLIENT-SIDE CALLBACKS
# ============================================================================

# 1. Không cho phép hai môn tự chọn trùng nhau.
#
# Toàn bộ logic chỉ phụ thuộc vào BANG_CHON_MON và hai giá trị đang chọn,
# nên không cần request lên Python server.
clientside_callback(
    ClientsideFunction("withoutSbd", "sync_subjects"),
    Output(pid("mon-1"), "options"),
    Output(pid("mon-1"), "value"),
    Output(pid("mon-2"), "options"),
    Output(pid("mon-2"), "value"),
    Input(pid("mon-1"), "value"),
    Input(pid("mon-2"), "value")
)





# 2. Kiểm tra dữ liệu điểm để bật/tắt nút "Tính toán điểm tổ hợp".
clientside_callback(
    ClientsideFunction("withoutSbd", "validate_scores"),
    Output(pid("build-combs"), "disabled"),
    Input(pid("math"), "value"),
    Input(pid("literature"), "value"),
    Input(pid("diem-mon-1"), "value"),
    Input(pid("diem-mon-2"), "value"),
)





# 3. Bảo vệ tổ hợp chính trong Dropdown tổ hợp so sánh.
#
# Component "combs-list" được tạo động bởi callback render_scenario_dropdown.
clientside_callback(
    ClientsideFunction("withoutSbd", "protect_original_comb"),
    Output(pid("combs-list"), "value"),
    Input(pid("combs-list"), "value"),
    State(pid("your-comb"), "value"),
    prevent_initial_call=True,
)





# 4. Gộp callback cũ #6 + #7:
#
# - cập nhật max theo điểm tổ hợp của thí sinh;
# - đồng bộ hai chiều Slider <-> Numeric Input.
#
# Đây hoàn toàn là UI state, nên chạy clientside.
clientside_callback(
    ClientsideFunction("withoutSbd", "sync_floor_score"),
    Output(pid("floor-score"), "max"),
    Output(pid("floor-score"), "value"),
    Output(pid("floor-score-input"), "max"),
    Output(pid("floor-score-input"), "value"),
    Input(pid("your-score"), "value"),
    Input(pid("floor-score"), "value"),
    Input(pid("floor-score-input"), "value"),
)





clientside_callback(
    ClientsideFunction("withoutSbd", "toggle_run_button"),
    Output(pid("run-scenario"), "disabled"),
    Input(pid("your-score"), "value"),
    Input(pid("combs-list"), "value"),
)





# ============================================================================
# SERVER-SIDE CALLBACKS
# ============================================================================

@callback(
    Output(pid("scenario"), "style"),
    Output(pid("error"), "children"),
    Output(pid("your-comb"), "options"),
    Output(pid("your-comb"), "value"),
    Output(pid("stored-results"), "data"),
    Output(pid("your-comb"), "disabled"),
    Input(pid("build-combs"), "n_clicks"),
    State(pid("math"), "value"),
    State(pid("literature"), "value"),
    State(pid("mon-1"), "value"),
    State(pid("diem-mon-1"), "value"),
    State(pid("mon-2"), "value"),
    State(pid("diem-mon-2"), "value"),
    prevent_initial_call=True,
)
def calculate_and_store(
    n_clicks,
    toan,
    van,
    mon_1,
    diem_mon_1,
    mon_2,
    diem_mon_2,
):
    """
    Tính toán các tổ hợp điểm khả dĩ và lưu kết quả vào dcc.Store.

    Đây là callback server-side chính của bước xây dựng kịch bản.
    Callback nhận bốn điểm thi, ánh xạ chúng vào TO_HOP bằng Polars,
    lọc các tổ hợp tạo được tổng điểm từ 15 trở lên, sau đó lưu toàn bộ
    kết quả đã tính vào stored-results để các callback phía sau tái sử dụng.

    Quy trình:
        1. Chuẩn hóa bốn điểm thành user_map.
        2. Loại dữ liệu có điểm liệt (<= 1).
        3. Lọc TO_HOP theo tập môn người dùng có.
        4. Tính tổng điểm bằng biểu thức Polars.
        5. Giữ các tổ hợp có score >= 15.
        6. Chuyển kết quả sang list[dict] để lưu trong dcc.Store.
        7. Hiển thị khu vực Xây dựng kịch bản.

    Args:
        n_clicks (int | None):
            Số lần nút "Tính toán điểm tổ hợp" được nhấn.

        toan (float | None):
            Điểm Toán.

        van (float | None):
            Điểm Ngữ văn.

        mon_1 (str | None):
            Tên môn tự chọn thứ nhất.

        diem_mon_1 (float | None):
            Điểm của môn tự chọn thứ nhất.

        mon_2 (str | None):
            Tên môn tự chọn thứ hai.

        diem_mon_2 (float | None):
            Điểm của môn tự chọn thứ hai.

    Returns:
        tuple:
            (
                scenario_style,
                error_message,
                combination_options,
                selected_combination,
                stored_results,
            )
    """
    if not n_clicks:
        return {"display": "none"}, None, [], None, None, True

    user_map = {
        "Toán": float(toan or 0),
        "Văn": float(van or 0),
        mon_1: float(diem_mon_1 or 0),
        mon_2: float(diem_mon_2 or 0),
    }

    if any(score <= 1 for score in user_map.values()):
        return (
            {"display": "none"},
            dbc.Alert(
                "Phát hiện điểm liệt (<= 1)!",
                color="danger",
            ),
            [],
            None,
            None,
            True
        )

    list_mon = list(user_map.keys())

    try:
        results = (
            TO_HOP
            .with_columns(
                pl.concat_list(
                    ["Môn 1", "Môn 2", "Môn 3"]
                ).alias("mon_set")
            )
            .filter(
                pl.col("mon_set")
                .list.eval(
                    pl.element().is_in(list_mon)
                )
                .list.all()
            )
            .with_columns(
                (
                    pl.col("Môn 1").replace(user_map).cast(pl.Float64)
                    + pl.col("Môn 2").replace(user_map).cast(pl.Float64)
                    + pl.col("Môn 3").replace(user_map).cast(pl.Float64)
                ).alias("score")
            )
            .filter(pl.col("score") >= 15)
            .collect()
        )
    except Exception as exc:
        return (
            {"display": "none"},
            html.P(f"Lỗi: {exc}"),
            [],
            None,
            None,
            True
        )

    if results.height == 0:
        return (
            {"display": "none"},
            dbc.Alert(
                "Không có tổ hợp >= 15đ",
                color="warning",
            ),
            [],
            None,
            None,
            True
        )

    data_to_store = results.to_dicts()

    options = [
        {
            "label": row["Tên tổ hợp"],
            "value": row["Tổ hợp"],
        }
        for row in data_to_store
    ]

    return (
        {"display": "block"},
        None,
        options,
        options[0]["value"],
        data_to_store,
        False
    )





@callback(
    Output(pid("your-score"), "value"),
    Output(pid("combs-list-container"), "children"),
    Input(pid("your-comb"), "value"),
    State(pid("stored-results"), "data"),
    prevent_initial_call=True,
)
def update_combination_details(selected_comb, stored_data):
    """
    Cập nhật đồng thời điểm tổ hợp và danh sách tổ hợp so sánh.

    Callback này gộp hai callback cũ:

        update_score_display()
        render_scenario_dropdown()

    Cả hai đều có cùng Input/State và đều chỉ phụ thuộc vào tổ hợp
    đang chọn cùng dữ liệu đã cache trong dcc.Store, vì vậy việc gộp
    giúp tránh chạy hai callback Python riêng biệt cho cùng một sự kiện.

    Args:
        selected_comb (str | None):
            Mã tổ hợp hiện đang được chọn.

        stored_data (list[dict] | None):
            Kết quả tổ hợp đã được calculate_and_store() lưu vào dcc.Store.

    Returns:
        tuple:
            - str:
                Điểm tổ hợp được định dạng, ví dụ "25.50 điểm".
            - Component | None:
                Multi-select Dropdown dùng để chọn các tổ hợp so sánh.
    """
    if not selected_comb or not stored_data:
        return "", None

    selected_item = next(
        (
            item
            for item in stored_data
            if item["Tổ hợp"] == selected_comb
        ),
        None,
    )

    if selected_item is None:
        score_text = "N/A"
    else:
        score_text = f"{selected_item['score']:.2f} điểm"

    options = [
        {
            "label": item["Tên tổ hợp"],
            "value": item["Tổ hợp"],
        }
        for item in stored_data
    ]

    scenario_dropdown = make_persistent(
        dcc.Dropdown(
            id=pid("combs-list"),
            options=options,
            value=[selected_comb],
            multi=True,
            clearable=True,
        )
    )

    return score_text, scenario_dropdown





@callback(
    Output(pid("right-content"), "children"),
    Input(pid("run-scenario"), "n_clicks"),
    State(pid("your-score"), "value"),
    State(pid("year"), "value"),
    State(pid("floor-score"), "value"),
    State(pid("combs-list"), "value"),
    State(pid("stored-results"), "data"),
    prevent_initial_call=True,
)
def display_analysis_without_sbd(
    n,
    main_score_text,
    year,
    floor_score,
    selected_combs,
    stored_data,
):
    """
    Chạy phân tích cuối cùng và hiển thị Dashboard kết quả.

    Đây là callback server-side vì nó gọi display_graph_and_table(),
    nơi thực hiện xử lý dữ liệu và tạo các thành phần trực quan hóa.

    Args:
        n (int | None):
            Số lần nhấn nút "Chạy kịch bản phân tích".

        main_score_text (str):
            Điểm tổ hợp chính ở dạng chuỗi, ví dụ "25.50 điểm".

        year (int | float | str):
            Năm khảo thí.

        floor_score (float):
            Ngưỡng điểm sàn.

        selected_combs (list[str] | None):
            Các tổ hợp được chọn để phân tích.

        stored_data (list[dict] | None):
            Dữ liệu tổ hợp đã tính trước đó.

    Returns:
        Component:
            Dashboard biểu đồ/bảng do display_graph_and_table() tạo ra,
            hoặc dbc.Alert nếu dữ liệu không hợp lệ.
    """
    if not n or not main_score_text or not selected_combs:
        return no_update

    if not stored_data:
        return dbc.Alert(
            "Chưa có dữ liệu tổ hợp. Vui lòng tính điểm trước.",
            color="warning",
        )

    try:
        score_val = float(main_score_text.split()[0])
        floor_score_value = float(floor_score)

        return display_graph_and_table(
            year=int(year),
            self_score=score_val,
            floor_score=floor_score_value,
            combs=selected_combs,
            mode="raw-score",
        )

    except Exception as exc:
        return dbc.Alert(
            f"Lỗi: {exc}",
            color="danger",
        )