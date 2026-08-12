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
        description="Chạy pipeline xử lý dữ liệu THPTQG."
    )

    parser.add_argument(
        "-y",
        "--year",
        type=int,
        required=True,
        help="Năm dữ liệu cần xử lý.",
    )

    return parser.parse_args()


# ============================================================
# Validation
# ============================================================

def validate_year(year: int) -> bool:
    """Kiểm tra năm dữ liệu."""

    if year < 2025:
        print(
            f"ERROR: Năm dữ liệu phải từ 2025 trở đi: {year}",
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
        OUTPUT_DIR / "bang-diem",
        OUTPUT_DIR / "bang-diem-to-hop",
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

    return VENV_DIR / "Scripts" / "python.exe"


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
) -> int:
    """Chạy pipeline.py và trả về exit code."""

    print(
        f"\nĐang chạy pipeline cho năm {year}...\n"
    )

    result = subprocess.run(
        [
            str(python_executable),
            str(PIPELINE_FILE),
            "--year",
            str(year),
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
    year = args.year

    # --------------------------------------------------------
    # B2. Validate year
    # --------------------------------------------------------

    if not validate_year(year):
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

        return run_pipeline(
            python_executable,
            year,
        )

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
