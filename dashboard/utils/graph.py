import plotly.graph_objects as go
from .exception import todo, unimplemented, unreachable




def build_strict_graph(fig: go.Figure) -> go.Figure:
    """
    Chuẩn hóa giao diện cho biểu đồ Plotly theo phong cách tối giản, 
    chuyên nghiệp và đồng bộ trên toàn hệ thống Dashboard.
    """
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=20, t=30, b=40),
        font=dict(
            family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
            size=12,
            color="#212529"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#f1f3f5",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#dee2e6"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#f1f3f5",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="#dee2e6"
    )

    return fig





def create_empty_figure(message="Không có dữ liệu phù hợp") -> go.Figure:
    """Tạo một biểu đồ trống nhưng có chữ thông báo ở giữa"""
    fig = go.Figure()
    
    # 1. Chạy chuẩn hóa layout chung trước
    fig = build_strict_graph(fig)
    
    # 2. Sau đó mới ẩn trục tọa độ đi để biểu đồ trống hoàn toàn sạch sẽ
    fig.update_xaxes(visible=False, showgrid=False)
    fig.update_yaxes(visible=False, showgrid=False)
    
    # 3. Thêm chữ thông báo vào giữa biểu đồ
    fig.add_annotation(
        text=message,
        xref="paper", 
        yref="paper",
        x=0.5, 
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#6c757d")
    )
    
    return fig