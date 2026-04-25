from typing import Literal

from dash import html, dcc, dash_table
import plotly.graph_objects as go
import plotly.express as px
import polars as pl
import dash_bootstrap_components as dbc

from data import BANG_DIEM
from .graph import build_strict_graph





def filter_raw_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Trích xuất dữ liệu điểm thô dựa trên các tiêu chí lọc.

    Phương pháp này giữ nguyên giá trị thực tế của kỳ thi, phục vụ cho việc
    tra cứu vị thế trực tiếp mà không qua biến đổi thống kê.

    Args:
        year (int): Năm dữ liệu cần truy vấn.
        floor_score (float): Ngưỡng điểm sàn thiết lập bởi người dùng.
        combs (list[str]): Danh sách mã các tổ hợp cần lọc.

    Returns:
        pl.LazyFrame: Một bản kế hoạch truy vấn Polars đã được lọc theo điều kiện.
    """
    return BANG_DIEM[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) &
        (pl.col("Tổng điểm") >= floor_score) &
        (pl.col("Hợp lệ") == True)
    ).with_columns(
        pl.col("Tổng điểm").alias("Điểm quy đổi")
    )





def filter_z_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Chuẩn hóa dữ liệu bằng phương pháp Z-Score (Standardization).

    Mục đích: Đưa các tổ hợp môn khác nhau về cùng một phân phối chuẩn (Mean=0, Std=1),
    sau đó tái quy đổi về thang điểm 30. Giúp so sánh công bằng giữa các tổ hợp
    có độ khó/phổ điểm khác nhau.

    Quy trình:
        1. Tính Mean và Standard Deviation cho từng tổ hợp.
        2. Tính toán Z-score: z = (x - mean) / std.
        3. Feature Scaling: Ép dãn giá trị Z về thang [0, 30] dựa trên Min/Max Z.

    Args:
        year (int): Năm dữ liệu.
        floor_score (float): Điểm sàn quy đổi.
        combs (list[str]): Danh sách tổ hợp.

    Returns:
        pl.LazyFrame: Dữ liệu đã chuẩn hóa theo phân phối xác suất.
    """
    # B1: Lọc dữ liệu cơ bản
    df = BANG_DIEM[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) &
        (pl.col("Hợp lệ") == True)
    )
    
    # B2: Quy đổi về thang [~-3, ~3]
    stats = df.group_by("Tổ hợp").agg([
        pl.col("Tổng điểm").mean().alias("mean"),
        pl.col("Tổng điểm").std().alias("std")
    ])
    
    df = df.join(stats, on="Tổ hợp").with_columns(
        pl.when(pl.col("std") > 0)
            .then((pl.col("Tổng điểm") - pl.col("mean")) / pl.col("std"))
            .otherwise(0.0)
            .alias("z_val")
    ).drop(["mean", "std"])

    # B3: Quy đổi về thang [0, 30]
    min_max_z = df.group_by("Tổ hợp").agg([
        pl.col("z_val").min().alias("z_min"),
        pl.col("z_val").max().alias("z_max")
    ])
    
    df = (
        df.join(min_max_z, on="Tổ hợp")
        .with_columns(
            pl.when(pl.col("z_max") > pl.col("z_min"))
                .then((pl.col("z_val") - pl.col("z_min")) / (pl.col("z_max") - pl.col("z_min")) * 30)
                .otherwise(15.0) # 15 là mức trung bình an toàn cho Z-score
                .alias("Điểm quy đổi")
        )
        .drop(["z_min", "z_max", "z_val"])
        .filter(
            pl.col("Điểm quy đổi") >= floor_score
        )
    )

    return df





def filter_robust_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    """Chuẩn hóa dữ liệu bằng phương pháp Robust Scaling.

    Mục đích: Loại bỏ ảnh hưởng của các giá trị ngoại lai (outliers) và các phổ điểm
    bị lệch (skewed distribution). Sử dụng Trung vị (Median) và Khoảng biến thiên
    tứ phân vị (IQR) thay vì Mean/Std để đảm bảo tính ổn định.

    Công thức quy đổi: r = (x - Median) / (Q3 - Q1).

    Args:
        year (int): Năm dữ liệu.
        floor_score (float): Điểm sàn quy đổi.
        combs (list[str]): Danh sách tổ hợp.

    Returns:
        pl.LazyFrame: Dữ liệu đã được loại bỏ nhiễu từ các điểm số cực đoan.
    """
    df = BANG_DIEM[year].filter(pl.col("Tổ hợp").is_in(combs))
    
    # B1: Tính các chỉ số Robust (Median, Q1, Q3)
    stats = df.group_by("Tổ hợp").agg([
        pl.col("Tổng điểm").median().alias("median"),
        pl.col("Tổng điểm").quantile(0.25).alias("q1"),
        pl.col("Tổng điểm").quantile(0.75).alias("q3")
    ])
    
    # B2: Tính giá trị Robust và quy đổi luôn về thang 30
    # Công thức: (x - median) / (q3 - q1)
    df_robust = df.join(stats, on="Tổ hợp").with_columns(
        pl.when(pl.col("q3") > pl.col("q1"))
        .then((pl.col("Tổng điểm") - pl.col("median")) / (pl.col("q3") - pl.col("q1")))
        .otherwise(0.0)
        .alias("r_val")
    )
    
    # Tìm r_min, r_max để ép về [0, 30]
    r_limit = df_robust.group_by("Tổ hợp").agg([
        pl.col("r_val").min().alias("r_min"),
        pl.col("r_val").max().alias("r_max")
    ])
    
    return (
        df_robust.join(r_limit, on="Tổ hợp")
        .with_columns(
            pl.when(pl.col("r_max") > pl.col("r_min"))
            .then((pl.col("r_val") - pl.col("r_min")) / (pl.col("r_max") - pl.col("r_min")) * 30)
            .otherwise(15.0)
            .alias("Điểm quy đổi")
        )
        .filter(pl.col("Điểm quy đổi") >= floor_score)
    )





def transform_scores(year: int, combs: list[str], mode: str) -> pl.LazyFrame:
    """Hàm điều phối (Dispatcher) cho các phương thức quy đổi điểm số.

    Sử dụng các hằng số ANCHOR (15.0) và SCALE_FACTOR (5.0) để duy trì đặc tính
    phân phối của dữ liệu trong khi vẫn giữ kết quả nằm trong khung điểm 0-30
    quen thuộc với người dùng.

    Args:
        year (int): Năm khảo thí.
        combs (list[str]): Danh sách tổ hợp môn.
        mode (str): Chế độ quy đổi ('raw-score', 'z-score', 'robust').

    Returns:
        pl.LazyFrame: LazyFrame chứa cột 'Điểm quy đổi' đã được xử lý theo mode.
        
    Note:
        Sử dụng phương pháp .clip(0, 30) để đảm bảo tính an toàn dữ liệu đầu ra.
    """
    lf = BANG_DIEM[year].filter(pl.col("Tổ hợp").is_in(combs))
    
    # Hằng số quy đổi để giữ thang 0-30 nhưng không làm mất đặc tính phân phối
    # Giả sử: Mean/Median nằm ở 15 điểm, mỗi 1 Std/IQR dãn ra 5 điểm
    ANCHOR = 15.0
    SCALE_FACTOR = 5.0 

    if mode == "raw-score":
        return lf.with_columns(pl.col("Tổng điểm").alias("Điểm quy đổi"))

    elif mode == "z-score":
        stats = lf.group_by("Tổ hợp").agg([
            pl.col("Tổng điểm").mean().alias("mean"),
            pl.col("Tổng điểm").std().alias("std")
        ])
        return lf.join(stats, on="Tổ hợp").with_columns(
            (ANCHOR + ((pl.col("Tổng điểm") - pl.col("mean")) / pl.col("std")) * SCALE_FACTOR)
            .clip(0, 30) # Đảm bảo không vượt quá thang điểm
            .round(3)
            .alias("Điểm quy đổi")
        )

    elif mode == "robust":
        stats = lf.group_by("Tổ hợp").agg([
            pl.col("Tổng điểm").median().alias("median"),
            pl.col("Tổng điểm").quantile(0.25).alias("q1"),
            pl.col("Tổng điểm").quantile(0.75).alias("q3")
        ])
        return lf.join(stats, on="Tổ hợp").with_columns(
            pl.when(pl.col("q3") > pl.col("q1"))
            .then(ANCHOR + ((pl.col("Tổng điểm") - pl.col("median")) / (pl.col("q3") - pl.col("q1"))) * SCALE_FACTOR)
            .otherwise(ANCHOR)
            .clip(0, 30)
            .round(3)
            .alias("Điểm quy đổi")
        )

    return lf





def display_graph_and_table(year: int, self_score : float,  floor_score : float, combs : list[str], mode : Literal["raw-score", "min-max", "z-score", "robust"]) -> html.Div:
    """
    Xây dựng báo cáo phân tích vị thế và dự báo rủi ro tuyển sinh dựa trên kịch bản điểm số.

    Hệ thống sử dụng các phương pháp quy đổi thống kê để chuẩn hóa sự khác biệt giữa các tổ hợp môn, 
    giúp thí sinh định vị chính xác năng lực trong "biển" dữ liệu.

    Args:
        year (int): Năm dữ liệu khảo thí.
        self_score (float): Điểm số thực tế hoặc dự kiến của người dùng.
        floor_score (float): Ngưỡng điểm xét tuyển dự kiến (Điểm sàn).
        combs (list[str]): Các tổ hợp môn cùng xét tuyển vào ngành/trường mục tiêu.
        mode (str): Phương pháp chuẩn hóa dữ liệu:
            - "raw-score": Phân tích dựa trên điểm thực tế (Dành cho tra cứu nhanh).
            - "z-score": Định vị năng lực qua độ lệch chuẩn (Vị thế học thuật cho lớp 12).
            - "robust": Khử nhiễu "mưa điểm 10" / "mưa điểm thấp" và sai số outliers bằng trung vị (Median).

    Returns:
        html.Div: Dashboard báo cáo đa tầng, bao gồm các cụm thông tin:
            1. Cụm Vị Thế (PR & Rank): Thống kê số người vượt ngưỡng và xếp hạng phần trăm (Percentile Rank).
            2. Cụm Toàn Cảnh (Distribution): So sánh phổ điểm cá nhân với phổ điểm tổng quát của các tổ hợp được chọn.
            3. Cụm Cạnh Tranh (Competition Zoom): Biểu đồ mật độ thí sinh tại vùng điểm [Self ± 1] để đánh giá rủi ro "nghẽn điểm".
            4. Cụm An Toàn (Safety Zoom): Biểu đồ vùng điểm sàn [Floor ± 1] để dự báo xác suất trúng tuyển (Đáp ứng nhu cầu lớp 10).
            5. Cụm Tham Chiếu (Reference Data): Bảng đại lượng thống kê (Mean, Median, Std) và danh sách Top 20 "tinh hoa".
    """

    # 1. Kiểm tra đầu vào & Xử lý dữ liệu (Lazy)
    if not combs:
        return html.Div("Vui lòng chọn ít nhất một tổ hợp môn.")
    
    # Sử dụng hàm transform_scores bạn đã viết để quy đổi
    lf_transformed = transform_scores(year, combs, mode)
    
    # Lấy điểm cao nhất mỗi thí sinh
    lf_final = lf_transformed.group_by("SOBAODANH").agg([
        pl.col("Điểm quy đổi").max().alias("Điểm quy đổi"),
        pl.col("Tổ hợp").get(pl.col("Điểm quy đổi").arg_max()).alias("Tổ hợp_chọn")
    ])

    # 2. Thực thi (Collect) một lần duy nhất
    df_result = lf_final.collect()

    if df_result.is_empty():
        return dbc.Alert("Không tìm thấy dữ liệu phù hợp với bộ lọc hiện tại.", color="warning", className="mt-4")

    # 3. Tính toán vị thế kép
    
    # A. Vị thế tổng quát (So với toàn bộ thí sinh thi tổ hợp đó)
    total_count = df_result.height
    overall_rank = df_result.filter(pl.col("Điểm quy đổi") > self_score).height + 1
    overall_pr = (1 - (overall_rank / total_count)) * 100

    # B. Vị thế cạnh tranh (Chỉ so với những người đủ điểm sàn)
    df_on_floor = df_result.filter(pl.col("Điểm quy đổi") >= floor_score)
    total_on_floor = df_on_floor.height
    
    if total_on_floor > 0 and self_score >= floor_score:
        floor_rank = df_on_floor.filter(pl.col("Điểm quy đổi") > self_score).height + 1
        floor_pr = (1 - (floor_rank / total_on_floor)) * 100
    else:
        floor_rank = "N/A"
        floor_pr = 0

    # 4. Lọc dữ liệu biểu đồ Zoom (Eager)
    df_comp = df_result.filter(
        (pl.col("Điểm quy đổi") >= self_score - 1) & 
        (pl.col("Điểm quy đổi") <= self_score + 1)
    )
    df_safety = df_result.filter(
        (pl.col("Điểm quy đổi") >= floor_score - 1) & 
        (pl.col("Điểm quy đổi") <= floor_score + 1)
    )
    df_top20 = df_result.sort("Điểm quy đổi", descending=True).head(20)

    df_top20_display = df_top20.rename({
        "Điểm quy đổi": "Điểm",
        "Tổ hợp_chọn": "Tổ hợp"
    })


    # --- 5. CẤU HÌNH BIỂU ĐỒ (Sử dụng xbins để chuẩn hóa cột 0.2) ---    
    fig_overall = px.histogram(
        df_result.to_pandas(), 
        x="Điểm quy đổi", 
        title="Phổ điểm toàn cảnh", 
        color_discrete_sequence=['#3498db'],
        hover_data={"Điểm quy đổi": False}
    )
    fig_overall.update_traces(
        xbins=dict(
            start=0, 
            end=30 + 0.2, 
            size=0.25
        ),
        hovertemplate="<br>".join([
            "<b>Mức điểm: %{x}</b>",
            "Số lượng: %{y} thí sinh",
        ])
    )
    fig_overall.add_vline(
        x=floor_score, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Điểm sàn",
        annotation_position="top left"
    )
    fig_overall.add_vline(
        x=self_score, 
        line_dash="dash", 
        line_color="#DAA520", 
        annotation_text="Điểm của bạn"
    )
    fig_overall.update_xaxes(
        range=[0, 31],        
        constrain="domain",   
        nticks=10             
    )
    build_strict_graph(fig_overall)



    if df_comp.is_empty():
    # Thay vì trả về Graph trống, có thể trả về một thông báo
        fig_comp = go.Figure().add_annotation(text="Không có thí sinh trong vùng điểm này", showarrow=False)
    else:
        fig_comp = px.histogram(
            df_comp.to_pandas(), 
            x="Điểm quy đổi", 
            color_discrete_sequence=['#e74c3c'], 
            title="Cận cảnh cạnh tranh (Bạn ± 1đ)"
        )
        fig_comp.update_traces(
            xbins=dict(size=0.2)
        )
        fig_comp.add_vline(
            x=self_score, 
            line_dash="dot", 
            line_color="#27ae60", 
            annotation_text="Vị trí của bạn"
        )
    build_strict_graph(fig_comp)


    fig_safety = px.histogram(
        df_safety.to_pandas(), 
        x="Điểm quy đổi", 
        color_discrete_sequence=['#2ecc71'], 
        title="Cận cảnh an toàn (Sàn ± 1đ)"
    )
    fig_safety.update_traces(
        xbins=dict(size=0.2)
    )
    fig_safety.add_vline(
        x=floor_score, 
        line_dash="dot", 
        line_color="#9935cc", 
        annotation_text="Sàn"
    )
    build_strict_graph(fig_safety)


    # --- 6. TRẢ VỀ GIAO DIỆN ---
    return html.Div([
        # --- HEADER BÁO CÁO ---
        html.Div([
            html.H2(f"BÁO CÁO PHÂN TÍCH VỊ THẾ {year}", 
                    className="text-center fw-bold text-dark mt-2 mb-0"),
            html.P(f"Phương pháp chuẩn hóa: {mode.upper()}", 
                   className="text-center text-muted small mb-4"),
        ]),

        # --- CỤM THẺ CHỈ SỐ (KPI Cards) ---
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("VỊ THẾ TỔNG QUÁT", className="text-center small fw-bold py-1"),
                    dbc.CardBody([
                        html.H4(f"Hạng {overall_rank:,}", className="text-primary text-center mb-0"),
                        html.P(f"Trên tổng {total_count:,} thí sinh", className="text-center small text-muted mb-2"),
                        html.Div(dbc.Badge(f"PR: {overall_pr:.2f}%", color="info", className="w-100"), className="text-center")
                    ])
                ], className="shadow-sm border-0"), width=12, md=6, className="mb-3"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("VỊ THẾ CẠNH TRANH", className="text-center small fw-bold py-1"),
                    dbc.CardBody([
                        html.H4(f"Hạng {floor_rank:,}", className="text-dark text-center mb-0"),
                        html.P(f"Trong nhóm đủ điểm sàn (>{floor_score})", className="text-center small text-muted mb-2"),
                        html.Div(
                            dbc.Badge(
                                f"An toàn: {floor_pr:.2f}%", 
                                color="success" if floor_pr > 50 else "warning", 
                                className="w-100"
                            ), className="text-center"
                        )
                    ])
                ], className="shadow-sm border-0"), width=12, md=6, className="mb-3"
            ),
        ], className="mb-4"),

        # --- 1. BIỂU ĐỒ PHỔ ĐIỂM TOÀN CẢNH ---
        dbc.Card([
            dbc.CardBody([
                html.H5([html.I(className="bi bi-bar-chart-line me-2"), "1. Phổ điểm hệ thống"], className="card-title"),
                dcc.Graph(
                    figure=fig_overall, 
                    config={
                        'displayModeBar': True,  # Hiện thanh công cụ khi di chuột/chạm vào
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d'], # Bỏ mấy cái không cần thiết
                        'scrollZoom': True,      # Cho phép dùng con lăn hoặc hai ngón tay zoom
                        'displaylogo': False,    # Tắt logo Plotly cho chuyên nghiệp
                        'responsive': True       # Tự co giãn theo khung
                    }
                )
            ])
        ], className="shadow-sm border-0 mb-4"),

        # --- 2 & 3. CẬN CẢNH (ZOOM) ---
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("2. Cận cảnh tại vùng điểm của bạn", className="fw-bold"),
                        dcc.Graph(figure=fig_comp, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm border-0 mb-4"), width=12, lg=6
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("3. Cận cảnh tại vùng điểm sàn", className="fw-bold"),
                        dcc.Graph(figure=fig_safety, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm border-0 mb-4"), width=12, lg=6
            ),
        ]),

        # --- 4. BẢNG TOP 20 TINH HOA ---
        # Bước 2: Đưa vào Component
        dbc.Card([
            dbc.CardHeader([
                html.I(className="bi bi-trophy me-2 text-warning"),
                "4. Top 20 thí sinh dẫn đầu" # Bỏ bớt chữ cho ngắn
            ], className="fw-bold"),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df_top20_display.to_dicts(),
                    columns=[{"name": i, "id": i} for i in df_top20_display.columns],
                    # ... các phần style giữ nguyên như Mus viết ...
                    style_cell={
                        'minWidth': '60px', 'width': '100px', 'maxWidth': '150px', # Siết thêm tí nữa
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'fontSize': '11px', # Giảm 1 size cho mobile
                        'padding': '6px'    # Giảm padding để bảng "gầy" hơn
                    },
                )
            ], className="p-1") # Giảm padding của CardBody để tận dụng không gian
        ], className="shadow-sm border-0 mb-5")
    ])
