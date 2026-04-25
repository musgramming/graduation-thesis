# Phân Tích Dữ Liệu và Xây Dựng Dashboard Điểm Thi THPT Quốc Gia 2025

Dự án này là đề tài tiểu luận tốt nghiệp, tập trung vào việc khai thác dữ liệu điểm thi THPTQG 2025 để đưa ra các phân tích thống kê và công cụ trực quan hóa hỗ trợ thí sinh/phụ huynh trong việc định hướng tuyển đại học.

---

## 📁 Cấu Trúc Tổng Thể

```bash
thptqg2025-tltn/
├── dashboard/              # Ứng dụng Dashboard (Dash/Flask)
│   ├── assets/             # CSS, hình ảnh tùy chỉnh
│   ├── data/               # Dữ liệu sạch dùng cho dashboard
│   ├── pages/              # Các trang nội dung của dashboard (Multi-page app)
│   ├── utils/ & tools/     # Các hàm hỗ trợ xử lý logic
│   ├── main_layout.py      # Giao diện chính của ứng dụng
│   ├── server.py           # File khởi chạy server Flask/Dash
│   └── requirements.txt    # Thư viện cho môi trường dashboard
└── notebook/               # Môi trường nghiên cứu dữ liệu
    ├── input/              # Dữ liệu thô ban đầu
    ├── output/             # Kết quả sau khi xử lý (CSV/Parquet...)
    ├── preprocessing.ipynb # Notebook làm sạch và tiền xử lý dữ liệu
    ├── analysis-diem-to-hop.ipynb # Phân tích phổ điểm theo các tổ hợp môn
    └── requirements.txt    # Thư viện cho môi trường Notebook
```

Hệ thống được chia làm hai phân vùng làm việc biệt lập nhưng bổ trợ cho nhau:

1. Phân vùng Nghiên cứu & Tiền xử lý (/notebook)

- `preprocessing.ipynb`: Làm sạch dữ liệu thô, xử lý các giá trị thiếu (null) và định dạng lại kiểu dữ liệu của các môn thi.

- `analysis-diem-to-hop.ipynb`: Tập trung tính toán điểm theo các tổ hợp xét tuyển phổ biến (A00, A01, B00, C00, D01).

- `input/` & `output/`: Quản lý dòng chảy dữ liệu từ khi nhập liệu đến khi trích xuất tệp sạch để nạp vào hệ thống dashboard.

2. Phân vùng Ứng dụng Dashboard (/dashboard)

- `server.py` & `main_layout.py`: Trái tim của ứng dụng, khởi tạo server và định nghĩa cấu trúc giao diện đa trang (Multi-page App).

- `pages/`: Chứa các module giao diện riêng biệt, gồm các thành phần:
    - `dss-with-sbd`: Cho phép thí sinh dự thi có thể tra cứu 
    - `dss-without-sbd`: Cho phép người dùng có thể xây dựng kịch bản từ điểm số mong muốn

- `utils/` & `tools/`: Chứa các "backend logic" xử lý truy vấn dữ liệu nhanh và các hàm bổ trợ.

---

## 🛠 Công Nghệ & Kỹ Thuật Sử Dụng

|Thành phần|Công nghệ|
|----------|----------|
|Ngôn ngữ| Python (Có kèm js)
|Tiền xử lý dữ liệu| Polars, Pyarrow (để lưu trữ)
|Phân tích dữ liệu| Polars, Matplotlib, Seaborn, Plotly|
|Web Framework| Dash, Plotly, Polars, Bootstrap|

---

## Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống

- Python: Phiên bản 3.12 trở lên.

- Hardware: Khuyến cáo RAM tối thiểu 8GB (do xử lý dữ liệu lớn với Polars trong Notebook).

### 2. Cài đặt chi tiết

#### 2.1. Phân đoạn Notebook (Xử lý dữ liệu)

⚠️ Lưu ý: Phần này tiêu tốn tài nguyên phần cứng đáng kể. Nếu máy yếu, bạn có thể bỏ qua và sử dụng trực tiếp dữ liệu đã làm sạch trong thư mục dashboard/data.


- Bước 1: Di chuyển vào thư mục notebook:

```bash
cd notebook
```

- Bước 2: Khởi tạo môi trường tự động: Chạy file setup.bat (File này sẽ tự động tạo venv và cài đặt thư viện).

- Bước 3: Truy cập giao diện làm việc: Mở trình duyệt và truy cập: `http://localhost:8888`


#### 2.2. Phân đoạn Dashboard (Giao diện)

- Bước 1: Di chuyển vào thư mục dashboard:

```bash
cd dashboard
```

- Bước 2: Tạo môi trường ảo:

```bash
python -m venv .venv_dashboard

.venv_dashboard/Scripts/activate
```

- Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

- Bước 4: Chạy file:

```bash
python server.py
```

---

## Các Tính Năng Nổi Bật

1. Phân tích phổ điểm: Trực quan hóa hình dáng phổ điểm theo từng môn và theo tổ hợp 3 môn.

2. Thống kê theo vùng miền: So sánh kết quả thi giữa các tỉnh thành trên cả nước.

3. Phân tích chuyên sâu: Dự báo mức độ cạnh tranh dựa trên số lượng thí sinh đạt điểm cao ở từng tổ hợp.

---

## By Mus
