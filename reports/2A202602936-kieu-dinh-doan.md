# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Kiều Đình Đoàn
- Mã học viên: 2A202602936
- Nhóm: 1PROMPT
- Repository/branch: https://github.com/conanWinner/K4-L3B-RAG-Pipeline.git

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Giao diện chatbot PUBG | Thiết kế giao diện HTML/CSS/JS responsive theo phong cách terminal chiến thuật; xây dựng khu vực hội thoại, quick actions, radar, trạng thái squad và form nhập câu hỏi. | `UI/index.html` | Done |
| Tài nguyên hình ảnh | Tạo và xử lý 8 vật phẩm PUBG PNG nền trong suốt; tối ưu từ 1024×1024 xuống 256×256; tích hợp ảnh nền và GIF loading đã loại nền trắng. | `UI/background.jpg`, `UI/pubg-*.png`, `UI/runner-clean.gif` | Done |
| Animation và tương tác | Xây dựng loading intro, vụ nổ, sóng xung kích, tia lửa, hiệu ứng vật phẩm văng ra và chuyển động idle. Cho phép kéo, ném, xoay, rơi và nảy vật phẩm bằng Pointer Events. | `UI/index.html` | Done |
| Chatbot demo phía client | Cài đặt lịch sử hội thoại, câu hỏi gợi ý và phản hồi theo nhóm chủ đề PUBG như điểm nhảy, loot, vòng bo, vũ khí và hồi máu. | `UI/index.html` | Done |
| Tối ưu và kiểm tra UI | Giảm số particle, ưu tiên `transform`/`opacity`, giảm kích thước ảnh và hỗ trợ `prefers-reduced-motion`; kiểm tra cú pháp HTML/JavaScript. | `UI/index.html` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Xây UI dạng một file HTML chứa CSS và JavaScript, tài nguyên ảnh đặt riêng trong thư mục `UI/`.  
   **Lý do/evidence:** Giao diện có thể mở trực tiếp để demo, không cần build frontend hoặc cài framework; toàn bộ luồng tương tác nằm trong `UI/index.html`.  
   **Trade-off:** Dễ chạy và bàn giao nhưng file HTML lớn, khó bảo trì hơn khi số component và logic tiếp tục tăng.

2. **Quyết định:** Dùng CSS transform/opacity và `requestAnimationFrame` cho animation, đồng thời tối ưu PNG xuống 256×256.  
   **Lý do/evidence:** Phiên bản đầu dùng nhiều blur/filter và ảnh 1024×1024 gây nặng; sau tối ưu, particle giảm từ 34 xuống 18 và các chuyển động chính được GPU xử lý.  
   **Trade-off:** Hiệu ứng nhẹ và mượt hơn nhưng giảm một phần độ chi tiết hình ảnh và độ phức tạp của vụ nổ.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: mở `UI/index.html` trên Microsoft Edge; thử các quick action và câu hỏi về điểm nhảy, loot, vòng bo, súng; thử kéo/ném item bằng chuột; kiểm tra responsive và chạy `node --check` với phần JavaScript trích từ HTML.
- Kết quả trước/sau nếu có: 8 ảnh vật phẩm giảm từ 1024×1024 xuống 256×256; intro giảm còn khoảng 1 giây sau loading; số tia lửa giảm từ 34 xuống 18; HTML parse thành công và JavaScript báo `syntax: OK`.
- Lỗi đã phát hiện và cách xử lý: công cụ tạo ảnh xuất dữ liệu JPEG dù mang đuôi PNG nên đã chuyển lại thành RGBA PNG và loại nền; GIF loading có nền trắng nên xử lý toàn bộ 80 frame thành `runner-clean.gif`; loại bỏ các filter động gây giật.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: chatbot hiện dùng phản hồi mô phỏng phía client, chưa kết nối trực tiếp với retrieval/generation API của pipeline RAG.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: tách CSS/JavaScript thành module và kết nối form chat với API RAG để hiển thị answer, citation, retrieval method và score thực tế.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Kiều Đình Đoàn
