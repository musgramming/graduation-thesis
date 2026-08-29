from dash import callback, Input, Output, State, html, clientside_callback, ClientsideFunction, no_update, callback_context as ctx
import dash_bootstrap_components as dbc
import polars as pl

from data import (
    BANG_DIEM_TO_HOP,
    TO_HOP,
    BANG_QUY_DOI_TINH_THANH,
    COMB_OPTIONS
)

from utils.build_script import display_graph_and_table
from .list_of_id import pid





@callback(
    [ 
        Output(pid("sbd"), "invalid"), 
        Output(pid("sbd-feedback"), "children"), 
        Output(pid("search-info"), "disabled") 
    ], 
    [ 
        Input(pid("year"), "value"), 
        Input(pid("sbd"), "value")
    ],
    prevent_initial_call=True,
)
def validate_sbd_and_toggle_button(year, sbd):
    """
    Xác thực số báo danh và điều khiển trạng thái nút Tra cứu.

    Callback được kích hoạt khi người dùng thay đổi năm thi hoặc số báo danh.
    Việc xác thực được thực hiện theo thứ tự:

    1. Kiểm tra SBD và năm thi có được nhập hay chưa.
    2. Kiểm tra SBD chỉ chứa chữ số.
    3. Kiểm tra SBD có đúng 8 chữ số.
    4. Kiểm tra năm thi có hợp lệ và từ năm 2025 trở đi.
    5. Kiểm tra mã tỉnh/thành (2 chữ số đầu của SBD) có tồn tại
       trong BANG_QUY_DOI_TINH_THANH của năm tương ứng.
    6. Kiểm tra phần số thứ tự của SBD không bằng 00000000.

    Lưu ý:
        Mã tỉnh/thành được lưu dưới dạng chuỗi trong
        BANG_QUY_DOI_TINH_THANH. Vì vậy, hai chữ số đầu của SBD
        phải được giữ nguyên dưới dạng chuỗi để không làm mất số 0
        ở đầu, ví dụ "01" không được chuyển thành int(01) -> 1.

    Args:
        year (int | float | str | None):
            Năm thi được nhập trên giao diện.

        sbd (str | int | None):
            Số báo danh cần kiểm tra.

    Returns:
        tuple:
            Tuple gồm ba giá trị:

            - invalid (bool):
                Trạng thái invalid của ô nhập SBD.
            - feedback (str):
                Thông báo lỗi hiển thị bên dưới ô nhập SBD.
            - disabled (bool):
                Trạng thái disabled của nút Tra cứu.
    """

    if not sbd or not year:
        return False, "", True

    sbd = str(sbd).strip()

    if not sbd.isdigit():
        return True, "❌ Chỉ được nhập số!", True

    if len(sbd) < 8:
        return False, "", True

    if len(sbd) > 8:
        return True, "❌ Số báo danh phải có đúng 8 chữ số!", True

    try:
        year_int = int(year)
    except (TypeError, ValueError):
        return True, "❌ Năm thi không hợp lệ!", True

    if year_int < 2025:
        return True, "❌ Năm thi không hợp lệ!", True

    year_str = str(int(year))
    ma_tinh = sbd[:2]
    stt = int(sbd[2:])

    if (
        year_str not in BANG_QUY_DOI_TINH_THANH
        or ma_tinh not in BANG_QUY_DOI_TINH_THANH[year_str]
    ):
        return True, f"❌ Mã tỉnh {ma_tinh} không tồn tại!", True

    if stt == 0:
        return True, "❌ Số báo danh không tồn tại!", True

    return False, "", False





@callback(
    [
        Output(pid("comb"), "options"),
        Output(pid("comb"), "value"),
        Output(pid("status-output-2"), "children"),
        Output(pid("score"), "children")
    ],
    [
        Input(pid("search-info"), "n_clicks"),
        Input(pid("comb"), "value")
    ], 
    [
        State(pid("sbd"), "value"),
        State(pid("year"), "value")
    ],
    prevent_initial_call=True,
)
def lookup_candidate(search_clicks, selected_comb, sbd, year):
    """
    Tra cứu dữ liệu thí sinh và hiển thị điểm theo tổ hợp.

    Callback xử lý hai sự kiện khác nhau:

    - Khi nhấn nút Tra cứu:
        + Tìm SBD trong BANG_DIEM_TO_HOP.
        + Lọc các bản ghi có tổ hợp hợp lệ.
        + Kết hợp với TO_HOP để lấy tên tổ hợp.
        + Tạo danh sách options cho Dropdown tổ hợp.
        + Tự động chọn tổ hợp đầu tiên.
        + Hiển thị tổng điểm của tổ hợp được chọn.

    - Khi người dùng thay đổi tổ hợp:
        + Giữ nguyên danh sách options và trạng thái tra cứu.
        + Chỉ truy vấn lại tổng điểm của tổ hợp mới.

    Args:
        search_clicks (int | None):
            Số lần nút Tra cứu được nhấn.

        selected_comb (str | None):
            Mã tổ hợp hiện đang được chọn.

        sbd (str | int | None):
            Số báo danh của thí sinh.

        year (int | float | str | None):
            Năm thi cần tra cứu.

    Returns:
        tuple:
            Gồm:

            - options (list):
                Danh sách tổ hợp hợp lệ cho Dropdown.
            - value (str | None):
                Tổ hợp được chọn.
            - status (component | str):
                Thông báo trạng thái tra cứu.
            - score (str):
                Tổng điểm được định dạng, ví dụ "25.50 điểm".
    """
        
    if not sbd or not year:
        return [], None, "", "---"

    try:
        year_int = int(year)
        sbd_str = str(sbd).strip()
    except (TypeError, ValueError):
        return [], None, "", "---"

    triggered = ctx.triggered_id

    # ---------------------------------------------------------------
    # 1. Bấm Tra cứu: lấy toàn bộ tổ hợp hợp lệ của SBD.
    # ---------------------------------------------------------------
    if triggered == pid("search-info"):
        if not search_clicks:
            return [], None, "", "---"

        if year_int not in BANG_DIEM_TO_HOP:
            return (
                [],
                None,
                dbc.Alert("Dữ liệu năm này chưa có!", color="warning"),
                "---",
            )

        df_all = (
            BANG_DIEM_TO_HOP[year_int]
            .filter(pl.col("SOBAODANH") == sbd_str)
            .collect()
        )

        if df_all.is_empty():
            return (
                [],
                None,
                dbc.Alert(
                    f"Không tìm thấy SBD {sbd_str}!",
                    color="danger",
                ),
                "---",
            )

        df_valid = df_all.filter(pl.col("Hợp lệ") == True)

        if df_valid.is_empty():
            return (
                [],
                None,
                [
                    dbc.Alert(
                        "Thông tin xét tuyển không khả dụng",
                        color="warning",
                        className="mb-1",
                    ),
                    html.Small(
                        "Lý do: Không tìm thấy dữ liệu tổ hợp hợp lệ "
                        "(có thể do thiếu điểm môn thành phần hoặc chưa "
                        "đủ điều kiện xét công nhận tốt nghiệp).",
                        className="text-muted",
                    ),
                ],
                "---",
            )

        final_df = (
            df_valid.lazy()
            .join(TO_HOP, on="Tổ hợp", how="left")
            .select(["Tổ hợp", "Tên tổ hợp", "Tổng điểm"])
            .sort("Tổ hợp")
            .collect()
        )

        options = [
            {
                "label": row["Tên tổ hợp"],
                "value": row["Tổ hợp"],
            }
            for row in final_df.to_dicts()
        ]

        first_value = options[0]["value"] if options else None

        score_val = (
            final_df
            .filter(pl.col("Tổ hợp") == first_value)
            .select("Tổng điểm")
            .item()
            if first_value
            else None
        )

        score_text = (
            f"{score_val:.2f} điểm"
            if score_val is not None
            else "---"
        )

        return options, first_value, "", score_text

    # ---------------------------------------------------------------
    # 2. Đổi tổ hợp: chỉ lấy lại điểm.
    # ---------------------------------------------------------------
    if triggered == pid("comb"):
        if not selected_comb:
            return no_update, None, no_update, "---"

        if year_int not in BANG_DIEM_TO_HOP:
            return no_update, no_update, no_update, "Lỗi dữ liệu"

        df_score = (
            BANG_DIEM_TO_HOP[year_int]
            .filter(
                (pl.col("SOBAODANH") == sbd_str)
                & (pl.col("Tổ hợp") == selected_comb)
            )
            .select("Tổng điểm")
            .collect()
        )

        if df_score.is_empty():
            return no_update, no_update, no_update, "Không tìm thấy điểm"

        score_val = df_score.item()

        return (
            no_update,
            no_update,
            no_update,
            f"{score_val:.2f} điểm",
        )

    return no_update, no_update, no_update, no_update


# ---------------------------------------------------------------------------
# DROPDOWN SO SÁNH
# ---------------------------------------------------------------------------
# Component đã tồn tại trong layout. Callback chỉ cập nhật properties.

@callback(
    [
        Output(pid("combs-script"), "options"),
        Output(pid("combs-script"), "value"),
        Output(pid("combs-script"), "disabled"),
    ],
    Input(pid("comb"), "value"),
    prevent_initial_call=True,
)
def update_comparison_combinations(original_comb):
    """
    Cập nhật Dropdown các tổ hợp dùng để xây dựng kịch bản so sánh.

    Khi tổ hợp chính của thí sinh thay đổi, callback:

    - Nạp danh sách toàn bộ tổ hợp có thể sử dụng để so sánh.
    - Đặt tổ hợp chính làm giá trị được chọn mặc định.
    - Kích hoạt Dropdown nếu đã có tổ hợp chính.

    Nếu chưa có tổ hợp chính, Dropdown được xóa options/value và disabled.

    Args:
        original_comb (str | None):
            Mã tổ hợp chính đang được chọn.

    Returns:
        tuple:
            Gồm:

            - options (list):
                Danh sách toàn bộ tổ hợp có thể lựa chọn.
            - value (list):
                Danh sách tổ hợp được chọn mặc định.
            - disabled (bool):
                Trạng thái disabled của Dropdown.
    """
    if not original_comb:
        return [], [], True

    return (
        COMB_OPTIONS,
        [original_comb],
        False,
    )





# ---------------------------------------------------------------------------
# CLIENT-SIDE: CẤU HÌNH SLIDER ĐIỂM SÀN
# ---------------------------------------------------------------------------
# Slider đã có sẵn trong layout; JS chỉ cập nhật max/marks/value/disabled
# và nội dung/cảnh báo.
clientside_callback(
    ClientsideFunction("withSBD", "configure_floor_score"),
    [
        Output(pid("floor-score-slider"), "max"),
        Output(pid("floor-score-slider"), "marks"),
        Output(pid("floor-score-slider"), "value"),
        Output(pid("floor-score-slider"), "disabled"),

        Output(pid("floor-score-warning"), "children"),
        Output(pid("floor-score-warning"), "is_open"),
    ],
    Input(pid("score"), "children"),
    prevent_initial_call=True,
)




clientside_callback(
    ClientsideFunction("withSBD", "input_to_slider"),
    Output(pid("floor-score-slider"), "value", allow_duplicate=True),
    Input(pid("floor-score-input"), "value"),
    State(pid("floor-score-slider"), "min"),
    State(pid("floor-score-slider"), "max"),
    prevent_initial_call=True,
)





clientside_callback(
    ClientsideFunction("withSBD", "slider_to_input"),
    Output(pid("floor-score-input"), "value"),
    Input(pid("floor-score-slider"), "value"),
    prevent_initial_call=True,
)





# ---------------------------------------------------------------------------
# CLIENT-SIDE: ENABLE/DISABLE NÚT PHÂN TÍCH
# ---------------------------------------------------------------------------
clientside_callback(
    ClientsideFunction("withSBD", "toggle_analysis_button"),
    Output(pid("analysis"),"disabled"),
    [
        Input(pid("score"), "children"),
        Input(pid("combs-script"), "value"),
        Input(pid("floor-score-slider"), "disabled"),
    ],
    prevent_initial_call=True,
)





# ---------------------------------------------------------------------------
# SERVER-SIDE: PHÂN TÍCH
# ---------------------------------------------------------------------------
@callback(
    Output(pid("full-div"), "children"),
    Input(pid("analysis"), "n_clicks"),
    State(pid("score"), "children"),
    State(pid("year"), "value"),
    State(pid("floor-score-slider"), "value"),
    State(pid("combs-script"), "value"),
    State(pid("mode-selection"), "value"),
    prevent_initial_call=True,
)
def analysis_callback(n, score_text, year, floor_score, combs, mode):
    """
    Thực hiện phân tích dữ liệu và hiển thị kết quả.

    Callback chỉ được kích hoạt khi người dùng nhấn nút Xây kịch bản.
    Các giá trị cấu hình từ giao diện được kiểm tra trước khi truyền
    vào hàm display_graph_and_table().

    Quy trình xử lý:

    1. Kiểm tra điểm và các tham số bắt buộc.
    2. Chuyển đổi điểm, năm và điểm sàn về kiểu dữ liệu phù hợp.
    3. Gọi display_graph_and_table() để thực hiện toàn bộ xử lý
       dữ liệu và tạo kết quả phân tích.
    4. Trả kết quả vào vùng full-div.
    5. Nếu dữ liệu không hợp lệ hoặc xảy ra lỗi, hiển thị Alert tương ứng.

    Args:
        n (int | None):
            Số lần nút Xây kịch bản được nhấn.

        score_text (str):
            Điểm của thí sinh ở dạng chuỗi hiển thị, ví dụ "25.50 điểm".

        year (int | float | str | None):
            Năm thi được sử dụng trong phân tích.

        floor_score (float | None):
            Ngưỡng điểm sàn được người dùng lựa chọn.

        combs (list[str] | None):
            Danh sách các tổ hợp được sử dụng trong kịch bản.

        mode (str | None):
            Phương pháp quy đổi điểm, ví dụ:
            "raw-score", "z-score" hoặc "robust".

    Returns:
        component:
            Nội dung hiển thị trong vùng kết quả phân tích.
            Có thể là kết quả từ display_graph_and_table() hoặc
            dbc.Alert nếu dữ liệu đầu vào không hợp lệ / xảy ra lỗi.
    """
    
    if not n or not score_text or score_text in {"---", "Không tìm thấy điểm"}:
        return None

    if year is None or floor_score is None or not combs or not mode:
        return dbc.Alert(
            "Vui lòng hoàn thiện đầy đủ thông tin phân tích.",
            color="warning",
        )

    try:
        score_val = float(str(score_text).split()[0])

        return display_graph_and_table(
            year=int(year),
            self_score=score_val,
            floor_score=float(floor_score),
            combs=combs,
            mode=mode,
        )

    except (ValueError, TypeError, KeyError) as e:
        print(f"Lỗi dữ liệu Callback: {e}")
        return dbc.Alert(
            f"Dữ liệu đầu vào không hợp lệ: {e}",
            color="danger",
        )

    except Exception as e:
        print(f"Lỗi Callback: {e}")
        return dbc.Alert(
            f"Đã có lỗi xảy ra: {e}",
            color="danger",
        )