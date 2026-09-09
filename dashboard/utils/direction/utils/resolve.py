from pathlib import Path
import sys


def _resolve_page_name() -> str:
    """Lấy tên trang từ module gọi hàm, độc lập với hệ điều hành."""
    frame = sys._getframe(2)
    try:
        filename = frame.f_code.co_filename
    finally:
        del frame

    path = Path(filename).resolve()
    cwd = Path.cwd().resolve()

    try:
        relative = path.relative_to(cwd)
    except ValueError:
        # File nằm ngoài working directory
        relative = path

    return relative.with_suffix("").as_posix().replace("/", ".")