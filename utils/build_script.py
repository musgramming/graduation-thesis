from typing import Literal

from dash import html, dcc, dash_table
import plotly.graph_objects as go
import plotly.express as px
import polars as pl
import dash_bootstrap_components as dbc

from data import BANG_DIEM
from .graph import build_strict_graph





def filter_raw_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    return BANG_DIEM[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) &
        (pl.col("Tổng điểm") >= floor_score) &
        (pl.col("Hợp lệ") == True)
    ).with_columns(
        pl.col("Tổng điểm").alias("Điểm quy đổi")
    )





def filter_max_min(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
    # B1: Lọc cơ bản
    df = BANG_DIEM[year].filter(
        (pl.col("Tổ hợp").is_in(combs)) &
        (pl.col("Hợp lệ") == True)
    )
    
    # B2: Quy đổi max-min
    min_max_table = df.group_by("Tổ hợp").agg(
        [
            pl.col("Tổng điểm").min().alias("min"),
            pl.col("Tổng điểm").max().alias("max")
        ]
    )
    df = (
        df.join(min_max_table, on="Tổ hợp")
        .with_columns(
            pl.when(pl.col("max") > pl.col("min"))
                .then((pl.col("Tổng điểm") - pl.col("min")) / (pl.col("max") - pl.col("min")) * 30)
                .otherwise(30.0)
                .round(3)
                .alias("Điểm quy đổi")
        )
        .drop(["min", "max"])
        .filter(
            pl.col("Điểm quy đổi") >= floor_score
        )
    )

    return df





def filter_z_score(year: int, floor_score : float, combs : list[str]) -> pl.LazyFrame:
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
    lf = BANG_DIEM[year].filter(pl.col("Tổ hợp").is_in(combs))
    
    # Hằng số quy đổi để giữ thang 0-30 nhưng không làm mất đặc tính phân phối
    # Giả sử: Mean/Median nằm ở 15 điểm, mỗi 1 Std/IQR dãn ra 5 điểm
    ANCHOR = 15.0
    SCALE_FACTOR = 5.0 

    if mode == "raw-score":
        return lf.with_columns(pl.col("Tổng điểm").alias("Điểm quy đổi"))

    if mode == "min-max":
        # Min-Max nên dùng Max/Min của TOÀN QUỐC (ví dụ 0 và 30) để thấy độ lệch của tổ hợp
        GLOBAL_MIN, GLOBAL_MAX = 0.0, 30.0
        return lf.with_columns(
            ((pl.col("Tổng điểm") - GLOBAL_MIN) / (GLOBAL_MAX - GLOBAL_MIN) * 30)
            .round(3)
            .alias("Điểm quy đổi")
        )

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
            - "min-max": Tuyến tính hóa điểm số về thang [15, 30] (Dễ hiểu cho lớp 10, 11).
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
        return html.Div("Không tìm thấy dữ liệu phù hợp.")

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
        # Header báo cáo
        html.Div([
            html.H2(f"BÁO CÁO PHÂN TÍCH VỊ THẾ {year}", style={'textAlign': 'center', 'color': '#2c3e50', 'fontWeight': 'bold'}),
            html.P(f"Phương pháp định vị: {mode.upper()}", style={'textAlign': 'center', 'marginTop': '-10px', 'color': '#95a5a6'}),
        ], className="mb-4"),

        # Cụm Badge Vị Thế
        html.Div([
            dbc.Row([
                # Cột 1: Vị thế tổng quát
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("VỊ THẾ TỔNG QUÁT", className="fw-bold text-center bg-light"),
                        dbc.CardBody([
                            html.Div([
                                dbc.Badge(f"Hạng {overall_rank:,} / {total_count:,}", color="primary", className="me-2 p-2", style={'fontSize': '16px'}),
                                dbc.Badge(f"PR: {overall_pr:.2f}%", color="info", className="p-2", style={'fontSize': '16px'}),
                            ], className="d-flex justify-content-center mb-2"),
                            html.Small("So với tất cả thí sinh thi cùng tổ hợp", className="text-muted d-block text-center")
                        ])
                    ], className="shadow-sm border-0") # shadow-sm tạo đổ bóng nhẹ, border-0 để bỏ viền mặc định nếu thích
                ], width=12, lg=6, className="mb-3"),

                # Cột 2: Vị thế cạnh tranh
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("VỊ THẾ CẠNH TRANH", className="fw-bold text-center bg-light"),
                        dbc.CardBody([
                            html.Div([
                                dbc.Badge(f"Hạng {floor_rank:,} / {total_on_floor:,}", color="dark", className="me-2 p-2", style={'fontSize': '16px'}),
                                dbc.Badge(
                                    f"An toàn: {floor_pr:.2f}%", 
                                    color="success" if floor_pr > 50 else "warning", 
                                    className="p-2", 
                                    style={'fontSize': '16px'}
                                ),
                            ], className="d-flex justify-content-center mb-2"),
                            html.Small(f"Chỉ tính người đủ sàn (>= {floor_score})", className="text-muted d-block text-center")
                        ])
                    ], className="shadow-sm border-0")
                ], width=12, lg=6, className="mb-3")
            ], className="g-4 mb-4")
        ]),

        
        # Biểu đồ
        html.Div([
            html.H4("1. Phổ điểm hệ thống"),
            dcc.Graph(
                figure=fig_overall, 
                config={'displayModeBar': False}
            )
        ], className="mb-4"),

        html.Div([
            html.Div(
                [
                    html.H4("2. Cận cảnh điểm của bạn"),
                    dcc.Graph(
                        figure=fig_comp, 
                        config={'displayModeBar': False}
                    )
                ], style={
                    'width': '49%', 
                    'display': 'inline-block'
                }
            ),

            html.Div(
                [
                    html.H4("3. Cận cảnh điểm sàn"),
                    dcc.Graph(
                        figure=fig_safety, 
                        config={'displayModeBar': False}
                    )
                ], style={
                    'width': '49%', 
                    'display': 'inline-block', 
                    'float': 'right'
                }
            )
        ], className="mb-4", style={'overflow': 'hidden'}),

        # Bảng Top 20
        html.Div([
            html.H4("4. Top 20 thí sinh dẫn đầu (Quy đổi)"),
            dash_table.DataTable(
                data=df_top20.with_columns(
                    pl.col("Tổ hợp_chọn").alias("Tổ hợp có điểm cao nhất")
                ).to_dicts(),
                columns=[{"name": i, "id": i} for i in df_top20.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '12px'},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'}
            )
        ])
    ], style={'padding': '30px', 'backgroundColor': '#f8f9fa'})
