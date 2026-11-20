# Phiếu QC 1 — Road v1.0

> **Phiếu QC 1 (duong kiểm lô của Hưng).** Dựng theo đúng mẫu và phương pháp của `templates/qc1_form.md` (kiểm theo mẫu 6 ảnh front, mẫu số = số nhãn đã kiểm, không chia cho số ảnh). Số liệu dưới đây là kết quả rà lô của Hưng; nếu phát sinh thêm lỗi khi đối chiếu chéo thì ghi bổ sung vào danh sách lỗi.

Lô được kiểm (học viên): Nguyễn Quốc Hưng (2A202603324)        Người kiểm (học viên): Phạm Vũ Tùng Dương (2A202603319)
Ngày: 2026-11-20                          Phiên bản guideline: Road v1.0
File được kiểm (tên + `revision` trong manifest): hung-front.zip · `revision = 1`
Số ảnh kiểm: 6 (A01, A02, A03, A04, A06, A08) (+ 0 ảnh thêm, ghi riêng)   Số nhãn đã kiểm (shape + tag): 68

## Tổng hợp theo mã
| Mã | Loại lỗi | Số mục kiểm | Số lỗi | Mức |
| --- | --- | ---: | ---: | --- |
| QC1-01 tag camera | sai thuộc tính / bỏ sót | 6 | 0 | nặng |
| QC1-02 đủ L1, R1 | bỏ sót | 12 | 2 | nặng |
| QC1-03 position | sai thuộc tính / thừa | 12 | 1 | nặng |
| QC1-04 tâm vạch, chiều, điểm dừng | sai phạm vi / bỏ sót | 12 | 1 | chính |
| QC1-05 vạch đứt, che | sai phạm vi / sai thuộc tính | 6 | 0 | chính |
| QC1-06 style, color, kind | sai thuộc tính | 12 | 2 | chính |
| QC1-07 vùng lái | sai phạm vi / bỏ sót / thừa | 4 | 0 | chính |
| QC1-08 đèn, màu | bỏ sót / sai phạm vi / sai thuộc tính | 8 | 0 | nặng / chính |
| QC1-09 facing, type, group, biển phụ | sai thuộc tính | 10 | 0 | chính |
| QC1-10 hình in, đủ biển | bỏ sót / sai phạm vi | 9 | 0 | chính |
| QC1-11 fisheye | sai phạm vi / sai thuộc tính | 0 | 0 | chính |
| QC1-12 file | lỗi file | 2 | 1 | nhẹ / nặng |

## Danh sách lỗi (mỗi lỗi một dòng)
| # | Mã | Ảnh | Nhãn (label, id) | Mức | Mô tả ngắn |
| --- | --- | --- | --- | --- | --- |
| 1 | QC1-02 | A03 | lane (thiếu L1) | nặng | Thấy vạch trái nhưng không gán L1. |
| 2 | QC1-02 | A06 | lane (thiếu R1) | nặng | Thấy vạch phải nhưng chỉ gán L1. |
| 3 | QC1-03 | A02 | lane#2 (đang là L2) | nặng | Vạch sát xe bị gán L2 — nhầm làn của mình với làn bên cạnh. |
| 4 | QC1-04 | A08 | lane (R1) | chính | Polyline dừng sớm ~15 px trước điểm xa nhất còn thấy vạch. |
| 5 | QC1-06 | A01 | lane#3 (solid) | chính | Vạch đứt bị gán style = solid. |
| 6 | QC1-06 | A04 | lane#1 (single) | chính | Vạch vàng đôi bị gán kind = single. |
| 7 | QC1-12 | A08 | tag timeofday | nhẹ | Thiếu tag timeofday (ảnh còn 3 tag). |

## Ca mơ hồ
| Ảnh | Câu hỏi cho lead | Lời đáp (nếu có) |
| --- | --- | --- |
| A06 | Vạch trái bị che một phần: nối qua chỗ che hay dừng? | (chờ lead) |
| A04 | Vạch vàng đôi: vẽ một polyline trên tâm hay hai polyline? | (chờ lead) |

## Quyết định
Lỗi nặng: 3   Lỗi chính: 3 / 68 nhãn = 4.4 %   Lỗi nhẹ: 1   Ca chờ lead: 2
Quyết định (Release / Hold / Rework): **Rework**
Lý do (theo luật của phiếu): Còn 3 lỗi nặng (QC1-02 ×2, QC1-03 ×1) → theo luật "có ít nhất một lỗi nặng → Rework". Tỉ lệ lỗi chính 4,4 % ≤ 5 % nhưng không cần xét vì đã có lỗi nặng. Hai ca mơ hồ (A06, A04) không đổi kết luận vì Rework đã được quyết bởi lỗi nặng; nếu sau khi sửa hết lỗi nặng mà hai ca này vẫn treo thì chuyển Hold chờ lead.

Loại lỗi: bỏ sót = thiếu nhãn phải có; thừa = gán cái không phải đối tượng; sai phạm vi = hình lệch, sai chiều, dừng sai chỗ, tràn vùng. Ba loại này theo cách chia lỗi gán nhãn của ISO/IEC 5259-4 (mục 8.4.2); "sai thuộc tính" và "lỗi file" là khóa học thêm. Cách xếp mức: [thang mức lỗi](../docs/qc_severity_road_v1.0.md).

---
*Cách tính mẫu số: 68 = tổng số nhãn đã kiểm trên 6 ảnh (shape + tag), không chia cho số ảnh. Với mỗi lỗi chính (mã QC1-04, -06) lấy số lỗi chính / 68. Quyết định theo thứ tự: lỗi nặng → Rework; hết nặng thì xét tỉ lệ chính > 5 % → Rework; còn ca mơ hồ chưa có lời đáp → Hold; còn lại → Release.*