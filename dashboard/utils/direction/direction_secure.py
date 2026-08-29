from dash import MATCH, ALL, ALLSMALLER
import inspect
import os
import hmac
import hashlib
import random
import platform
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Union

from .utils.hashing import __RANDOM_SALT, __RANDOM_SALT_HEX, _hashing





class PageDirection:
    """
    Hệ thống quản lý định danh (Registry Hub) bảo mật cao cho Dash Multi-page App.
    Sử dụng cơ chế hashing để ngăn chặn việc rò rỉ cấu trúc logic App phía Client.
    """
    def __init__(self) -> None:
        """
        Khởi tạo kho lưu trữ các trang (Page Registry).
        """
        self.__pages: Dict[str, '_SingleDirection'] = {}


    def __get_page_hash(self, page_name: Optional[str] = None) -> str:
        """
        [Private] Xác định Namespace của trang dựa trên tên module hoặc tên tùy chỉnh.
        
        Args:
            page_name (Optional[str]): 
                - Nếu cung cấp: Dùng chuỗi này làm định danh trang.
                - Nếu None: Tự động truy vết Call Stack tầng thứ 2 để lấy tên file .py thực thi.
        
        Returns:
            str: Mã băm đại diện cho Namespace của trang.
        """
        if page_name is None:
            stack = inspect.stack()
            frame_info = stack[2]
            filename = frame_info.filename
            page_name = os.path.relpath(filename, os.getcwd()).replace(".py", "")
            
        return _hashing(page_name)


    def assign_page(self, page: Optional[str] = None) -> '_SingleDirection':
        """
        Khởi tạo và đăng ký đối tượng quản lý ID cho một trang cụ thể.
        
        Args:
            page (Optional[str]): Tên định danh trang thủ công.

        Returns:
            _SingleDirection: Instance quản lý ID dành riêng cho trang đã được băm hóa.
        
        Raises:
            Exception: Page đã tạo rồi
        """
        page_hash = self.__get_page_hash(page)
        if page_hash in self.__pages:
            raise Exception(f"Trang với mã hash {page_hash} đã được khởi tạo!")
        
        self.__pages[page_hash] = _SingleDirection(page_hash)
        return self.__pages[page_hash]


    def use_page(self, page: Optional[str] = None) -> '_SingleDirection':
        """
        Truy xuất bộ quản lý ID hiện có mà không tạo mới (Alias của assign_page).
        
        Args:
            page (Optional[str]): Tên định danh trang cần truy xuất.

        Returns:
            _SingleDirection: Instance quản lý ID tương ứng.
        
        Raises:
            Exception: Page chưa được đăng ký
        """        
        page_hash = self.__get_page_hash(page)
        if page_hash not in self.__pages:
            raise Exception(f"Trang {page_hash} chưa được đăng ký! Hãy gọi assign_page trước.")
        
        return self.__pages[page_hash]





class _SingleDirection:
    """
    Hệ thống tạo ID cục bộ (Scoped) đã được mã hóa cho từng trang đơn lẻ.
    Quản lý ánh xạ giữa tên ID thô (Server-side) và mã băm (Client-side).
    """
    def __init__(self, page_hash: str) -> None:
        """
        Khởi tạo trình quản lý ID cho một Namespace trang.

        Args:
            page_hash (str): Mã băm đại diện cho trang.
        """
        self.__page: str = page_hash
        self.__table_of_id: Dict[str, Optional[int]] = {}  
        self.__hash_to_id: Dict[str, str] = {} 
        self.__id_to_hash: Dict[str, str] = {} 


    def __build_dict(self, id_hash: str, index: Any = None) -> Dict[str, Any]:
        """
        [Private] Xây dựng cấu trúc ID Dictionary chuẩn Dash Pattern-matching.
        Chuyển đổi index 'None' thành 'static' để đảm bảo tính hợp lệ trong Dash.

        Args:
            id_hash (str): Mã băm của ID định danh.
            index (Any): Chỉ số index hoặc các Marker (MATCH, ALL, ALLSMALLER).

        Returns:
            Dict[str, Any]: Dictionary ID đã sẵn sàng để sử dụng trong Dash Components.
        """
        render_index = index if index is not None else "static"
        return {
            "type": self.__page,
            "id_name": id_hash,
            "index": render_index
        }


    def assign_id(self, id_name: str, is_dynamic: bool = False) -> Dict[str, Any]:
        """
        Đăng ký và băm một ID mới vào hệ thống của trang.
        
        Args:
            id_name (str): Tên ID chức năng (ví dụ: 'submit-button').
            is_dynamic (bool): Nếu True, ID sẽ hỗ trợ cơ chế tăng index (Pattern-matching).
            
        Returns:
            Dict[str, Any]: Dictionary ID chứa mã băm đã được đăng ký.

        Raises:
            Exception: Nếu ID trống hoặc đã tồn tại trên trang này.
        """

        if not id_name: 
            raise Exception("Không được để ID trống")

        if id_name in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' đã tồn tại")
        
        id_hash = _hashing(id_name)
        self.__id_to_hash[id_name] = id_hash
        self.__hash_to_id[id_hash] = id_name
        self.__table_of_id[id_hash] = 1 if is_dynamic else None

        return self.__build_dict(id_hash, self.__table_of_id[id_hash])


    def next_index(self, id_name: str) -> Dict[str, Any]:
        """
        Tăng chỉ số index cho một ID động đã đăng ký.
        Thường dùng khi render thêm các hàng dữ liệu hoặc component mới vào giao diện.

        Args:
            id_name (str): Tên ID gốc của component.

        Returns:
            Dict[str, Any]: Dictionary ID với chỉ số index mới.
        
        Raises:
            Exception: Nếu ID chưa khai báo, hoặc là ID tĩnh.
        """
        if not id_name: 
            raise Exception("Không được để ID trống")
        
        if id_name not in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại để sinh thêm index")

        id_hash = self.__id_to_hash[id_name]
        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' là id tĩnh. Không thể dùng next_index()")
        
        self.__table_of_id[id_hash] += 1
        return self.__build_dict(id_hash, self.__table_of_id[id_hash])


    def use_id(self, id_name: str, index: Union[int, Any, None] = None) -> Dict[str, Any]:
        """
        Sử dụng lại một ID đã được đăng ký trước đó.
        
        Args:
            id_name (str): Tên ID gốc cần truy xuất.
            index (Union[int, Any, None]): Chỉ số index cụ thể hoặc các Marker Dash.
            
        Returns:
            Dict[str, Any]: Dictionary ID hoàn chỉnh.

        Raises:
            Exception: 
                - ID chưa được đăng ký qua `assign_id`.
                - Truyền index cho ID tĩnh hoặc bỏ trống index cho ID động.
                - Truy cập vào một index chưa được khởi tạo (OutOfBounds).
        """
        if not id_name: 
            raise Exception("Không được để ID trống")
        
        if id_name not in self.__id_to_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại")
        
        id_hash = self.__id_to_hash[id_name]
        val_in_table = self.__table_of_id[id_hash]

        if val_in_table is None:
            if index is not None:
                raise Exception(f"ID '{id_name}' là dạng static. Không được truyền index")
            return self.__build_dict(id_hash, index=None)
        
        if index is None:
            raise Exception(f"ID '{id_name}' là dạng dynamic. Phải truyền index")
        
        if isinstance(index, int) and val_in_table < index:
            raise Exception(f"Index {index} chưa được khởi tạo cho ID '{id_name}'")
        
        return self.__build_dict(id_hash, index)


    def reduce_index(self, id_name : str) -> Dict[str, Any]:
        """
        Giảm chỉ số index hiện tại của một ID động.
        Sử dụng khi xóa bỏ component cuối cùng trong một danh sách động.

        Args:
            id_name (str): Tên ID gốc cần giảm chỉ số.

        Returns:
            Dict[str, Any]: Dictionary ID với chỉ số index đã giảm.

        Raises:
            Exception: Nếu ID không tồn tại, là ID tĩnh, hoặc đang ở chỉ số tối thiểu (1).
        """
        id_hash = self.__id_to_hash.get(id_name)
        if not id_hash:
            raise Exception(f"ID '{id_name}' chưa tồn tại")
        
        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' là id tĩnh.")
        
        if self.__table_of_id[id_hash] <= 1:
            raise Exception(f"ID '{id_name}' không thể giảm thêm index.")

        self.__table_of_id[id_hash] -= 1
        return self.__build_dict(id_hash, self.__table_of_id[id_hash])


    def match(self, id_name : str) -> Dict[str, Any]:
        """
        Tạo khuôn mẫu định danh cho cơ chế khớp bộ bộ (dash.MATCH).
        
        Sử dụng trong Callback để tạo mối liên kết 1-1 giữa Input và Output có cùng chỉ số index.

        Args:
            id_name (str): Tên định danh gốc đã đăng ký.

        Returns:
            Dict[str, Any]: Dictionary ID chứa mã băm với trường 'index' là hằng số MATCH.

        Raises:
            Exception: 
                - Nếu id_name trống hoặc chưa được đăng ký.
                - Nếu là ID tĩnh: Ngăn chặn vì MATCH trên giá trị tĩnh sẽ không bao giờ kích hoạt Callback 
                  (vô nghĩa về mặt vận hành).
        """
        if not id_name:
            raise Exception("Không được để ID trống")

        id_hash = self.__id_to_hash.get(id_name)
        
        if not id_hash:
            raise Exception(f"ID '{id_name}' không tồn tại")

        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' là ID tĩnh, không hợp lệ cho MATCH")
        
        return self.__build_dict(id_hash, index=MATCH)


    def all(self, id_name : str) -> Dict[str, Any]:
        """
        Tạo khuôn mẫu định danh cho cơ chế khớp toàn bộ (dash.ALL).
        
        Dùng để thu thập dữ liệu từ tất cả các thành phần có cùng ID băm dưới dạng một danh sách (List).

        Args:
            id_name (str): Tên định danh gốc đã đăng ký.

        Returns:
            Dict[str, Any]: Dictionary ID với trường 'index' là hằng số ALL.

        Raises:
            Exception: 
                - Nếu id_name trống hoặc chưa được đăng ký.
                - Nếu ID là dạng tĩnh: Hệ thống chủ động chặn để triệt tiêu cấu trúc dữ liệu đơn tử 
                  (single-element list), tránh gây nhiễu loạn và phức tạp hóa logic xử lý trong Callback.
        """
        if not id_name:
            raise Exception("Không được để ID trống")

        id_hash = self.__id_to_hash.get(id_name)
        
        if not id_hash:
            raise Exception(f"ID '{id_name}' không tồn tại")

        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' là ID tĩnh, không hợp lệ cho ALL")
            
        return self.__build_dict(id_hash, index=ALL)


    def allsmaller(self, id_name : str) -> Dict[str, Any]:
        """
        Tạo khuôn mẫu định danh cho cơ chế khớp thứ bậc (dash.ALLSMALLER).
        
        Phản hồi với các thành phần có chỉ số index nhỏ hơn thành phần đang kích hoạt Callback.

        Args:
            id_name (str): Tên định danh gốc đã đăng ký.

        Returns:
            Dict[str, Any]: Dictionary ID với trường 'index' là hằng số ALLSMALLER.

        Raises:
            Exception: 
                - Nếu id_name trống hoặc chưa được đăng ký.
                - Nếu ID không phải dạng động: Cơ chế ALLSMALLER yêu cầu tính tuần tự của index để thực hiện so sánh toán học.
        """
        if not id_name:
            raise Exception("Không được để ID trống")

        id_hash = self.__id_to_hash.get(id_name)
        
        if not id_hash:
            raise Exception(f"ID '{id_name}' không tồn tại")

        if self.__table_of_id[id_hash] is None:
            raise Exception(f"ID '{id_name}' là ID tĩnh, không hợp lệ cho ALLSMALLER")
            
        return self.__build_dict(id_hash, index=ALLSMALLER)