from dash import register_page

register_page(
    __name__,
    order=3,
    path="/dss-without-sbd",
    name='Phân tích tổ hợp điểm',
    title="Xây dựng kịch bản",
    description="Trang này cho phép nhập điểm của mình để tính toán kịch bản cho hợp lý"
)



from page_modules.dss_without_sbd.layout import layout
import page_modules.dss_without_sbd.callbacks