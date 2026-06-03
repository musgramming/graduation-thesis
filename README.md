# Phân Tích Dữ Liệu và Xây Dựng Dashboard Điểm Thi THPT Quốc Gia 2025

Dự án này là đề tài nghiên cứu tập trung vào việc khai thác dữ liệu điểm thi THPTQG 2025. Điểm khác biệt cốt lõi là hệ thống được xây dựng dựa trên kết quả khai phá hành vi thực tế của thí sinh thông qua khảo sát định tính và định lượng.

---

## 📁 Cấu Trúc Tổng Thể

```bash
thptqg2025-tltn/
├── survey/                   # Phân vùng Khai phá dữ liệu khảo sát
│   ├── input/                # Dữ liệu khảo sát thô (xlsx/csv)
│   ├── output/               # Kết quả sau khai phá & wordcloud
│   ├── preprocessing.ipynb   # Tiền xử lý văn bản & NLP
│   ├── analysis.ipynb        # Khai phá luật kết hợp (Apriori)
│   ├── requirements.txt      # Thư viện: underthesea, mlxtend...
│   └── setup.bat             # Khởi tạo môi trường tự động
├── notebook/                 # Phân vùng Nghiên cứu phổ điểm (Big Data)
│   ├── input/                # Dữ liệu điểm thi thô toàn quốc
│   ├── output/               # Dữ liệu đã làm sạch & tính tổ hợp
│   ├── preprocessing.ipynb   # Xử lý hiệu năng cao với Polars
│   ├── analysis-diem-to-hop.ipynb # Phân tích phổ điểm chuyên sâu
│   ├── requirements.txt      # Thư viện: polars, pyarrow, seaborn...
│   └── setup.bat             # Khởi tạo môi trường cho notebook
└── dashboard/                # Phân vùng Ứng dụng & Triển khai (DSS)
    ├── assets/               # Tài nguyên giao diện (CSS/Images)
    ├── data/                 # Dữ liệu tinh gọn phục vụ Dashboard
    ├── pages/                # Các trang chức năng (Multi-page App)
    │   ├── dss-with-sbd.py   # Tra cứu theo số báo danh
    │   └── dss-without-sbd.py# Giả lập kịch bản điểm số
    ├── utils/ & tools/       # Thư viện hàm xử lý nội bộ
    ├── server.py             # Khởi chạy Flask/Dash Server
    ├── main_layout.py        # Định nghĩa cấu trúc UI tổng thể
    └── requirements.txt      # Thư viện: dash, plotly, bootstrap...
```

Hệ thống được chia làm 3 phân vùng làm việc biệt lập nhưng bổ trợ cho nhau:

**1. Phân vùng Nghiên cứu & Tiền xử lý (/notebook)**

- `preprocessing.ipynb`: Làm sạch dữ liệu thô, xử lý các giá trị thiếu (null) và định dạng lại kiểu dữ liệu của các môn thi.

- `analysis-diem-to-hop.ipynb`: Tập trung tính toán điểm theo các tổ hợp xét tuyển phổ biến (A00, A01, B00, C00, D01).

- `input/` & `output/`: Quản lý dòng chảy dữ liệu từ khi nhập liệu đến khi trích xuất tệp sạch để nạp vào hệ thống dashboard.

**2. Phân vùng Ứng dụng Dashboard (/dashboard)**

- `server.py` & `main_layout.py`: Trái tim của ứng dụng, khởi tạo server và định nghĩa cấu trúc giao diện đa trang (Multi-page App).

- `pages/`: Chứa các module giao diện riêng biệt, gồm các thành phần:
    - `dss-with-sbd`: Cho phép thí sinh dự thi có thể tra cứu 
    - `dss-without-sbd`: Cho phép người dùng có thể xây dựng kịch bản từ điểm số mong muốn

- `utils/` & `tools/`: Chứa các "backend logic" xử lý truy vấn dữ liệu nhanh và các hàm bổ trợ.

**3. Phân vùng Khảo sát & Khai phá (./survey)**

Nơi thực hiện các nghiên cứu định tính và định lượng để hiểu nhu cầu thí sinh.

- preprocessing.ipynb: Tiền xử lý dữ liệu văn bản bằng NLP (Underthesea).

- analysis.ipynb: Khai phá luật kết hợp (Apriori) để tìm ra mối liên hệ giữa các nhu cầu của thí sinh.

- input/ & output/: Quản lý dữ liệu khảo sát thô và kết quả khai phá.

---

## 🛠 Công Nghệ & Kỹ Thuật Sử Dụng

|Thành phần | Công nghệ / Thuật toán
|-----------|-----------------------
|Khai phá dữ liệu|Apriori (Association Rules Mining), NLP (Underthesea)
|Xử lý dữ liệu lớn|"Pandas, Polars, Pyarrow"
|Trực quan hóa|"Plotly, WordCloud, Matplotlib, Seaborn"
|Web Framework|"Dash (Plotly), Bootstrap, Flask"

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

#### 2.3. Phân đoạn Survey (Khai phá dữ liệu khảo sát)

```cd 
cd survey
setup.bat
```

---

## Các Tính Năng Nổi Bật

1. Phân tích phổ điểm: Trực quan hóa hình dáng phổ điểm theo từng môn và theo tổ hợp 3 môn.

2. Thống kê theo vùng miền: So sánh kết quả thi giữa các tỉnh thành trên cả nước.

3. Phân tích chuyên sâu: Dự báo mức độ cạnh tranh dựa trên số lượng thí sinh đạt điểm cao ở từng tổ hợp.

---

## By Mus
