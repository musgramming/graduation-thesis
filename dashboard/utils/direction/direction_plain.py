from typing import Union, Any, Dict

from dash import MATCH, ALL, ALLSMALLER
import inspect
import os





class PageDirection:
    """
    Hệ thống quản lý định danh (ID Management System) trung tâm cho Dash Multi-page App.
    
    Lớp này đóng vai trò là một 'Registry Hub', tự động nhận diện ngữ cảnh trang 
    thông qua Call Stack và điều phối các bộ tạo ID riêng biệt cho từng trang.
    """


    def __init__(self):
        # Kho lưu trữ nội bộ duy trì trạng thái ID giữa các lần nạp trang
        self.__pages = {}


    def __get_page_name(self) -> str:
        stack = inspect.stack()
        frame_info = stack[2]
        filename = frame_info.filename
        
        rel_path = os.path.relpath(filename, os.getcwd())
        
        return rel_path.replace(os.sep, ".").replace(".py", "")


    def assign_page(self, page: str = None):
        """
        Khởi tạo hoặc lấy ra bộ quản lý ID cho một trang cụ thể.
        
        Args:
            page (str, optional): Tên trang thủ công. Nếu None, tự động lấy tên file.
            
        Returns:
            _SingleDirection: Đối tượng quản lý ID riêng biệt cho trang đó.
        
        Raises:
            Exception: Page đã được khởi tạo
        """
        page_name = page or self.__get_page_name()
        if page_name in self.__pages:
            raise RuntimeError(f"Page '{page_name}' đã được đăng ký trước đó!")
            
        self.__pages[page_name] = _SingleDirection(page_name)
        return self.__pages[page_name]


    def use_page(self, page: str = None):
        """
        Truy xuất bộ quản lý ID hiện có mà không làm thay đổi trạng thái đăng ký.
        Thường dùng trong các file callback hoặc module bổ trợ.
        
        Args:
            page (str, optional): Tên trang thủ công. Nếu None, tự động lấy tên file.
            
        Returns:
            _SingleDirection: Đối tượng quản lý ID riêng biệt cho trang đó.
        
        Raises:
            Exception: Page chưa được khởi tạo        
        """
        page_name = page or self.__get_page_name()
        if page_name not in self.__pages:
            raise LookupError(f"Không tìm thấy trang '{page_name}'. Bạn phải gọi assign_page() trước!")
            
        return self.__pages[page_name]





class _SingleDirection:
    """
    Bộ điều phối ID nội bộ cho từng trang (Internal Scoped ID Manager).
    
    Hỗ trợ quản lý ID tĩnh và ID động (Pattern-matching) với khả năng
    tự động tăng/giảm index và bảo mật Namespace bằng tên trang.
    """


    def __init__(self, page_name: str):
        self.__page = page_name
        self.__id_registry = dict() 


    def __build_dict(self, id_name : str, index: Union[None, int, Any] = None):
        """
        [private] Xây dựng cấu trúc ID Dictionary chuẩn Dash Pattern-matching.
        """
        render_index = index if index is not None else "static"
        return {
            "type": self.__page,
            "id_name": id_name,
            "index": render_index
        }


    def assign_id(self, id_name: str, is_dynamic: bool = False) -> Dict[str, Any]:
        """
        Đăng ký một ID mới vào hệ thống của trang.
        
        Args:
            id_name (str): Tên định danh chức năng (ví dụ: 'btn-submit').
            is_dynamic (bool): Nếu True, ID sẽ hỗ trợ cơ chế Pattern-matching.
            
        Raises:
            Exception: Nếu id_name trống
            Exception: Nếu ID đã được đăng ký trước đó trên cùng một trang.
        """
        if id_name is None:
            raise Exception("Không được để ID trống")
        
        if id_name in self.__id_registry:
            raise Exception(f"ID '{id_name}' đã được đăng ký!")
        
        self.__id_registry[id_name] = 1 if is_dynamic else None
        return self.__build_dict(id_name, self.__id_registry[id_name])


    def next_index(self, id_name: str) -> Dict[str, Any]:
        """
        Tăng index cho một ID động.

        Args:
            id_name: Tên ID đã được đăng ký với `is_dynamic=True`.

        Returns:
            dict: ID với index mới đã tăng.

        Raises:
            Exception: Nếu `id_name` trống
            Exception: Nếu `id_name` chưa được khai báo hoặc là ID tĩnh (static).
        """
        if id_name is None:
            raise Exception("Không được để ID trống")

        if id_name not in self.__id_registry or self.__id_registry[id_name] is None:
            raise Exception(f"ID '{id_name}' không phải là ID động.")
        
        self.__id_registry[id_name] += 1
        return self.__build_dict(id_name, self.__id_registry[id_name])


    def reduce_index(self, id_name: str):
        """
        Giảm index cho một ID động.

        Args:
            id_name: Tên ID cần giảm index.

        Returns:
            dict: ID với index đã giảm.

        Raises:
            Exception: Nếu ID trống
            Exception: Nếu ID chưa tồn tại.
            Exception: Nếu ID là tĩnh (không có index để giảm).
            Exception: Nếu index hiện tại đang là 1 (không thể giảm thêm).
        """
        if id_name is None:
            raise Exception("Không được để ID trống")
        
        if id_name not in self.__id_registry:
            raise Exception(f"ID '{id_name}' chưa tồn tại.")

        if self.__id_registry[id_name] is None:
            raise Exception(f"ID {id_name} là ID tĩnh.")

        if self.__id_registry[id_name] <= 1:
            raise Exception(f"ID {id_name} đạt giới hạn tối thiểu (1).")

        self.__id_registry[id_name] -= 1
        return self.__build_dict(id_name, self.__id_registry[id_name])


    def use_id(self, id_name: str, index: any = None) -> Dict[str, Any]:
        """
        Truy xuất ID để sử dụng trong Layout hoặc Callback.

        Args:
            id_name: Tên ID đã khai báo.
            index: Giá trị index cụ thể hoặc các Marker (MATCH, ALL, ALLSMALLER).

        Returns:
            dict: ID hoàn chỉnh.

        Raises:
            Exception: Nếu id_name trống        
            Exception: Nếu gọi một ID chưa từng được qua bước `assign_id`.
        """
        
        if id_name is None:
            raise Exception("Không được để ID trống")

        if id_name not in self.__id_registry:
            raise Exception(f"Lỗi: ID '{id_name}' chưa được khai báo!")
        
        if self.__id_registry[id_name] is not None and index is None:
            index = self.__id_registry[id_name]
        return self.__build_dict(id_name, index)


    # --- Sugar Methods cho Dash Callbacks ---
    def match(self, id_name: str) -> Dict[str, Any]: 
        """
        Trả về ID dùng cho Output/Input với cơ chế dash.MATCH.
        
        Args:
            id_name: Tên của id

        Raises:
            Exception: Nếu truyền id_name trống
            Exception: Nếu gọi một id_name chưa được khởi tạo trước đó
            Exception: Nếu gọi một id_name là ID tĩnh, khi này không sử dụng phương thức MATCH
        """
        if id_name is None:
            raise Exception("Không được để ID trống")

        if id_name not in self.__id_registry:
            raise Exception(f"ID {id_name} chưa được khởi tạo")
        
        if self.__id_registry[id_name] is None:
            raise Exception(f"ID {id_name} là ID tĩnh.")
        
        return self.__build_dict(id_name, MATCH)
        

    def all(self, id_name: str) -> Dict[str, Any]: 
        """
        Trả về ID dùng cho Output/Input với cơ chế dash.ALL.
        
        Args:
            id_name: Tên của id

        Returns:
            Dict[str, Any]: Dictionary ID với trường 'index' là hằng số ALL.

        Raises:
            Exception: Nếu id_name trống
            Exception: Nếu gọi một id_name chưa được khởi tạo trước đó
            Exception: Nếu gọi một id_name là ID tĩnh, khi này không sử dụng phương thức ALL
        """
        if id_name is None:
            raise Exception("Không được để ID trống")

        if id_name not in self.__id_registry:
            raise Exception(f"ID {id_name} chưa được khởi tạo")
        
        if self.__id_registry[id_name] is None:
            raise Exception(f"ID {id_name} là ID tĩnh.")
        
        return self.__build_dict(id_name, ALL)


    def allsmaller(self, id_name: str): 
        """
        Trả về ID dùng cho Output/Input với cơ chế dash.ALLSMALLER.
        
        Args:
            id_name: Tên của id

        Raises:
            Exception: Nếu id_name trống
            Exception: Nếu gọi một id_name chưa được khởi tạo trước đó
            Exception: Nếu gọi một id_name là ID tĩnh, khi này không sử dụng phương thức ALLSMALLER
        """
        if id_name is None:
            raise Exception("Không được để ID trống")

        if id_name not in self.__id_registry:
            raise Exception(f"ID {id_name} chưa được khởi tạo")
        
        if self.__id_registry[id_name] is None:
            raise Exception(f"ID {id_name} là ID tĩnh.")
        
        return self.__build_dict(id_name, ALLSMALLER)