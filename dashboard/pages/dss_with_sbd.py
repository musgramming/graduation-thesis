from dash import register_page

register_page(
    __name__,
    order=2,
    path="/dss-with-sbd",
    name='Tra cứu theo SBD',
    title="Dự báo thứ hạng",
    description="Trang này cho phép các sĩ tử nhập điểm của mình và so sánh điểm của mình so với cả nước",
)

from page_modules.dss_with_sbd.layout import layout
import page_modules.dss_with_sbd.callbacks