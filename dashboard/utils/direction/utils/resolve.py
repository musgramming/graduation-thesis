import sys
import os


def _resolve_page_name() -> str:
    """Hàm phụ trợ lấy tên trang tối ưu bằng sys._getframe."""
    frame = sys._getframe(2)
    filename = frame.f_code.co_filename
    
    rel_path = os.path.relpath(filename, os.getcwd())
    return rel_path.replace(os.sep, ".").replace(".py", "")