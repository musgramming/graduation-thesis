import plotly.graph_objects as go

def build_strict_graph(fig: go.Figure = None) -> go.Figure:
    """
    Hàm 2-trong-1: 
    - Nếu không truyền fig: Tạo đồ thị trống đã được 'phong ấn'.
    - Nếu truyền fig: Áp dụng layout 'phong ấn' lên đồ thị đó.
    """
    if fig is None:
        fig = go.Figure()
        is_empty = True
    else:
        is_empty = False

    fig.update_layout(
        xaxis=dict(
            fixedrange=True, 
            showgrid=False, 
            zeroline=False, 
            visible=not is_empty 
        ),
        yaxis=dict(
            fixedrange=True, 
            showgrid=False, 
            zeroline=False, 
            visible=not is_empty
        ),
        dragmode=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode='x unified'
    )

    return fig
