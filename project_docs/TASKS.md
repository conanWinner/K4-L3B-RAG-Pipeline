# Kế hoạch triển khai RAG Pipeline

Tài liệu này là danh sách công việc chính thức của dự án. Thực hiện theo thứ tự từ T00 đến T12 vì đầu ra của bước trước là đầu vào của bước sau.

## Quy ước trạng thái

- `TODO`: chưa bắt đầu.
- `IN_PROGRESS`: đang thực hiện.
- `BLOCKED`: bị chặn; phải ghi nguyên nhân và điều kiện gỡ chặn trong `TRACE.md`.
- `DONE`: đã hoàn thành và có bằng chứng kiểm tra.

Không đánh dấu `DONE` chỉ vì đã viết code. Một task chỉ hoàn thành khi đạt toàn bộ tiêu chí nghiệm thu và có bằng chứng được ghi trong `TRACE.md`.

## T00 — Chốt đề tài và cấu hình nền

**Trạng thái:** TODO

**Mục tiêu:** Xác định rõ chatbot sẽ trả lời về phạm vi nào và dùng nhà cung cấp mô hình nào.

**Cách làm:**

1. Chọn một chủ đề đủ ổn định và có ít nhất 3 tài liệu chính sách cùng 5 bài viết công khai. Chủ đề mặc định phù hợp với code hiện tại là dịch vụ đại học.
2. Ghi phạm vi câu hỏi được hỗ trợ và 3–5 nhóm câu hỏi ngoài phạm vi.
3. Copy `.env.example` thành `.env`; chỉ điền khóa của dịch vụ thực sự sử dụng và tuyệt đối không commit `.env`.
4. Chọn một embedding model duy nhất cho cả lúc lập chỉ mục và lúc tìm kiếm.
5. Ghi phiên bản Python, model, embedding model và ngày thu thập dữ liệu vào trace.

**Tiêu chí hoàn thành:** Chủ đề, nguồn dự kiến, provider và model được ghi rõ; `git status` không hiển thị `.env`.

## T01 — Thu thập tài liệu chính sách

**Trạng thái:** DONE

**Tệp chính:** `src/task1_collect_legal_docs.py`

**Cách làm:**

1. Lập danh sách ít nhất 3 URL chính thức tới PDF, DOC hoặc DOCX.
2. Ưu tiên tải thủ công nếu trang có điều khoản hoặc cơ chế chống crawler; không vượt WAF hay cơ chế bảo vệ website.
3. Nếu tự động tải, dùng timeout, kiểm tra HTTP status và kiểm tra loại nội dung trước khi ghi file.
4. Lưu bản gốc vào `data/landing/legal/` với tên không dấu, có ý nghĩa và không ghi đè file khác ngoài ý muốn.
5. Ghi URL, ngày tải, tên file và kích thước vào `TRACE.md`.

**Tiêu chí hoàn thành:** Có ít nhất 3 tệp hợp lệ, mỗi tệp lớn hơn 1 KB và mở/đọc được.

## T02 — Thu thập bài viết hoặc thông báo

**Trạng thái:** IN_PROGRESS — bản demo đã crawl 1/5 URL

**Tệp chính:** `src/task2_crawl_news.py`

**Cách làm:**

1. Điền ít nhất 5 URL công khai vào `ARTICLE_URLS` hoặc cấu hình tương đương.
2. Crawl bằng Crawl4AI hoặc công cụ phù hợp, có timeout và xử lý lỗi theo từng URL.
3. Chuẩn hóa mỗi kết quả thành JSON gồm `url`, `title`, `date_crawled`, `content_markdown`.
4. Loại bỏ nội dung điều hướng, footer và phần rỗng nhưng không làm sai nội dung nguồn.
5. Lưu từng bài riêng trong `data/landing/news/`; chạy lại phải cho kết quả xác định và không tạo bản trùng không cần thiết.

**Tiêu chí hoàn thành:** Có ít nhất 5 JSON hợp lệ, đủ metadata và nội dung không rỗng.

## T03 — Chuẩn hóa dữ liệu sang Markdown

**Trạng thái:** BLOCKED — code đã hoàn thiện; chờ T02 bổ sung đủ 4 bài news còn thiếu

**Tệp chính:** `src/task3_convert_markdown.py`

**Cách làm:**

1. Chuyển PDF/DOCX sang Markdown bằng MarkItDown hoặc công cụ đã chọn.
2. Chuyển JSON bài viết sang Markdown và giữ tiêu đề, URL, ngày crawl ở đầu tài liệu.
3. Giữ hai nhánh `data/standardized/legal/` và `data/standardized/news/`.
4. Kiểm tra file rỗng, lỗi mã hóa, chữ bị vỡ, bảng bị mất và nội dung lặp.
5. Đảm bảo tên đầu ra ổn định để chạy lại không phát sinh bản sao.

**Tiêu chí hoàn thành:** Có ít nhất 3 Markdown legal và 5 Markdown news; mỗi file có tối thiểu 200 ký tự có nghĩa.

## T04 — Đọc tài liệu, chia đoạn, embedding và lập chỉ mục

**Trạng thái:** TODO

**Tệp chính:** `src/task4_chunking_indexing.py`

**Cách làm:**

1. Hoàn thiện `load_documents()` để đọc toàn bộ Markdown và tạo đúng `Document` contract.
2. Hoàn thiện `chunk_documents()` bằng bộ chia recursive, ban đầu dùng `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50` rồi điều chỉnh dựa trên dữ liệu thật.
3. Sinh ID ổn định theo tài liệu và thứ tự chunk; giữ nguyên `source`, `title`, `doc_type`, `url` và thêm `chunk_index`.
4. Hoàn thiện `embed_texts()`; cùng một hàm phải được Task 5 sử dụng cho query.
5. Kiểm tra số vector và chiều vector khớp với số chunk và model.
6. Tạo Chroma collection dùng cosine distance và `upsert` theo ID để chạy lại không tạo trùng.

**Tiêu chí hoàn thành:** Test chunk pass; mọi chunk hợp lệ, không rỗng, ID duy nhất; index lại không tăng số bản ghi ngoài dự kiến.

## T05 — Dense retrieval

**Trạng thái:** TODO

**Tệp chính:** `src/task5_semantic_search.py`

**Cách làm:**

1. Embed query bằng chính `embed_texts()` của T04.
2. Query Chroma với `n_results=top_k` và lấy document, metadata, distance.
3. Đổi cosine distance thành similarity theo quy ước của collection.
4. Map về `SearchResult` với `retrieval_method="dense"`.
5. Khử ID trùng, sắp xếp score giảm dần và giới hạn đúng `top_k`.

**Tiêu chí hoàn thành:** Contract test dense pass và các query trong miền trả về đoạn liên quan ở nhóm đầu.

## T06 — BM25 retrieval

**Trạng thái:** TODO

**Tệp chính:** `src/task6_lexical_search.py`

**Cách làm:**

1. Nạp đúng cùng corpus chunk đã dùng để lập vector index.
2. Chọn tokenizer phù hợp với tiếng Việt; ghi rõ lựa chọn thay vì mặc định coi khoảng trắng luôn đủ tốt.
3. Xây BM25 index một lần và tái sử dụng, tránh dựng lại cho mọi query nếu chạy trong ứng dụng.
4. Map kết quả về `SearchResult` với `retrieval_method="bm25"`.
5. Loại score không có ý nghĩa, khử trùng và sort giảm dần.

**Tiêu chí hoàn thành:** Contract test BM25 pass; query chứa mã, tên riêng hoặc cụm từ chính xác tìm được đúng tài liệu.

## T07 — Hợp nhất thứ hạng bằng RRF

**Trạng thái:** TODO

**Tệp chính:** `src/task7_reranking.py`

**Cách làm:**

1. Nhận danh sách dense và BM25 đã được xếp hạng.
2. Tính `sum(1 / (k + rank))`, với rank bắt đầu từ 1.
3. Gộp theo ID, không cộng trực tiếp cosine score với BM25 score.
4. Sao chép item trước khi đổi score để không làm biến đổi input.
5. Đặt `retrieval_method="hybrid"`, sort giảm dần và cắt `top_k`.

**Tiêu chí hoàn thành:** Test RRF pass; một chunk xuất hiện cao ở cả hai danh sách được ưu tiên và không bị lặp.

## T08 — PageIndex fallback

**Trạng thái:** TODO

**Tệp chính:** `src/task8_pageindex_vectorless.py`

**Cách làm:**

1. Chỉ tích hợp sau khi dense, BM25 và RRF đã chạy ổn định.
2. Đọc khóa từ môi trường; không log hoặc ghi khóa vào repo.
3. Upload tài liệu theo định dạng SDK thật sự hỗ trợ và lưu mapping document ID để tránh upload lại.
4. Thêm timeout, xử lý lỗi mạng/provider và parse response dựa trên phản hồi thật.
5. Map về `SearchResult` với `retrieval_method="pageindex"`; nếu provider không có score, dùng score giảm dần theo rank và ghi rõ quy ước.

**Tiêu chí hoàn thành:** Query fallback trả đúng contract; lỗi provider không làm ứng dụng crash.

## T09 — Pipeline truy xuất hoàn chỉnh

**Trạng thái:** TODO

**Tệp chính:** `src/task9_retrieval_pipeline.py`

**Cách làm:**

1. Chạy dense và BM25 trên cùng query.
2. Hợp nhất bằng RRF đúng một lần khi `use_reranking=True`; nếu tắt thì trả dense.
3. Dùng cosine score gốc tốt nhất của dense để so threshold, không dùng RRF score.
4. Nếu dưới threshold, thử PageIndex; nếu PageIndex lỗi hoặc rỗng, trả hybrid thay vì crash.
5. Hiệu chỉnh threshold bằng cả query đúng miền và ngoài miền; ghi bảng thử nghiệm vào trace.

**Tiêu chí hoàn thành:** Ba test về fallback/RRF pass; output đúng contract trong cả nhánh bình thường, fallback và provider lỗi.

## T10 — Sinh câu trả lời có trích dẫn

**Trạng thái:** TODO

**Tệp chính:** `src/task10_generation.py`

**Cách làm:**

1. Hoàn thiện `reorder_for_llm()` nhưng không làm thay đổi danh sách đầu vào hay mất ID.
2. Hoàn thiện `format_context()` để mỗi đoạn có nhãn, tiêu đề và nguồn kiểm chứng được.
3. Hoàn thiện `call_llm()` cho provider được chọn; đặt timeout và trả lỗi có kiểm soát.
4. Prompt phải yêu cầu chỉ trả lời từ context và gắn citation cho các khẳng định.
5. Nếu không có evidence hoặc provider lỗi, trả safe refusal thay vì bịa câu trả lời.
6. `sources` phải giữ các chunk gốc để citation có thể đối chiếu.

**Tiêu chí hoàn thành:** Generation contract pass; câu trả lời đúng miền có citation hợp lệ, câu ngoài miền bị từ chối an toàn.

## T11 — Hoàn thiện giao diện Streamlit

**Trạng thái:** TODO

**Tệp chính:** `app.py`

**Cách làm:**

1. Thay nội dung placeholder bằng chủ đề và hướng dẫn thật.
2. Gọi `generate_with_citation(query, top_k)`.
3. Lưu cả câu trả lời và nguồn vào `st.session_state` để lịch sử hiển thị đúng sau mỗi lần rerun.
4. Hiển thị title, source/URL, phương thức retrieval và score cho từng nguồn.
5. Bắt lỗi ở biên UI và hiển thị thông báo hữu ích, không để lộ API key hoặc stack trace nhạy cảm.

**Tiêu chí hoàn thành:** Demo được một câu đúng miền, một câu ngoài miền và một tình huống provider lỗi mà UI không crash.

## T12 — Golden dataset, đánh giá và bàn giao

**Trạng thái:** TODO

**Tệp chính:** `group_project/evaluation/golden_dataset.json`, báo cáo đánh giá và báo cáo cá nhân.

**Cách làm:**

1. Tạo tối thiểu 15 trường hợp gồm `question`, `expected_answer`, `expected_context`; tất cả phải dựa trên corpus thật.
2. Viết runner đánh giá có thể chạy lại cho faithfulness, answer relevance, context recall và context precision.
3. So sánh dense-only với hybrid + RRF trên cùng dataset, generator, evaluator, prompt và `top_k`.
4. Lưu cấu hình, phiên bản model, thời gian, chi phí/độ trễ và kết quả thô trước khi tổng hợp.
5. Phân tích ít nhất 3 trường hợp kém nhất và đưa khuyến nghị có cách kiểm chứng.
6. Thống nhất vị trí báo cáo: test hiện yêu cầu `group_project/evaluation/RESULT.md`, trong khi repo đang có mẫu `reports/RESULT.md`.
7. Cập nhật README cho đúng đường dẫn thực tế và hoàn thiện báo cáo cá nhân có dẫn chứng commit/test.
8. Chạy toàn bộ test và kiểm tra repo không chứa secret.

**Tiêu chí hoàn thành:** `pytest -q` pass; báo cáo không còn placeholder; kết quả A/B có số liệu và có thể chạy lại.

## Thứ tự kiểm tra khuyến nghị

```bash
pytest tests/test_contracts.py -q
pytest tests/test_acceptance.py -q
pytest -q
git status --short
```

Các lệnh gọi API thật, crawl website, tải model hoặc upload dữ liệu phải được ghi riêng trong `TRACE.md`, kèm cấu hình và kết quả thực tế.
