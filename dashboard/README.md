# Kỳ thi Tốt nghiệp THPT — Data Analytics & Decision Support Dashboard

Dashboard hỗ trợ phân tích dữ liệu điểm thi Tốt nghiệp THPT và xây dựng các kịch bản xét tuyển.

## Chức năng chính

* Nhập điểm dự kiến và tính các tổ hợp khả dĩ.
* Tra cứu kết quả theo SBD.
* Phân tích và so sánh điểm giữa các tổ hợp.
* Thiết lập điểm sàn và xây dựng kịch bản.
* Trực quan hóa dữ liệu bằng biểu đồ và bảng.

## Cấu trúc

```text
.
├── api/                    # API
├── assets/                 # CSS, JS, hình ảnh
├── data/                   # Dữ liệu và bảng tra cứu
│   ├── combs_scores/
│   ├── lookup_tables/
│   └── raw_scores/
├── pages/                  # Dash pages
├── page_modules/           # Layout và callbacks của từng page
│   ├── dss_without_sbd/
│   ├── dss_with_sbd/
│   └── main_page/
├── tests/                  # Kiểm thử
├── utils/                  # Các tiện ích dùng chung
│   └── direction/          # PageDirection
└── ...
```

## Công nghệ

* **Python**
* **Polars** — preprocessing dữ liệu điểm thi
* **Pandas** — xử lý dữ liệu khảo sát
* **Dash & Plotly** — dashboard và trực quan hóa
* **Dash Bootstrap Components** — giao diện
* **Scikit-learn** — hỗ trợ phân tích dữ liệu

## PageDirection

`utils/direction` là thư viện quản lý ID cho Dash, được phát triển riêng và tích hợp vào project.

Source: [musgramming/dash-id-problem](https://github.com/musgramming/dash-id-problem?utm_source=chatgpt.com)

