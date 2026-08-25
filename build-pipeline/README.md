# THPTQG Data Pipeline (2025+)

Hệ thống pipeline tự động hóa quy trình xử lý dữ liệu điểm thi và điểm tổ hợp xét tuyển trong kỳ thi tốt nghiệp THPT (áp dụng từ năm 2025).

---

## 📂 Cấu trúc thư mục dự án

```text
build-pipeline/
│
├── data/                  # Thư mục chứa dữ liệu thô (raw data) đầu vào
├── logs/                  # Thư mục lưu trữ log vận hành của pipeline
├── output/                # Thư mục lưu trữ kết quả xử lý
│   ├── bang-diem/         # Dữ liệu bảng điểm thi chi tiết theo năm
│   └── bang-diem-to-hop/  # Dữ liệu bảng điểm tổ hợp xét tuyển
│
├── .gitignore             # Các tệp và thư mục bị bỏ qua bởi Git
├── logging_utils.py       # Các tiện ích và cấu hình ghi log hệ thống
├── pipeline.py            # Logic xử lý dữ liệu chính (thực thi theo từng năm)
├── README.md              # Tài liệu hướng dẫn sử dụng dự án
├── requirements.txt       # Danh sách các thư viện Python phụ thuộc
└── run.py                 # Script điều phối chính (hỗ trợ chạy đa luồng/nhiều năm, quản lý venv)
```

---

## ⚙️ Yêu cầu hệ thống

- Python: Phiên bản 3.10 trở lên.
- Hệ điều hành: Windows / Linux / macOS.

## 🚀 Hướng dẫn sử dụng

### 1. Chuẩn bị dữ liệu

Đặt các tệp dữ liệu thô vào thư mục data/ đúng cấu trúc:

- data/bang_diem/: Chứa dữ liệu điểm thi gốc theo các năm (từ 2025 trở đi).

- data/mapping/: Chứa các tệp ánh xạ cần thiết cho quá trình chuẩn hóa.

### 2. Cài đặt các thư viện phụ thuộc (nếu cần chạy thủ công)

Hệ thống sử dụng tệp requirements.txt. Tuy nhiên, script điều phối run.py sẽ tự động tạo môi trường ảo (.venv_pipeline) và cài đặt các thư viện này một cách hoàn toàn tự động.

### 3. Chạy Pipeline

Bạn có thể chạy pipeline cho một năm hoặc nhiều năm cùng lúc thông qua script điều phối run.py.

Chạy cho một năm duy nhất (từ 2025 trở đi):

```bash
python run.py -y 2025
```

Chạy cho nhiều năm cùng lúc:

```bash
python run.py -y 2025 2026
```

## 🛠️ Cơ chế hoạt động của run.py

Kiểm tra tham số & Validation: Đảm bảo các năm được yêu cầu xử lý từ năm 2025 trở đi.

Chuẩn bị môi trường: Tự động tạo thư mục output/ (bang-diem, bang-diem-to-hop) và thiết lập môi trường ảo Python biệt lập (.venv_pipeline).

Cài đặt thư viện: Tự động nâng cấp pip và cài đặt các gói từ requirements.txt vào môi trường ảo.

Thực thi pipeline: Lần lượt kích hoạt pipeline.py cho từng năm được chỉ định. Nếu có bất kỳ năm nào xảy ra lỗi, pipeline sẽ dừng lại và báo cáo mã lỗi chi tiết.

Dọn dẹp (Cleanup): Tự động xóa môi trường ảo sau khi hoàn tất phiên làm việc để giải phóng dung lượng.