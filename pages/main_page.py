from dash import html, register_page

register_page(
    __name__,
    path="/",
    redirect_from=["/main_page"],
    title="Trang chủ",
    description="Trang chủ",
    image="./images/home.png"
)

layout = html.Div([
    html.P("Hello world")
])
