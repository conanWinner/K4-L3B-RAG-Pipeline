# Nhật ký triển khai

Tệp này dùng để lưu dấu vết công việc. Chỉ nối thêm mục mới theo thời gian; không sửa lại lịch sử để làm đẹp kết quả. Nếu một kết luận cũ sai, thêm mục mới giải thích điều chỉnh.

## Quy tắc ghi trace

Mỗi lần làm việc cần ghi:

- Thời gian và người/tác nhân thực hiện.
- Task ID tương ứng trong `TASKS.md`.
- Mục tiêu ngắn gọn.
- Tệp đã thay đổi.
- Lệnh kiểm tra đã chạy.
- Kết quả thực tế: pass/fail và số lượng cụ thể.
- Lỗi hoặc giới hạn còn lại.
- Bước tiếp theo.

Không ghi API key, access token, cookie, dữ liệu cá nhân hoặc toàn bộ nội dung `.env` vào trace.

## Mẫu cho mỗi lần cập nhật

```markdown
## YYYY-MM-DD HH:MM — Txx — Tiêu đề ngắn

- Người thực hiện:
- Mục tiêu:
- Trạng thái: IN_PROGRESS | BLOCKED | DONE
- Tệp thay đổi:
  - `path/to/file`
- Thay đổi chính:
  - ...
- Kiểm tra:
  - Lệnh: `...`
  - Kết quả: ...
- Bằng chứng/dữ liệu:
  - ...
- Vấn đề còn lại:
  - ...
- Bước tiếp theo:
  - ...
```

## 2026-09-25 — INIT — Khảo sát trạng thái ban đầu

- Người thực hiện: Codex
- Mục tiêu: Đọc hiểu cấu trúc và xác định mức độ hoàn thiện hiện tại.
- Trạng thái: DONE
- Tệp thay đổi:
  - `project_docs/TASKS.md`
  - `project_docs/TRACE.md`
  - `AGENTS.md`
- Kết quả khảo sát:
  - Repo là bộ khung bài lab RAG; phần lớn hàm Task 1–10 vẫn là `NotImplementedError`.
  - Corpus hiện có 0 tài liệu legal và 0 bài news.
  - `group_project/evaluation/golden_dataset.json` đang rỗng.
  - Giao diện Streamlit vẫn trả nội dung placeholder.
  - Có sai lệch giữa vị trí báo cáo mà test yêu cầu và mẫu báo cáo hiện có.
- Kiểm tra:
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`
  - Kết quả: 7 passed, 13 failed.
- Vấn đề còn lại:
  - Chưa chọn/chốt nguồn dữ liệu và provider.
  - Chưa triển khai pipeline end-to-end.
- Bước tiếp theo:
  - Thực hiện T00, sau đó T01 và T02.

## 2026-09-25 — T01 — Thu thập tài liệu luật PUBG Esports

- Người thực hiện: Codex
- Mục tiêu: Chuẩn bị tối thiểu 3 PDF cùng chủ đề luật thi đấu PUBG Esports.
- Trạng thái: DONE
- Tệp dữ liệu:
  - `data/landing/legal/pubg_super_v6.0.1.pdf` — 25 trang, 1.003.573 bytes.
  - `data/landing/legal/pubg_global_championship_2024_rules.pdf` — 24 trang, 854.485 bytes.
  - `data/landing/legal/pubg_ewc_2026_rulebook.pdf` — 32 trang, 8.383.915 bytes.
- Nguồn:
  - `https://pubgesports.com/download/UPDATED-SUPERv6.0.1.pdf`
  - `https://wstatic-prod-boc.krafton.com/common/default/20241206/1tyjv0P1/PUBG%20GLOBAL%20CHAMPIONSHIP%202024_Tournament_Rules_EN_1206.pdf`
  - `https://cdn.esportsworldcup.com/resources/uploads/PUBG_BATTLEGROUNDS_at_2026_Esports_World_Cup_Rulebook_423e7cbd82.pdf`
- Thay đổi chính:
  - Đổi tên PDF người dùng đã tải thành `pubg_super_v6.0.1.pdf`.
  - Tải thêm hai rulebook cùng chủ đề và đặt tên thống nhất.
  - Xác minh định dạng, số trang và khả năng trích xuất văn bản của cả ba PDF.
- Kiểm tra:
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest tests/test_acceptance.py::test_corpus_has_required_legal_documents -q -p no:cacheprovider`
  - Kết quả: `1 passed`.
- Vấn đề còn lại:
  - Chưa chuyển các PDF sang Markdown; công việc này thuộc T03.
- Bước tiếp theo:
  - Thực hiện T02: thu thập tối thiểu 5 bài viết cùng chủ đề từ URL.

## 2026-09-25 — T02 — Crawl URL đầu tiên cho bản demo

- Người thực hiện: Codex
- Mục tiêu: Crawl trang PUBG Terms of Service thành JSON có thể đưa sang bước chuẩn hóa.
- Trạng thái: IN_PROGRESS
- Tệp thay đổi:
  - `src/task2_crawl_news.py`
  - `data/landing/news/pubg_terms_of_service.json`
- Nguồn:
  - `https://pubg.com/en/clause/term_of_service/label_steam/latest`
- Thay đổi chính:
  - Thêm URL demo và tên đầu ra ổn định.
  - Dùng `requests` có timeout và User-Agent; không cần cài browser cho bản demo.
  - Chỉ trích xuất thẻ nội dung chính, loại menu và footer.
  - Lưu đủ `url`, `title`, `date_crawled`, `content_markdown`.
  - Mặc định bỏ qua JSON đã tồn tại; chỉ cập nhật đúng tệp cấu hình khi dùng `--refresh`.
- Kiểm tra:
  - Chạy crawl thật thành công; tiêu đề là `PUBG: BATTLEGROUNDS Terms of Service`.
  - JSON validation: pass, nội dung 32.790 ký tự, không chứa footer.
  - Chạy lại không có `--refresh`: bỏ qua file hiện có, không tạo bản trùng.
  - `pytest tests/test_contracts.py -q -p no:cacheprovider`: 7 passed, 8 failed do Task 4–10 chưa triển khai.
  - `pytest tests/test_acceptance.py::test_corpus_has_required_news_with_metadata -q -p no:cacheprovider`: fail đúng dự kiến vì bản demo mới có 1/5 JSON.
- Vấn đề còn lại:
  - T02 chưa đạt tiêu chí bài nộp tối thiểu 5 URL nên chưa được đánh dấu `DONE`.
  - Terms of Service là quy định chung của trò chơi, không chỉ tập trung vào Esports.
- Bước tiếp theo:
  - Có thể thực hiện T03 cho bản demo với dữ liệu hiện có; bổ sung 4 URL trước khi nghiệm thu bài nộp.

## 2026-09-25 10:11 — T03 — Chuẩn hóa corpus hiện có sang Markdown

- Người thực hiện: Codex
- Mục tiêu: Hoàn thiện bộ chuyển đổi PDF/DOCX và JSON, sau đó chuẩn hóa dữ liệu T01–T02 hiện có.
- Trạng thái: BLOCKED
- Tệp thay đổi:
  - `src/task3_convert_markdown.py`
  - `tests/test_task3_convert_markdown.py`
  - `data/standardized/legal/pubg_ewc_2026_rulebook.md`
  - `data/standardized/legal/pubg_global_championship_2024_rules.md`
  - `data/standardized/legal/pubg_super_v6.0.1.md`
  - `data/standardized/news/pubg_terms_of_service.md`
  - `project_docs/TASKS.md`
  - `project_docs/TRACE.md`
- Thay đổi chính:
  - Chuyển PDF/DOC/DOCX bằng MarkItDown khi có; môi trường hiện tại dùng `pdftotext` cục bộ cho PDF vì chưa cài module MarkItDown.
  - Chuyển JSON sang Markdown và giữ `title`, `url`, `date_crawled` ở đầu tệp.
  - Kiểm tra JSON bắt buộc, lỗi mã hóa rõ ràng, nội dung dưới 200 ký tự và xung đột tên đầu ra.
  - Chỉ cập nhật output khi nội dung thay đổi; không sửa dữ liệu nguồn và không xóa output cũ.
- Kiểm tra:
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest tests/test_task3_convert_markdown.py -q -p no:cacheprovider`
  - Kết quả: `3 passed`.
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 python -m src.task3_convert_markdown` (chạy hai lần)
  - Kết quả: lần đầu tạo 3 legal + 1 news; lần hai báo `0 updated` cho cả hai nhánh.
  - Kiểm tra nội dung: cả 4 tệp đều trên 200 ký tự, không có ký tự thay thế Unicode và không có dòng trùng liền nhau.
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest tests/test_contracts.py -q -p no:cacheprovider`
  - Kết quả: `7 passed, 8 failed`; các lỗi còn lại thuộc placeholder T04–T10.
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest tests/test_acceptance.py -q -p no:cacheprovider`
  - Kết quả: `1 passed, 4 failed`; T03 thiếu 4 news, hai lỗi còn lại thuộc T12.
  - Lệnh: `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`
  - Kết quả: `11 passed, 12 failed`; không có lỗi từ kiểm thử riêng của T03.
- Bằng chứng/dữ liệu:
  - Legal Markdown: 3 tệp, từ 50.804 đến 68.743 ký tự.
  - News Markdown: 1 tệp, 32.921 ký tự, có URL và ngày crawl ở đầu tệp.
- Vấn đề còn lại:
  - T02 mới có 1/5 JSON nên T03 chỉ tạo được 1/5 news Markdown và chưa đạt acceptance.
  - Chưa kiểm tra thủ công toàn bộ bảng trong cả 3 PDF; `pdftotext -layout` đã giữ bố cục văn bản ở mức trích xuất được.
- Bước tiếp theo:
  - Hoàn thành T02 với 4 bài news còn thiếu, chạy lại T03 và nghiệm thu đủ 3 legal + 5 news.
