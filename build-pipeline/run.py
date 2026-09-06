import argparse
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

VENV_DIR = Path(".venv_pipeline")

REQUIREMENTS_FILE = Path("requirements.txt")
PIPELINE_FILE = Path("pipeline.py")

OUTPUT_DIR = Path("output")





# ============================================================
# Argument
# ============================================================

def parse_arguments() -> argparse.Namespace:
    """Đọc tham số command line."""

    parser = argparse.ArgumentParser(
        description="Chạy pipeline xử lý dữ liệu THPTQG cho nhiều năm."
    )

    parser.add_argument(
        "-y",
        "--years",
        type=int,
        nargs="+",
        required=True,
        help=(
            "Danh sách các năm dữ liệu cần xử lý "
            "(ví dụ: -y 2025 2026 hoặc -y 2025)."
        ),
    )

    parser.add_argument(
        "--level",
        type=int,
        default=21,
        help=(
            "Mức compression level của Zstandard khi ghi Parquet "
            "(mặc định: 21)."
        ),
    )

    return parser.parse_args()





# ============================================================
# Validation
# ============================================================

def validate_years(years: list[int]) -> bool:
    """Kiểm tra danh sách năm dữ liệu."""

    valid = True

    for year in years:
        if year < 2025:
            print(
                f"ERROR: Năm dữ liệu phải từ 2025 trở đi: {year}",
                file=sys.stderr,
            )
            valid = False

    return valid





def validate_level(level: int) -> bool:
    """Kiểm tra compression level."""

    if level < 1:
        print(
            f"ERROR: Compression level phải lớn hơn hoặc bằng 1: {level}",
            file=sys.stderr,
        )
        return False

    return True





# ============================================================
# Prepare directories
# ============================================================

def prepare_directories() -> None:
    """Tạo các thư mục cần thiết."""

    directories = [
        OUTPUT_DIR / "bang_diem",
        OUTPUT_DIR / "bang_diem_to_hop",
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )





# ============================================================
# Virtual environment
# ============================================================

def create_virtual_environment() -> None:
    """Tạo virtual environment cho pipeline."""

    if VENV_DIR.exists():
        print("Đang xóa virtual environment cũ...")
        shutil.rmtree(VENV_DIR)

    print("Đang tạo virtual environment...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "venv",
            str(VENV_DIR),
        ],
        check=True,
    )





def get_python_executable() -> Path:
    """Lấy Python executable bên trong virtual environment."""

    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"

    return VENV_DIR / "bin" / "python"





# ============================================================
# Dependencies
# ============================================================

def install_requirements(
    python_executable: Path,
) -> None:
    """Cài đặt dependencies cho pipeline."""

    print("Đang cài đặt dependencies...")

    subprocess.run(
        [
            str(python_executable),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ],
        check=True,
    )

    subprocess.run(
        [
            str(python_executable),
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        check=True,
    )





# ============================================================
# Pipeline
# ============================================================

def run_pipeline(
    python_executable: Path,
    year: int,
    level: int,
) -> int:
    """Chạy pipeline.py cho một năm cụ thể."""

    print(
        f"\nĐang chạy pipeline cho năm {year} "
        f"với Zstandard compression level {level}...\n"
    )

    result = subprocess.run(
        [
            str(python_executable),
            str(PIPELINE_FILE),
            "--year",
            str(year),
            "--level",
            str(level),
        ],
        check=False,
    )

    return result.returncode





# ============================================================
# Main
# ============================================================

def main() -> int:

    # --------------------------------------------------------
    # B1. Parse arguments
    # --------------------------------------------------------

    args = parse_arguments()

    years = args.years
    level = args.level

    # --------------------------------------------------------
    # B2. Validate arguments
    # --------------------------------------------------------

    if not validate_years(years):
        return 1

    if not validate_level(level):
        return 1

    # --------------------------------------------------------
    # B3. Prepare directories
    # --------------------------------------------------------

    prepare_directories()

    print("Đã chuẩn bị thư mục output.")

    # --------------------------------------------------------
    # B4 → B6. Environment + pipeline
    # --------------------------------------------------------

    try:
        create_virtual_environment()

        python_executable = get_python_executable()

        install_requirements(
            python_executable
        )

        # Chạy lần lượt từng năm trong danh sách
        for year in years:

            exit_code = run_pipeline(
                python_executable,
                year,
                level,
            )

            if exit_code != 0:
                print(
                    f"\nERROR: Pipeline thất bại ở năm "
                    f"{year} với exit code {exit_code}.",
                    file=sys.stderr,
                )
                return exit_code

        return 0

    except subprocess.CalledProcessError as error:

        print(
            "\nERROR: Một subprocess đã thất bại.",
            file=sys.stderr,
        )

        return error.returncode

    finally:

        # ----------------------------------------------------
        # Cleanup
        # ----------------------------------------------------

        if VENV_DIR.exists():

            print(
                "\nĐang dọn dẹp virtual environment..."
            )

            shutil.rmtree(
                VENV_DIR,
                ignore_errors=True,
            )





# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())