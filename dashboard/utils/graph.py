import plotly.graph_objects as go

def build_strict_graph(fig: go.Figure = None) -> go.Figure:
    if fig is None:
        fig = go.Figure()
        is_empty = True
    else:
        is_empty = False

    fig.update_layout(
        xaxis=dict(
            fixedrange=False, 
            showgrid=True, 
            gridcolor='#f0f0f0',
            zeroline=False, 
            visible=not is_empty,
            tickfont=dict(size=10) # Chữ nhỏ lại một chút cho mobile
        ),
        yaxis=dict(
            fixedrange=True, 
            showgrid=True,
            gridcolor='#f0f0f0',
            zeroline=False, 
            visible=not is_empty,
            tickfont=dict(size=10)
        ),

        hovermode='x unified',
        
        dragmode='zoom', 
        
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        margin=dict(l=5, r=5, t=40, b=5),
        
        font=dict(family="Arial, sans-serif", size=12),
        
        autosize=True
    )

    return fig
