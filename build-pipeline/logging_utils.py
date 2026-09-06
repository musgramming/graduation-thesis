import logging
from pathlib import Path





# ============================================================
# Pipeline utilities
# ============================================================

def format_duration(seconds: float) -> str:
    """
    Chuyển số giây thành định dạng HH:MM:SS.
    """
    seconds = int(seconds)

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"





def setup_logging(year: int) -> logging.Logger:
    """
    Khởi tạo logger cho pipeline.

    Log được ghi đồng thời:
    - Ra terminal
    - Vào file ./logs/pipeline-{year}.log
    """

    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.INFO)

    # Tránh thêm Handler nhiều lần nếu hàm được gọi lại.
    if logger.handlers:
        return logger

    # --------------------------------------------------------
    # Format cho file log
    # --------------------------------------------------------

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --------------------------------------------------------
    # Format cho terminal
    # --------------------------------------------------------

    console_formatter = logging.Formatter(
        fmt="%(message)s"
    )

    # --------------------------------------------------------
    # File handler
    # --------------------------------------------------------

    file_handler = logging.FileHandler(
        log_dir / f"pipeline-{year}.log",
        encoding="utf-8",
    )

    file_handler.setFormatter(file_formatter)

    # --------------------------------------------------------
    # Console handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # --------------------------------------------------------
    # Đăng ký handlers
    # --------------------------------------------------------

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger





def log_step(
    logger: logging.Logger,
    step: int,
    total_steps: int,
    message: str,
    detail: str | None = None,
):
    """
    In thông tin bắt đầu một bước pipeline.
    """

    logger.info(
        f"[{step:02}/{total_steps:02}] {message}"
    )

    if detail:
        logger.info(
            f"       └─ {detail}"
        )





def log_success(
    logger: logging.Logger,
    elapsed: float,
):
    """
    In thông tin hoàn thành một bước pipeline.
    """

    logger.info(
        f"       ✓ Hoàn thành"
        f"{' ' * 25}"
        f"{format_duration(elapsed)}"
    )





def log_pipeline_success(
    logger: logging.Logger,
    elapsed: float,
):
    """
    In thông tin hoàn thành toàn bộ pipeline.
    """

    logger.info("")
    logger.info("─" * 70)
    logger.info("✓ PIPELINE HOÀN TẤT")
    logger.info(
        f"  Tổng thời gian: {format_duration(elapsed)}"
    )
    logger.info("─" * 70)
