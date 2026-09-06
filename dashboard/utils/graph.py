import plotly.graph_objects as go

def build_strict_graph(fig: go.Figure) -> go.Figure:
    """
    Chuẩn hóa giao diện cho biểu đồ Plotly theo phong cách tối giản, 
    chuyên nghiệp và đồng bộ trên toàn hệ thống Dashboard.

    Args:
        fig (go.Figure): Đối tượng biểu đồ Plotly cần định dạng.

    Returns:
        go.Figure: Biểu đồ sau khi được cập nhật layout.
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
    
    # Chuẩn hóa đường lưới (grid) nhạt hơn để không rối mắt
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