# Individual contribution report

## Thông tin

- Họ và tên: Đoàn Quang Thắng
- Mã học viên: 2A202602395
- Nhóm: Nhóm L3B
- Repository/branch: [conanWinner/K4-L3B-RAG-Pipeline](https://github.com/conanWinner/K4-L3B-RAG-Pipeline) — `main`, phụ trách `feat/data-pipeline`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| T01 — Legal corpus | Thu thập và kiểm tra ba rulebook chính thức của PUBG Esports; đặt tên tệp ổn định và lưu bản gốc trong landing zone. | `data/landing/legal/`; commit `e12e491` | Done |
| T02 — News corpus | Xây crawler có timeout, User-Agent, xử lý từng URL và output JSON gồm URL, tiêu đề, ngày crawl, Markdown; bổ sung đủ năm bài và test parser. | `src/task2_crawl_news.py`, `tests/test_task2_crawl_news.py`, `data/landing/news/`; commits `e12e491`, `58f0da9` | Done |
| T03 — Chuẩn hóa Markdown | Chuyển legal PDF và news JSON sang hai nhánh Markdown; giữ metadata nguồn, kiểm tra nội dung tối thiểu và bảo đảm chạy lại không tạo bản sao. | `src/task3_convert_markdown.py`, `tests/test_task3_convert_markdown.py`, `data/standardized/`; commit `e12e491` | Done |
| T04 — Chunking và indexing | Được phân công phụ trách, tham gia lựa chọn recursive chunking và cấu hình Jina; implementation gốc T04 thuộc commit tích hợp `b997140`, chưa có commit cá nhân riêng để xác nhận toàn bộ ownership. | `src/task4_chunking_indexing.py`; phân công trong `TEAMMATES.md` | Partial |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Tách dữ liệu thành `data/landing/` và `data/standardized/`, dùng tên tệp xác định và không ghi đè khi không yêu cầu refresh.
   **Lý do/evidence:** Hai commit `e12e491` và `58f0da9` tạo đủ ba legal PDF, năm news JSON và tám Markdown; crawler chạy lại không sinh tệp trùng.
   **Trade-off:** An toàn và dễ truy vết nguồn, nhưng khi nguồn thay đổi phải chủ động dùng chế độ refresh đúng tệp.

2. **Quyết định:** Chuẩn hóa news về JSON có metadata trước khi chuyển sang Markdown, thay vì ghi thẳng HTML đã crawl vào corpus.
   **Lý do/evidence:** Mỗi JSON giữ `url`, `title`, `date_crawled`, `content_markdown`; bước T03 có thể kiểm tra schema và tạo lại Markdown một cách xác định.
   **Trade-off:** Có thêm một lớp dữ liệu và dung lượng lưu trữ, đổi lại pipeline dễ kiểm tra, tái chạy và đối chiếu nguồn hơn.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: acceptance cho legal corpus; test parser/crawler T02; test chuyển đổi T03; chạy bộ chuyển đổi hai lần để kiểm tra tính idempotent.
- Kết quả: T01 acceptance `1 passed`; khi hoàn thành T02/T03, test tập trung `5 passed` và hai acceptance tương ứng `2 passed`. Corpus đạt ba legal Markdown và năm news Markdown, mỗi tệp trên 200 ký tự.
- Lỗi đã phát hiện và cách xử lý: bản đầu chỉ có một trong năm bài news nên acceptance chưa đạt; đã bổ sung bốn URL PUBG Esports chính thức và parser riêng cho `pubgesports.com`. Dữ liệu PDF có header/footer và bảng phức tạp được nhóm tiếp tục chuẩn hóa ở các bước sau.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: T04 chưa có bằng chứng live cho toàn bộ vector index bằng Jina trong các commit cá nhân; một số bảng PDF không thể giữ nguyên `rowspan`/`colspan` như bản gốc.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: hoàn tất phép thử Jina giới hạn, lập lại Chroma index, xác nhận số vector bằng số chunk và hiệu chỉnh `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50` trên bộ câu hỏi đánh giá.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Đoàn Quang Thắng
