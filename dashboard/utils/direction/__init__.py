from .engines.direction_plain import PageDirection as PageDirectionPlain
from .engines.direction_secure import PageDirection as PageDirectionSecure

from ..read_mode import get_standardized_mode

mode = get_standardized_mode()

# Chọn module tương ứng dựa trên mode đã được xác thực
PageDirection = PageDirectionSecure if mode == "production" else PageDirectionPlain


GLOBAL_DIRECTION = PageDirection()
__all__ = ["GLOBAL_DIRECTION"]