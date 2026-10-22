import functools
import gc
import time
import traceback
import tracemalloc
from typing import Callable, Any


def export_performance(func: Callable) -> Callable:
    """
    Decorator đo lường thời gian thực thi (latency), RAM hiện tại và RAM đỉnh điểm (Peak RAM)
    cho các callback/dịch vụ, đồng thời ép thu gom rác bộ nhớ (gc.collect) sau mỗi lượt chạy.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 1. Bắt đầu đo bộ nhớ RAM & Thời gian
        tracemalloc.start()
        start_time = time.perf_counter()

        try:
            # 2. Thực thi hàm gốc
            result = func(*args, **kwargs)

            # 3. Tính toán thông số sau khi hoàn thành
            end_time = time.perf_counter()
            current_ram, peak_ram = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            elapsed_time = end_time - start_time
            current_mb = current_ram / (1024 * 1024)
            peak_mb = peak_ram / (1024 * 1024)

            # 4. In thông số ra terminal / Render logs
            print(
                f"⚡ [{func.__name__}] "
                f"Thời gian: {elapsed_time:.4f}s | "
                f"RAM hiện tại: {current_mb:.2f} MB | "
                f"RAM Đỉnh điểm (Peak): {peak_mb:.2f} MB"
            )

            # 5. Ép dọn rác ngay lập tức để trả bộ nhớ cho hệ thống
            gc.collect()

            return result

        except Exception as e:
            # Dọn dẹp tracemalloc & gc kể cả khi xảy ra lỗi
            tracemalloc.stop()
            print(f"❌ [LỖI TRONG {func.__name__}]: {e}")
            traceback.print_exc()
            gc.collect()
            raise e

    return wrapper