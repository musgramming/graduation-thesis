class DashBaseException(Exception):
    """Base exception cho toàn bộ hệ thống Dash Architecture."""
    pass


class DashPageException(DashBaseException):
    """Lỗi phát sinh liên quan đến đăng ký hoặc truy xuất trang (Page)."""
    pass


class DashIdException(DashBaseException):
    """Lỗi phát sinh liên quan đến định danh, băm, hoặc index của Component ID."""
    pass


class DashModeException(DashBaseException):
    """Lỗi phát sinh liên quan đến cấu hình môi trường hệ thống (Development/Production)."""
    pass