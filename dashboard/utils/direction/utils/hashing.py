import os
import hmac
import hashlib
import random
import platform
import subprocess
import getpass
from dotenv import load_dotenv





# --- Khởi tạo hệ thống bảo mật mật mã (Cryptographic Initialization) ---

os.makedirs("utils/direction", exist_ok=True)
dotenv_path = "utils/direction/.env"

if not os.path.exists(dotenv_path):
    with open(dotenv_path, "w") as f:
        salt = random.getrandbits(1024).to_bytes(128, 'big').hex()
        f.write(f"RANDOM_SALT={salt}")




def protect_env_file(filepath: str):
    """
    Thiết lập quyền truy cập file ở mức hệ điều hành (OS-level permissions).
    Đảm bảo chỉ người dùng sở hữu tiến trình hiện tại mới có quyền đọc/ghi file Salt.
    """
    try:
        if platform.system() == "Windows":
            user = getpass.getuser()
            # Gộp chung /inheritance:r và /grant vào một lệnh duy nhất để tránh lặp lại
            cmd = f'icacls "{filepath}" /inheritance:r /grant:r {user}:(R,W)'
            subprocess.run(
                cmd, 
                shell=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        else:
            os.chmod(filepath, 0o600)
    except Exception:
        pass


protect_env_file(dotenv_path)


load_dotenv(dotenv_path)
__RANDOM_SALT_HEX = os.getenv("RANDOM_SALT")
__RANDOM_SALT = bytes.fromhex(__RANDOM_SALT_HEX) if __RANDOM_SALT_HEX else b'default_salt_if_failed'





def _hashing(string: str) -> str:
    """
    Thực hiện băm mật mã HMAC-SHA512 để bảo mật định danh.
    Chuyển đổi dữ liệu nhạy cảm (tên module, ID gốc) thành mã băm một chiều.

    Args:
        string (str): Chuỗi thô cần mã hóa.

    Returns:
        str: Chuỗi 128 ký tự Hex đại diện cho mã băm SHA512.
    """
    hash_object = hmac.new(
        key=__RANDOM_SALT, 
        msg=string.encode(), 
        digestmod=hashlib.sha512
    )
    return hash_object.hexdigest()
