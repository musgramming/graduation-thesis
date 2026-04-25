import plotly.graph_objects as go

def build_strict_graph(fig: go.Figure = None) -> go.Figure:
    if fig is None:
        fig = go.Figure()
        is_empty = True
    else:
        is_empty = False

    fig.update_layout(
        xaxis=dict(
            # Cho phép zoom (để xem kỹ vùng điểm) nhưng chặn kéo (pan)
            fixedrange=False, 
            showgrid=True,    # Nên hiện grid mờ để dễ dóng hàng trên màn hình nhỏ
            gridcolor='#f0f0f0',
            zeroline=False, 
            visible=not is_empty,
            tickfont=dict(size=10) # Chữ nhỏ lại một chút cho mobile
        ),
        yaxis=dict(
            fixedrange=True,  # Trục Y thường không cần zoom để giữ tỷ lệ phổ điểm
            showgrid=True,
            gridcolor='#f0f0f0',
            zeroline=False, 
            visible=not is_empty,
            tickfont=dict(size=10)
        ),
        # Chế độ hover "x unified" rất tốt cho mobile, giữ nguyên nhé!
        hovermode='x unified',
        
        # 'select' cho phép dùng tay quét một vùng để zoom vào
        dragmode='zoom', 
        
        paper_bgcolor='rgba(0,0,0,0)', # Để trong suốt để khớp với màu nền Card
        plot_bgcolor='rgba(0,0,0,0)',
        
        # Tăng lề trên một chút để không đè vào Annotation
        margin=dict(l=5, r=5, t=40, b=5),
        
        # Tối ưu hóa font chữ tổng thể
        font=dict(family="Arial, sans-serif", size=12),
        
        # Để biểu đồ tự thích ứng chiều ngang
        autosize=True
    )

    return fig
