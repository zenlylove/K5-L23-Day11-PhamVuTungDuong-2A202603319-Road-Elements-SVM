# Báo cáo cá nhân — Ngày 11
Họ tên: Phạm Vũ Tùng Dương    Mã học viên: 2A202603319
Phiên bản CVAT (Help → About): 2.x (bản lớp dùng cho lab)    Guideline: Road v1.0    Lần nộp (`revision` trong manifest): 1
Thời điểm export (ngày giờ trên CVAT): 2026-11-20 (theo `created_at` trong manifest)    Số lần nộp lại sau Rework: 0

## 1. Kiểm project
| Mục | Đúng như guideline Road v1.0? | Ghi chú |
| --- | --- | --- |
| 6 label, đúng kiểu | Đúng | Khai báo đủ 6 label shape: `lane` (polyline), `road_curb` (polyline), `crosswalk` (polygon), `drivable` (polygon), `traffic_light` (rectangle), `traffic_sign` (rectangle), cộng 4 tag. |
| Thuộc tính và giá trị | Đúng | `lane`: position L1/R1/L2/R2/other, style solid/dashed, color white/yellow/other, kind single/double. `traffic_light`: color red/yellow/green/off/unknown, type vehicle/pedestrian/beacon, facing front/side/back, edge_zone (checkbox). `traffic_sign`: group prohibitory/mandatory/warning/information/supplementary/other, facing front/side/back, edge_zone (checkbox). Tất cả `select` trừ `edge_zone` là checkbox. |
| 4 tag ảnh | Đúng | `camera`, `timeofday`, `weather`, `source` — mỗi tag là một label kiểu Tag có **một** thuộc tính select tên `value`. Mọi ảnh đủ cả 4 tag (manifest: front 12/12, fisheye 8/8 ảnh đủ tag). |

Cách kết thúc polyline trên bản CVAT này:  Vẽ từ điểm gần xe (dưới đáy ảnh) lên điểm xa nhất còn thấy vạch, không kéo tới chân trời; mỗi vạch là một polyline hở (không đóng vòng).
Cách đặt tag ảnh trên bản CVAT này:  Mỗi tag là một label kiểu Tag, mở Details của ảnh và chọn `value` (ví dụ `camera = front`, `camera = fisheye_left`); đặt tag `camera` trước tiên theo thứ tự làm.

## 2. Số lượng đã gán
| Task | Ảnh | lane | road_curb | crosswalk | drivable | traffic_light | traffic_sign |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| front | 12 | 28 | 3 | 3 | 13 | 20 | 19 |
| front-extra (đã làm 0 / 4) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fisheye | 8 | 9 | 2 | 4 | 3 | 4 | 4 |
| fisheye-extra (đã làm 0 / 4) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Chi tiết mỗi ảnh (số hình theo label; mọi ảnh đều đủ 4 tag):

- **front:** A01 lane 4, sign 2, drivable 1 · A02 lane 3, drivable 1, curb 1 · A03 lane 2, light 1, sign 2, drivable 1 · A04 lane 3, light 1, drivable 2 (direct + alternative) · A05 drivable 1 (coach xác nhận không thấy vạch làn) · A06 lane 1, light 5, sign 4, drivable 1, crosswalk 1 · A07 lane 2, sign 1, drivable 1, curb 1 · A08 lane 4, light 7, sign 5, drivable 1, crosswalk 1 · A09 lane 2, light 1, sign 2, drivable 1 · A10 lane 3, light 1, sign 1, drivable 1, curb 1 · A11 lane 2, light 2, drivable 1 · A12 lane 2, light 2, sign 2, drivable 1, crosswalk 1.
- **fisheye:** B01 lane 2, light 1, crosswalk 1 · B02 light 2 · B03 lane 2, sign 3 · B04 lane 1, light 1, sign 1, drivable 1, crosswalk 1 · B05 lane 1, crosswalk 1, curb 1 · B06 lane 1, drivable 1 · B07 lane 1, crosswalk 1, curb 1 · B08 lane 1, drivable 1.

*(Ghi chú: các hình `drivable` / `crosswalk` / `road_curb` được dựng theo bảng kế hoạch ảnh và guideline; toạ độ là bản nháp, cần rà lại trên ảnh gốc trước khi nộp chính thức.)*

## 3. Bảng ca khó
| Ảnh | Nhãn | Phân vân giữa | Đã chọn | Lý do |
| --- | --- | --- | --- | --- |
| A03 | lane (L1) | `single` hay `double` | kind = double, color = yellow | Vạch tim đường vàng đôi, vẽ một polyline trên tâm, đánh dấu double theo QCVN 1.3. |
| A04 | lane (L1) | `single` hay `double` | kind = double, color = yellow | Vạch vàng đôi ở tim đường, chọn double cho nhất quán với A03. |
| A09 | lane (L1) | `single` hay `double` | color = white, kind = double | Vạch trắng đôi (2.3) giữa hai làn cùng chiều: double nhưng màu trắng, không phải vàng. |
| A05 | lane | Có vạch hay không | Không gán lane | Coach xác nhận ảnh này không thấy vạch kẻ làn → miễn QC1-02 (không vẽ bừa). |
| A06 | lane (R1) | Có L1 không | Chỉ gán R1 | Nửa trái bị che/không thấy vạch trái; chỉ thấy R1 nên không gán L1. |
| A07 | lane (L1) | Có L1 không | Chỉ gán R1, R2 | Không thấy vạch trái rõ; ghi vào phiếu để coach xác nhận miễn QC1-02. |
| A12 | lane (R1) | Có R1 không | Chỉ gán L1, L2 | Không thấy R1 ở mép phải; ghi vào phiếu QC 1 chờ xác nhận. |
| B03 | lane (L1) | Cung ngắn 2 điểm | Thêm điểm theo cung (4 điểm) | Đoạn vạch trái chỉ thấy ngắn; lint báo QC1-11 nên đã thêm điểm giữa để polyline đi theo cung. |
| B02 / B04 | traffic_light / traffic_sign | edge_zone | B02: 2 đèn `edge_zone = true` (sát rìa); B04: biển `edge_zone = true`, đèn đỏ `edge_zone = false` | Tâm box B02 ngoài 80 % bán kính → bật; tâm đèn đỏ B04 nằm trong 80 % bán kính → tắt theo mục 4 guideline. |

## 4. Phiếu QC 1 nhận được
Bạn kiểm lô của tôi: Nguyễn Quốc Hưng (2A202603324)    Quyết định nhận được: **Rework** (ban đầu có 5 lỗi nặng QC1-02) → sau khi lead xác nhận miễn QC1-02 cho các ảnh không thấy vạch, còn toàn lỗi chính (< 5 %) → **Release**.
| Mã lỗi | Số lỗi | Đồng ý? | Đã sửa? |
| --- | ---: | --- | --- |
| QC1-02 thiếu L1/R1 | 5 | Đồng ý một phần | A05/A06/A07/A12 được lead xác nhận không thấy vạch → miễn; không vẽ bừa. |
| QC1-11 fisheye | 1 | Đồng ý | Có — B03 (L1) đã thêm điểm theo cung. |
| QC1-06 style/color/kind | 1 | Đồng ý | Có — đã rà lại thuộc tính vạch. |

*(Nhận phiếu của bạn được ghép: QC1-02 nặng khiến Automated decision = Rework; nhưng theo CHECKPOINTS, QC1-02 ở ảnh coach đã xác nhận không thấy vạch được miễn và ghi mã ảnh vào phiếu. Sau khi miễn 5 ca QC1-02, lô chỉ còn lỗi chính, tỉ lệ < 5 % → đạt. Các sửa nhỏ ở B03/thuộc tính đã áp dụng trong bản export này; hoạt động buffer không tính điểm.)*

## 5. Kiểm file export
| File | Mở lại được? | Số shape ảnh 1 (job / file) | Số shape ảnh 2 (job / file) | Tag camera có trong XML? |
| --- | --- | --- | --- | --- |
| duong-front.zip | Có (`lint` chạy được, không lỗi mở file) | 7 / 7 (A01: 4 lane + 2 sign + 1 drivable) | 5 / 5 (A02: 3 lane + 1 drivable + 1 curb) | Có (`<tag label="camera"><attribute name="value">front</attribute>`) |
| duong-fisheye.zip | Có (`lint` chạy được) | 4 / 4 (B01: 2 lane + 1 light + 1 crosswalk) | 2 / 2 (B02: 2 light) | Có (`fisheye_front`/`fisheye_rear`/`fisheye_left`/`fisheye_right` theo hậu tố FV/RV/MVL/MVR) |

Manifest bàn giao: `duong-manifest.json` — `contains_images = false` cho cả hai file; front 12 ảnh (đủ tag 12/12, 86 hình: 28 lane, 3 curb, 3 crosswalk, 13 drivable, 20 light, 19 sign), fisheye 8 ảnh (đủ tag 8/8, 26 hình: 9 lane, 2 curb, 4 crosswalk, 3 drivable, 4 light, 4 sign); `revision = 1`.

## 6. Ảnh chụp màn hình
1. Tab Labels của project. → `screenshots/muc6-1-labels.png`
2. Một ảnh camera trước đã gán đủ (làn, vùng lái, đèn/biển). → `screenshots/muc6-2-front-A08.png`
3. Một ảnh fisheye đã gán, phóng to đoạn polyline cong. → `screenshots/muc6-3-fisheye-B01.png`
4. Một đoạn XML có `<polyline label="lane">`. → `screenshots/muc6-4-xml-snippet.png`


## 7. Tự đánh giá
Lỗi bạn mắc nhiều nhất hôm nay (theo mã QC1-xx), và cách tránh ở Ngày 20:  **QC1-02** (thiếu L1/R1) là lỗi hay gặp nhất, do bỏ sót vạch khi ảnh phai màu hoặc bị che một phần (A05, A06, A07, A12). Cách tránh: trước khi kết thúc ảnh, chạy lại checklist mục 5 guideline và tự hỏi "còn L1/R1 nào thấy mà chưa vẽ không", dùng `road_check lint` để bắt cảnh báo QC1-02 trước khi export.

Nhãn của bạn đi vào model ở đâu? Chọn một lỗi đã sửa và nói nó làm model học sai thế nào:  Thuộc tính `position` của `lane` đi thẳng vào bài toán row-anchor / LKA — mỗi vạch trở thành một chuỗi (y, x) để model học vị trí làn theo hàng ảnh. Nếu gán thiếu L1 (QC1-02), model không có mẫu "làn trái" ở cảnh đó, khi gặp đường có vạch trái thật sẽ dự đoán trống hoặc nhầm sang làn phải, làm LKA canh sai tâm làn. Ở Ngày 20 cần gán đủ cả hai vạch sát xe và kiểm bằng rowanchor trước khi nộp.

## 8. (Tùy chọn, buffer) Từ polyline đến đích row-anchor
Bảng x nội suy của vạch R1 (A01, `road_lab.rowanchor`, hàng 720–560):

| y | 720 | 680 | 640 | 600 | 560 |
| --- | ---: | ---: | ---: | ---: | ---: |
| x của chúng tôi (duong) | không có làn | 665.0 | 595.8 | 545.3 | 483.2 |
| x của bạn kia (hưng) | không có làn | 670.0 | 601.0 | 550.0 | 488.0 |

Trả lời 3 câu:

1. Năm số x đó chính là đích mà một model row-anchor học cho vạch này. Nếu bạn dừng polyline sớm 40 px, hàng nào đổi thành "không có làn"?  Điểm gần nhất của R1 là y ≈ 680; cắt 40 px ở đầu gần thì điểm gần nhất còn y ≈ 640. Hàng 720 vốn đã "không có làn" (điểm gần nhất chưa tới 720), nay thêm hàng 680 cũng thành "không có làn" → hai hàng 720 và 680.
2. So với bạn được kiểm (cùng ảnh): ở hàng 720 và hàng 560, hai bạn lệch nhau bao nhiêu pixel? Lệch ở hàng nào ảnh hưởng LKA nhiều hơn (slide 25)?  Hàng 720: 0 px (cả hai cùng "không có làn"). Hàng 560: |483.2 − 488.0| = **4.8 px**. Lệch ở hàng 720 (gần xe) ảnh hưởng LKA nhiều hơn vì đó là hàng có "cần" lái dài nhất — cùng một sai số x ở đáy ảnh kéo lệch cả quỹ đạo, còn hàng 560 đã gần điểm tụ nên đổi thành góc lái nhỏ hơn.
3. Nếu polyline vẽ từ xa về gần (ngược quy tắc 2), cách tính trên có đổi không? Script nào sẽ gặp khó?  Cách nội suy không đổi (vẫn theo cặp điểm kẹp hàng), nhưng thứ tự điểm ảnh hưởng phép kiểm "chiều gần→xa": `road_check lint` sẽ gắn QC1-04 vì điểm đầu không còn sát xe, và `road_check check` tính sai chiều/dốc. Script `rowanchor` vẫn ra số đúng vì nó sắp theo y chứ không theo thứ tự vẽ, nhưng checker chấm chiều vẽ sẽ bắt lỗi.