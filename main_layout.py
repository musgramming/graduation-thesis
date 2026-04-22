import dash
from dash import html, page_container, Input, Output, State
import dash_bootstrap_components as dbc



STYLES = {
    "HEADER" : "bg-primary text-white text-center border-bottom shadow-sm p-3 fixed-top fs-3 text-uppercase",
    "MAIN" : "p-4 bg-white flex-grow-1 shadow-sm rounded-3 container overflow-auto",
    "FOOTER" : "p-2 bg-secondary text-white text-center fs-3 border-top fixed-bottom",
    "OUTER" : "d-flex flex-column vh-100 bg-light overflow-hidden",
    "NO-COPY" : {
        "user-select": "none",         
        "-webkit-user-select": "none",  
        "-moz-user-select": "none",     
        "-ms-user-select": "none",      
    }
}



header = html.Header([
    html.P("Đồ án tốt nghiệp")
], className=STYLES.get("HEADER", ""))



main = html.Main(
    [
        html.Div(page_container, className="pb-5")
    ], 
    className = STYLES.get("MAIN", ""),
    style={
        "marginTop": "80px",    # Đẩy xuống để không bị Header che (tùy độ cao header)
        "marginBottom": "80px", # Đẩy lên để không bị Footer che (tùy độ cao footer)
        "height": "calc(100vh - 140px)" # Tính toán chiều cao thực tế để hiện thanh cuộn
    }
)


footer = html.Footer([
    html.P("© By Mus ")
], className = STYLES.get("FOOTER", ""))



def get_security_script():
    try:
        with open("./assets/no_copy.js", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""



app_layout = html.Div([
    html.Noscript(
        html.Div([
            html.H1("CẢNH BÁO BẢO MẬT", style={"color": "red"}),
            html.P("Hệ thống phân tích dữ liệu yêu cầu JavaScript để hoạt động."),
            html.P("Vui lòng bật lại JavaScript để tiếp tục xem đồ án."),
            html.Img(src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjEx.../giphy.gif")
        ], style={"textAlign": "center", "marginTop": "20%"})
    ),

    html.Div(id="protected-content", children=[
        html.Script(
            get_security_script()
        ),
        header,
        main,
        footer,
    ])
], className=STYLES.get("OUTER", ""), style=STYLES.get("NO-COPY", ""))

