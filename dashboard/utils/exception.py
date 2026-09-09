import os
from typing import Never
from dash.exceptions import PreventUpdate

from direction.exception import DashModeException


class DashMacroError(Exception):
    pass


class TodoError(DashMacroError):
    pass


class UnimplementedError(DashMacroError):
    pass


class UnreachableDevelopmentError(DashMacroError):
    pass


class UnreachableProductionError(PreventUpdate):
    pass


def todo(message: str = "not yet implemented") -> Never:
    raise TodoError(message)


def unimplemented(message: str = "not implemented") -> Never:
    raise UnimplementedError(message)


def unreachable(message: str = "entered an unreachable branch", *, strict: bool = False) -> Never:
    """
    strict=True: Bất kể môi trường là gì, cứ chạm vào là CRASH (Phục vụ lỗi vi phạm bất biến tối cao).
    strict=False: Tuân theo biến môi trường (Dev thì crash, Prod thì PreventUpdate).
    """
    if strict:
        raise UnreachableDevelopmentError(message)

    mode = os.getenv("DASH_MODE") or os.getenv("MODE") or os.getenv("FLASK_ENV", "development")
    mode = mode.lower().strip()

    if mode not in ("development", "production"):
        raise DashModeException(
            f"Lỗi cấu hình: Biến môi trường chế độ ('{mode}') không hợp lệ. "
            "Chỉ chấp nhận giá trị 'development' hoặc 'production'."
        )

    if mode == "production":
        raise UnreachableProductionError(message)
    
    raise UnreachableDevelopmentError(message)