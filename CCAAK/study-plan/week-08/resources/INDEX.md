# 📂 Tài nguyên Tuần 8 — Tuần chốt: mock dồn, capstone vận hành, cram, thi

> Hai file crawl từ nguồn chính thức (trang certification của Confluent và trang upgrade của Apache Kafka), cộng ba file tổng hợp phục vụ riêng tuần chốt.
> Về [file học Tuần 8](../README.md) · [Kế hoạch tổng](../../../CCAAK-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn |
| - | --- | --- | --- |
| 1 | [ccaak-official-exam-page.md](ccaak-official-exam-page.md) | Phần **CCAAK** trên trang certification: đối tượng *"professionals who manage and maintain Kafka cluster environments"*, 4 năng lực *configure / deploy / monitor / support*; **90 phút**; 3 dạng câu **multiple-choice · matching · list order**; kết quả hiện ngay; **hiệu lực 2 năm**; **retake chờ 7 ngày**; proctor **Honorlock**; đổi lịch miễn phí trước 5 ngày | https://www.confluent.io/certification/ |
| 2 | [confluent-certification-policies.md](confluent-certification-policies.md) | Chính sách hiệu lực / retake / đổi lịch / proctoring (**crawl**) + **checklist phòng thi theo mốc 1 tuần → 1 ngày → ngày thi** và bảng sự cố hay gặp (**tổng hợp, ghi rõ trong file**); nêu 3 con số **chưa xác nhận được** từ nguồn chính thức (60 câu, 150 USD, ngưỡng đậu) | https://www.confluent.io/certification/ + tổng hợp |
| 3 | [kafka-4x-operational-changes.md](kafka-4x-operational-changes.md) | Thay đổi 4.0 → 4.3 **lọc theo góc admin**: KRaft-only, Java 17 cho broker, **3 bước rolling upgrade + `kafka-features.sh upgrade`**, bảng downgrade theo release, mặc định đã đổi (`num.recovery.threads.per.data.dir` 1→2, `segment.bytes` min 1 MiB, `controller.quorum.auto.join.enable`=false ở 4.3), ELR mặc định từ 4.1, tool/CLI option đã xoá, log4j2, share groups, cordoned log dir (KIP-1066) | https://kafka.apache.org/43/getting-started/upgrade/ |
| 4 | [mock-exam-and-prep-guide.md](mock-exam-and-prep-guide.md) | Nguồn đề + **cảnh báo tỉ lệ ZooKeeper 118:3** trong đề dump công khai; **quy trình chạy full mock 5 bước**; **bảng theo dõi 3–4 lần mock theo 7 domain**; **bảng phân loại 5 lý do sai** (thêm nhóm *bẫy version* và *quá tay* so với CCDAK); lịch 7 ngày cuối | Tổng hợp (**không crawl**) |
| 5 | [ccaak-vs-ccdak-map.md](ccaak-vs-ccdak-map.md) | Bảng ánh xạ **nội dung CCDAK tái dùng được cho từng domain CCAAK** (kèm % tái dùng ước tính và "phải bổ sung gì"); lab CCDAK dùng lại nguyên si; **bảng 8 chỗ kiến thức CCDAK lệch với góc admin** | Tổng hợp (**không crawl**) |

> 📌 **Không lặp lại ở đây:** bảng số phải thuộc nằm ở [§6 Kế hoạch tổng](../../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng); bảng phản xạ triệu chứng ở [§7](../../../CCAAK-STUDY-PLAN.md#7-bảng-phản-xạ-triệu-chứng--hành-động); đo đạc chất lượng đề dump công khai ở [`../../VALIDATION.md`](../../VALIDATION.md) và [`../../../mock-exams/SOURCES-AND-VALIDATION.md`](../../../mock-exams/SOURCES-AND-VALIDATION.md). Đọc những chỗ đó thay vì tìm lại trong tuần 8.

## Gợi ý thứ tự đọc

1. **Đọc (1) ngay đầu tuần, TRƯỚC khi đặt lịch.** Ba thông tin quyết định kế hoạch cả tuần: hiệu lực 2 năm, **retake phải chờ 7 ngày**, và đổi lịch miễn phí chỉ khi báo trước ≥5 ngày. Biết sớm thì chọn ngày thi thoải mái và giữ được van an toàn "<70% thì lùi lịch".
2. **Đọc (4) trước bài full mock đầu tiên của tuần (mock #2).** In sẵn bảng theo dõi 7 domain và bảng 5 lý do sai; điền **ngay sau khi chấm**, đừng để hôm sau mới nhớ lại — lý do sai là thứ phai nhanh nhất.
3. **Đọc (3) vào ngày xen giữa mock #2 và #3.** Đây là file diệt nhóm sai "bẫy version" — nhóm chiếm nhiều câu sai nhất của CCAAK và cũng là nhóm dễ diệt nhất, vì chỉ cần thuộc một danh sách hữu hạn. Đọc sau mock #2 thì bạn đã biết chính xác mình dính bẫy nào.
4. **Mở (5) khi bảng theo dõi chỉ ra một domain dưới ngưỡng.** Nó cho biết phần nào của domain đó bạn **đã có sẵn từ CCDAK** (chỉ cần đọc lại) và phần nào **thật sự mới** (phải làm lab). Đọc trước khi quyết định "học lại cả tuần" — thường bạn chỉ thiếu một nửa.
5. **Đọc (2) vào ngày 6 của lịch 7 ngày cuối**, đúng lúc chạy Honorlock System Check và chuẩn bị giấy tờ. Để đến ngày 7 mới đọc là muộn: sửa tên tài khoản cho khớp giấy tờ tuỳ thân có thể mất vài ngày.
