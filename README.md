# Drone Data Studio — Local-first Drone → PC Converter

Trang web tĩnh (HTML/CSS/JS thuần, không dependency), chạy trên GitHub Pages hoặc local Node.js static server. **Không có API upload, tracking, tài khoản hoặc lưu log ở server.** Tệp nhập được đọc bằng File API trong RAM của tab; dữ liệu xuất được tạo bằng Blob rồi tải trực tiếp về PC. Chế độ này ưu tiên dữ liệu cục bộ, không hứa sẽ giữ tệp qua lần làm mới trang. Trang không tải tài nguyên ngoài/third-party. `server.cjs` chỉ cung cấp tài nguyên tĩnh tại `127.0.0.1:8080` và không có endpoint nhận tệp.

## Mở trên Windows

- Giải nén ZIP.
- Cài Node.js LTS (bản 18+).
- Nhấp đúp `start-windows.bat`, mở http://127.0.0.1:8080.
- Hoặc từ Terminal: `node server.cjs`.
- Triển khai GitHub Pages: chép toàn bộ thư mục nguồn (không cần server.cjs) vào nhánh GitHub Pages. Dùng HTTPS.

**Không mở index.html trực tiếp qua `file://`** vì trình duyệt chặn JavaScript ES modules theo origin/CORS. Không cần Internet khi truy cập từ localhost.

## Định dạng thực hiện trong bản 0.1.0

| Nguồn | Bộ xử lý | Hạn chế |
|---|---|---|
| DJI SRT | Chọn các cue có GPS Lat/Lon; parse altitude/time tương đối | Subtitle theo phiên bản khác nhau; không hỗ trợ mọi mẫu DJI; ngày giờ không gắn timezone cần kiểm tra |
| CSV / TSV | Khớp tên trường telemetry phổ biến | CSV phân tách theo dấu phẩy/tab; không đọc mọi dialect |
| JSON / GeoJSON | Mảng telemetry, FeatureCollection Point/LineString | GeoJSON tọa độ WGS84 |
| GPX / KML | Trackpoints / Coordinates | Đầu vào XML phổ biến, chưa có XML parser tổng quát |
| PX4 ULog `.ulg` | Duyệt message ULog, đọc GPS topics cơ bản | Chỉ GPS, không đủ mọi topic/fmt; cần flight-review-rs để xuất Parquet đa topic |
| ArduPilot DataFlash `.bin` | Đọc FMT + GPS/POS | Chỉ GPS/POS và kiểu trường thông dụng, không đầy đủ mọi DataFlash |
| LAS không nén | Đọc header + XYZ/intensity, lấy mẫu tới ~250k điểm | Không hỗ trợ LAZ, CRS chưa được kiểm tra, giữ nguyên tọa độ gốc |

| Đầu ra | Tình trạng |
|---|---|
| CSV, JSON, NDJSON | Có, tải xuống |
| GeoJSON, KML, GPX | Có nếu dữ liệu có GPS WGS84 |
| CoT XML | Có nếu có GPS và UTC; xuất **một sự kiện CoT ở vị trí cuối cùng**, không truyền TAK live |
| XML canonical | Có, **schema riêng NDIEM-inspired**, không tuyên bố tuân thủ XSD NDIEM chính thức |
| MQTT JSONL envelope | Có, mỗi dòng là `{topic,qos,retain,payload}`; **không publish đến broker** |
| Parquet | Chưa có writer browser; giao diện nêu rõ chưa hỗ trợ |
| LAZ, ROS bag, MCAP, TLOG, KMZ, MP4 metadata | Chưa có giải mã; hiển thị lý do thay vì tạo đầu ra giả |

## Mô hình chuẩn hóa

```json
{
  "timestamp": "2026-11-03T02:00:00.000Z",
  "elapsed_ms": 0,
  "latitude": 10.776891,
  "longitude": 106.700806,
  "altitude_m": 31.5,
  "speed_mps": 3.2,
  "heading_deg": null,
  "satellites": 17,
  "battery_pct": 95,
  "source": "DJI SRT"
}
```

Nếu `timestamp` rỗng nhưng có `elapsed_ms`, nhập **UTC khởi đầu** để căn chỉnh. CoT không cho xuất khi thiếu UTC; để xem toàn bộ hành trình hãy dùng KML/GPX/GeoJSON. Với LAS, không biến hệ tọa độ trắc địa/projection thành WGS84 một cách võ đoán. Không dùng đường bay CoT xuất offline như xác nhận phát hiện UAV sống.

## Kiểm thử

`npm test` (chỉ dùng Node test runner, không tải package); dùng `samples/dji-demo.srt`, `samples/flight-telemetry.csv`. Kiểm tra log thực tế trước khi dùng trong đo đạc hoặc vận hành chuyên nghiệp. Trang này không phải công cụ an toàn bay / điều khiển drone.

## Hướng nâng cấp

- Thêm `parquet-wasm` được đóng gói tại `/vendor` và chạy trong Worker để xuất Arrow/Parquet cục bộ, không CDN.
- Adapter ULog/DataFlash chính thức qua Rust → WASM để xử lý mọi topic.
- PDAL/PROJ WASM hoặc desktop sidecar cho LAZ, CRS, DTM/DSM và kiểm định trắc địa.
- Đồng bộ NTP/PPS/PTP, ROS bag, tương quan tín hiệu IMU và GIS theo thời gian.
- MQTT/WebSocket trực tiếp chỉ nên bật khi người dùng cấu hình rõ endpoint (vì khi đó telemetry sẽ truyền đến bên thứ ba, không còn chỉ nằm trong trình duyệt).

## Dự án được tham khảo

- [iannil/open-uav-telemetry-bridge](https://github.com/iannil/open-uav-telemetry-bridge)
- [B-ushra/NDIEM](https://github.com/B-ushra/NDIEM-A-Networked-Drone-Information-Exchange-Model-for-Heterogenous-Drones)
- [alphafox02/DragonSync](https://github.com/alphafox02/DragonSync)
- [dji-drone-metadata-embedder](https://pypi.org/project/dji-drone-metadata-embedder/2.16.0/)
- [PX4/flight-review-rs](https://github.com/PX4/flight-review-rs)
- [OpenDroneMap/ODM](https://github.com/OpenDroneMap/ODM)

Các dự án được trích dẫn để ghi nhận ý tưởng và khuyến nghị tích hợp; **không sao chép code nguồn** của chúng vào sản phẩm này. Giấy phép của mỗi dự án gốc vẫn giữ nguyên.

## Giấy phép

Mã nguồn tự viết ở đây phân phối theo MIT; xem LICENSE.

## Tạo Parquet thật trên PC (tùy chọn)

Website offline không có bộ ghi Parquet/WASM, nhưng gói có công cụ cục bộ để tạo **Parquet thật** từ CSV đã xuất:

```powershell
python -m pip install pyarrow
python tools/csv_to_parquet.py flight-telemetry.csv --out flight-telemetry.parquet
```

Python và `pyarrow` chạy **trên máy cá nhân**; `pip install` chỉ tải gói thư viện, không tải dữ liệu bay của bạn. Với PX4 và yêu cầu giữ nguyên mọi topic hãy dùng `flight-review-rs` chính thức; CSV chuẩn hóa trong dashboard chỉ là bảng telemetry GPS.
