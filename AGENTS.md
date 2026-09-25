# Hướng dẫn làm việc trong K4-L3B-RAG-Pipeline

## Mục tiêu dự án

Xây dựng chatbot RAG từ bộ tài liệu do nhóm thu thập. Pipeline bắt buộc gồm chuẩn hóa dữ liệu, chunking, embedding, dense retrieval, BM25, RRF, fallback, generation có citation, giao diện Streamlit và đánh giá A/B.

Đây hiện là starter template. Không được mô tả một chức năng là đã hoàn thành nếu code vẫn là placeholder, chưa có dữ liệu thật hoặc chưa có bằng chứng kiểm tra.

## Tài liệu phải đọc trước khi sửa

1. `README.md`
2. `docs/MODULE_CONTRACTS.md`
3. `project_docs/TASKS.md`
4. `project_docs/TRACE.md`
5. Test liên quan trong `tests/`

Khi hợp đồng, test và README mâu thuẫn, không tự âm thầm chọn một phía. Ghi rõ mâu thuẫn vào trace và sửa đồng bộ khi phạm vi công việc cho phép.

## Quy trình bắt buộc

1. Chọn task chưa hoàn thành trong `project_docs/TASKS.md`.
2. Đọc module liền trước, module đang sửa và test liên quan để hiểu đầu vào/đầu ra.
3. Thực hiện thay đổi nhỏ nhất đủ hoàn thành task; không tái cấu trúc phần không liên quan.
4. Chạy test contract trước, acceptance sau, rồi mới chạy toàn bộ test.
5. Cập nhật trạng thái và thêm bằng chứng vào `project_docs/TRACE.md` trong cùng lần thay đổi.
6. Báo cáo rõ phần đã làm, chưa làm và giới hạn chưa được kiểm chứng.

## Hợp đồng kỹ thuật phải giữ

- Document/chunk phải giữ ID ổn định và metadata nguồn xuyên suốt pipeline.
- Chunk không rỗng, có `chunk_index`, và chạy index lại không tạo bản ghi trùng.
- Index và query phải dùng cùng embedding model, cùng chiều vector và cùng `embed_texts()`.
- Search result phải đúng schema, ID không trùng, score giảm dần và không vượt `top_k`.
- Dense dùng `retrieval_method="dense"`; BM25 dùng `"bm25"`; RRF dùng `"hybrid"`; fallback dùng `"pageindex"`.
- RRF chỉ hợp nhất thứ hạng đúng một lần. Không cộng trực tiếp cosine score với BM25 score.
- Quyết định fallback phải dựa trên cosine score gốc của dense retrieval, không dựa trên RRF score.
- Lỗi PageIndex hoặc LLM provider không được làm UI crash.
- Citation phải đối chiếu được với phần tử trong `sources`.
- Khi thiếu bằng chứng, trả safe refusal; không bịa câu trả lời.

## Dữ liệu và bảo mật

- Tuyệt đối không xoá tệp, thư mục, dữ liệu, lịch sử Git, branch hoặc worktree nếu chưa có xác nhận rõ ràng trong cuộc trò chuyện hiện tại.
- Cấm format, reformat, wipe hoặc khởi tạo lại bất kỳ thiết bị/volume/hệ thống tệp nào.
- Không ghi đè dữ liệu nguồn nếu chưa xác định chính xác tệp đích và khả năng khôi phục.
- Không commit `.env`, API key, token, cookie hoặc thông tin cá nhân.
- Không in secret vào terminal, test output, log hoặc `TRACE.md`.
- Không vượt WAF, CAPTCHA, robots policy hoặc điều khoản của nguồn dữ liệu.
- Ưu tiên nguồn chính thức và ghi lại URL cùng ngày thu thập.
- Không chạy upload, crawl diện rộng, gọi API trả phí hoặc tải model lớn nếu nhiệm vụ chỉ yêu cầu đọc hiểu/review.

## Quy tắc code

- Hỗ trợ Python theo `pyproject.toml`.
- Giữ nguyên public function signatures mà `tests/test_contracts.py` kiểm tra.
- Dùng type hints cho interface công khai; tránh schema riêng khi `src/contracts.py` đã có định nghĩa.
- Thiết kế tác vụ dữ liệu có thể chạy lại an toàn và cho kết quả xác định.
- Thêm timeout và xử lý lỗi cho mọi network/provider call.
- Không bắt `Exception` rồi im lặng, trừ ranh giới fallback đã có hành vi thay thế rõ ràng; khi phù hợp phải ghi lỗi có kiểm soát.
- Không hard-code khóa, đường dẫn máy cá nhân hoặc kết quả đánh giá.
- Test unit/contract không được gọi mạng hay API thật.

## Kiểm tra

Ưu tiên chạy:

```bash
pytest tests/test_contracts.py -q
pytest tests/test_acceptance.py -q
pytest -q
```

Khi chỉ khảo sát và không muốn tạo cache:

```bash
PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider
```

Mock test pass chỉ chứng minh contract cục bộ. Không được dùng nó làm bằng chứng rằng provider thật, API key, crawl, embedding model, ChromaDB hoặc chatbot end-to-end đã hoạt động.

## Định nghĩa hoàn thành

Một task chỉ được đánh dấu `DONE` khi:

- Không còn placeholder trong phạm vi task.
- Test liên quan pass.
- Nếu có dịch vụ thật, đã có một phép thử giới hạn và bằng chứng không chứa secret.
- Đầu ra đúng contract và có thể chạy lại.
- `project_docs/TRACE.md` đã ghi lệnh, kết quả và giới hạn còn lại.

Không tự thay dữ liệu đánh giá bằng số liệu giả. Nếu chưa thể chạy thật, giữ trạng thái `BLOCKED` hoặc `IN_PROGRESS` và nói rõ điều kiện còn thiếu.
