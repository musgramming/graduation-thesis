# Xây dựng Dashboard hỗ trợ ra quyết định chọn nguyện vọng trong kỳ thi Tốt nghiệp THPT dựa trên phân tích dữ liệu lớn

## Giới thiệu

Dự án xây dựng Dashboard hỗ trợ thí sinh phân tích kết quả thi Tốt nghiệp THPT và đưa ra quyết định lựa chọn nguyện vọng dựa trên dữ liệu.

> **[🚀 Live Demo](https://graduation-thesis-cxlt.onrender.com/)**

## Cấu trúc

Hệ thống gồm 3 thành phần chính:

* **`build-pipeline/`**: Xử lý, chuẩn hóa và chuyển đổi dữ liệu điểm thi sang Parquet.
* **`dashboard/`**: Dashboard trực quan hóa dữ liệu và hỗ trợ ra quyết định.
* **`survey/`**: Tiền xử lý và phân tích dữ liệu khảo sát thí sinh.

## Cài đặt

Mỗi thành phần có file `requirements.txt` riêng:

```bash
pip install -r build-pipeline/requirements.txt
pip install -r dashboard/requirements.txt
pip install -r survey/requirements.txt
```

## Chạy

### Build dữ liệu

```bash
cd build-pipeline
python run.py
```

Dữ liệu sau khi xử lý được lưu tại `build-pipeline/output/`.

### Chạy Dashboard

```bash
cd dashboard
python server.py
```

## Công nghệ

* Python
* Pandas
* Parquet / PyArrow
* Dash
* Plotly
* Bootstrap
* Jupyter Notebook (Chỉ `/survey`)
* Apriori (Chỉ `/survey`)
