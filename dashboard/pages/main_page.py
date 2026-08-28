from dash import register_page
from page_modules.main_page.layout import layout


register_page(
    __name__,
    path="/",
    order=1,
    redirect_from=["/main_page"],
    name="Trang chủ",
    title="Hệ thống Phân tích Phổ điểm thi Tốt nghiệp THPT",
    description="Phân tích vị thế điểm số và dự báo tổ hợp",
    layout=layout
)
