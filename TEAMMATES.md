# Danh sách thành viên nhóm — K4-L3B RAG Pipeline

## 1. Thông tin chung

- **Nhóm:** Nhóm L3B
- **Chủ đề dự án:** Chatbot RAG tư vấn luật thi đấu và thông tin PUBG Esports
- **Kho mã nguồn:** [conanWinner/K4-L3B-RAG-Pipeline](https://github.com/conanWinner/K4-L3B-RAG-Pipeline)

## 2. Danh sách thành viên

| STT | Họ và tên | Mã học viên | GitHub / Email | Vai trò chính | Nhánh (Branch) | Phần việc phụ trách |
|:---:|:---|:---:|:---|:---|:---|:---|
| 1 | **Đoàn Quang Thắng** | `2A202602395` | `@conanwinner`<br>`doanquangthangqt04@gmail.com` | Trưởng nhóm / Data Pipeline | `main`<br>`feat/data-pipeline` | • Thu thập legal documents (T01)<br>• Crawl news articles (T02)<br>• Chuẩn hóa dữ liệu sang Markdown (T03)<br>• Chunking & Vector Indexing ChromaDB (T04) |
| 2 | **Đỗ Việt Hoàng** | `2A202602882` | *Đang cập nhật* | Thành viên / Retrieval | `feat/retrieval` | • Dense retrieval / Semantic search (T05)<br>• BM25 retrieval / Lexical search (T06)<br>• Reciprocal Rank Fusion - RRF (T07)<br>• PageIndex fallback (T08) |
| 3 | **Kiều Đình Đoàn** | `2A202602936` | *Đang cập nhật* | Thành viên / Generation & UI | `feat/ui-generation` | • Prompt engineering & Generation có Citation (T10)<br>• Safe refusal khi thiếu evidence (T10)<br>• Giao diện chatbot Streamlit (T11)<br>• Trực quan hóa nguồn và phương thức retrieval (T11) |
| 4 | **Phạm Minh Hiếu** | `2A202602630` | *Đang cập nhật* | Thành viên / Evaluation & Integration | `feat/integration-evaluation` | • Tích hợp end-to-end retrieval pipeline (T09)<br>• Xây dựng 15+ grounded cases cho Golden Dataset (T12)<br>• Đánh giá 4 metrics (Faithfulness, Relevance, Recall, Precision)<br>• Báo cáo so sánh A/B test trong `RESULT.md` (T12) |

## 3. Phân công chi tiết theo Task (WBS)

| Task ID | Tên công việc | Thành viên phụ trách | Nhánh thực hiện | Trạng thái | Đầu ra bàn giao |
|:---|:---|:---|:---|:---:|:---|
| **T00** | Chốt đề tài và cấu hình nền | Cả nhóm | `main` | DONE | Quyết định đề tài PUBG Esports, cấu hình môi trường `.env` |
| **T01** | Thu thập tài liệu chính sách | Đoàn Quang Thắng | `feat/data-pipeline` | DONE | 3 tài liệu PDF trong `data/landing/legal/` |
| **T02** | Thu thập bài viết / tin tức | Đoàn Quang Thắng | `feat/data-pipeline` | DONE | 5 bài viết JSON trong `data/landing/news/` |
| **T03** | Chuẩn hóa dữ liệu sang Markdown | Đoàn Quang Thắng | `feat/data-pipeline` | DONE | 8 tệp Markdown trong `data/standardized/` |
| **T04** | Đọc tài liệu, chunking và indexing | Đoàn Quang Thắng | `feat/data-pipeline` | TODO | `src/task4_chunking_indexing.py` |
| **T05** | Dense retrieval (Semantic search) | Đỗ Việt Hoàng | `feat/retrieval` | TODO | `src/task5_semantic_search.py` |
| **T06** | BM25 retrieval (Lexical search) | Đỗ Việt Hoàng | `feat/retrieval` | TODO | `src/task6_lexical_search.py` |
| **T07** | Hợp nhất thứ hạng RRF | Đỗ Việt Hoàng | `feat/retrieval` | TODO | `src/task7_reranking.py` |
| **T08** | PageIndex fallback | Đỗ Việt Hoàng | `feat/retrieval` | TODO | `src/task8_pageindex_vectorless.py` |
| **T09** | Pipeline truy xuất hoàn chỉnh | Phạm Minh Hiếu | `feat/integration-evaluation` | TODO | `src/task9_retrieval_pipeline.py` |
| **T10** | Sinh câu trả lời có trích dẫn | Kiều Đình Đoàn | `feat/ui-generation` | TODO | `src/task10_generation.py` |
| **T11** | Hoàn thiện giao diện Streamlit | Kiều Đình Đoàn | `feat/ui-generation` | TODO | `app.py` |
| **T12** | Golden dataset, đánh giá và bàn giao | Phạm Minh Hiếu & Cả nhóm | `feat/integration-evaluation` | TODO | `group_project/evaluation/RESULT.md`, `golden_dataset.json` |

## 4. Quy ước làm việc nhóm

- **Quy tắc phân nhánh (Branching convention):**
  - Nhánh chính: `main` (luôn giữ trạng thái ổn định, chỉ merge khi code đã qua test hợp đồng và nghiệm thu).
  - Nhánh chức năng:
    - `feat/data-pipeline`: Phần việc Data (Đoàn Quang Thắng).
    - `feat/retrieval`: Phần việc Retrieval & Reranking (Đỗ Việt Hoàng).
    - `feat/ui-generation`: Phần việc Generation & Streamlit (Kiều Đình Đoàn).
    - `feat/integration-evaluation`: Phần việc Tích hợp & Đánh giá (Phạm Minh Hiếu).
- **Báo cáo đóng góp cá nhân (Individual Report):**
  - Mỗi thành viên copy file mẫu [reports/INDIVIDUAL_REPORT.md](reports/INDIVIDUAL_REPORT.md) thành:
    - `reports/2A202602395-Thang.md`
    - `reports/2A202602882-Hoang.md`
    - `reports/2A202602936-Doan.md`
    - `reports/2A202602630-Hieu.md`
  - Ghi nhận đầy đủ commit hash, pull request và file code do bản thân thực hiện để phục vụ chấm điểm.
- **Cam kết chất lượng code & an toàn:**
  - Luôn kiểm tra local test trước khi push:
    ```bash
    pytest tests/test_contracts.py -q
    pytest tests/test_acceptance.py -q
    ```
  - Tuyệt đối không commit file `.env`, API key cá nhân lên repository.
