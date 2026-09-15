from dash import register_page


register_page(
    __name__,
    path="/stat",
    name="Thống kê",
    title="Thống kê tỉnh thành",
    description="Thống kê tỉnh thành",
)

from page_modules.stat_provinces.layout import layout
