# Build Pipeline

Pipeline xử lý và chuẩn hóa dữ liệu điểm thi Tốt nghiệp THPT, phục vụ cho Dashboard.

## Cấu trúc

```text
data/       # Dữ liệu đầu vào và các bảng mapping
output/     # Dữ liệu sau xử lý
logs/       # Log của pipeline
pipeline.py # Logic xử lý dữ liệu
run.py      # Entry point
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy

```bash
python run.py -y <năm>

# Hoặc
# python run.py --year <năm>
```

Dữ liệu sau khi xử lý được lưu trong `output/` dưới dạng Parquet.
