# Secure Chat UI Design

## Mục tiêu

Xây dựng hai ứng dụng web local độc lập trong:

- `lab04/UI-AES-RSA`
- `lab04/UI-DH-AES`

Mỗi ứng dụng phải:

- Có giao diện web dùng `HTML`, `CSS`, `Bootstrap`
- Cho nhiều client chat thật với nhau qua server
- Bám sát yêu cầu đề bài: secure chat thông qua server
- Không sửa code trong `lab04/aes_rsa_socket` và `lab04/dh_key_pair`
- Tự chạy độc lập trong chính folder của nó

## Phạm vi

### 1. UI-AES-RSA

Ứng dụng web local mô phỏng bài secure chat dùng cơ chế:

- Server giữ cặp khóa `RSA`
- Mỗi client sinh `AES session key`
- Client dùng `RSA public key` của server để mã hóa `AES session key`
- Sau khi bắt tay xong, client và server trao đổi tin nhắn bằng `AES`
- Server đóng vai trò trung gian chuyển tiếp tin nhắn giữa các client

### 2. UI-DH-AES

Ứng dụng web local mô phỏng bài secure chat dùng cơ chế:

- Server sinh khóa công khai/phần riêng `Diffie-Hellman`
- Client và server trao đổi public key
- Hai bên dẫn xuất `shared secret`
- Từ `shared secret` sinh ra khóa `AES`
- Sau khi bắt tay xong, client và server trao đổi tin nhắn bằng `AES`
- Server đóng vai trò trung gian chuyển tiếp tin nhắn giữa các client

## Ràng buộc

- Không chỉnh sửa bài gốc trong `lab04/aes_rsa_socket` và `lab04/dh_key_pair`
- Mọi phần bổ sung phải nằm trong đúng hai folder `UI-AES-RSA` và `UI-DH-AES`
- Nội dung giao diện dùng tiếng Việt có dấu
- Các thuật ngữ kỹ thuật hoặc chữ tiếng Anh giữ nguyên tiếng Anh khi phù hợp
- Giao diện dùng `Bootstrap` để tăng tốc triển khai và bảo đảm trình bày rõ ràng

## Kiến trúc đề xuất

Khuyến nghị dùng cùng một mô hình triển khai cho cả hai bài:

- Backend Python dùng `Flask` + `Flask-SocketIO`
- Frontend server-rendered với `Jinja2` hoặc HTML tĩnh do Flask phục vụ
- Realtime chat qua `Socket.IO`
- Crypto xử lý ở backend Python để bám sát logic bài tập và dễ demo

Lý do chọn hướng này:

- Một process có thể vừa phục vụ web UI vừa làm realtime chat server
- Hỗ trợ nhiều client trình duyệt đồng thời
- Dễ thể hiện trạng thái kết nối, log bắt tay, người dùng online
- Đơn giản hơn mô hình TCP socket thuần + browser bridge

## Cấu trúc thư mục mục tiêu

Mỗi folder UI sẽ có cấu trúc gần giống nhau:

```text
UI-*/ 
  app.py
  requirements.txt
  templates/
    index.html
  static/
    css/
      styles.css
    js/
      app.js
  crypto/
    ...
```

Trong đó:

- `app.py`: web server + chat server + session manager
- `templates/index.html`: giao diện chính
- `static/css/styles.css`: tinh chỉnh giao diện ngoài Bootstrap
- `static/js/app.js`: logic tương tác UI và Socket.IO client
- `crypto/`: helper mã hóa/giải mã, tách riêng cho từng bài nếu cần

## Thiết kế giao diện

Mỗi ứng dụng chỉ cần một trang chính để demo rõ bài tập.

### Bố cục

1. Thanh tiêu đề
   - Tên bài
   - Mô tả ngắn cơ chế bảo mật đang dùng

2. Khu vực thông tin phiên
   - Tên hiển thị
   - Trạng thái kết nối
   - Trạng thái bắt tay khóa
   - Session ID hoặc client ID ngắn

3. Khu vực log bảo mật
   - Các bước handshake
   - Thông báo sinh khóa / trao đổi khóa / thiết lập AES session
   - Lỗi nếu có

4. Khu vực chat chính
   - Danh sách tin nhắn
   - Phân biệt `Tôi`, `Người khác`, `Hệ thống`

5. Khu vực nhập liệu
   - Ô nhập tin nhắn
   - Nút `Gửi`
   - Nút `Ngắt kết nối`

6. Khu vực danh sách online
   - Tên các client đang kết nối

### Nguyên tắc trình bày

- Giao diện rõ ràng, dễ demo trên lớp
- Ưu tiên card, badge, alert, list-group của Bootstrap
- Màu sắc vừa phải, phân tách rõ phần chat và phần log kỹ thuật
- Không thêm các tính năng ngoài bài như đăng nhập tài khoản, DB, upload file

## Luồng hoạt động

### Luồng chung

1. Người dùng mở trang web
2. Nhập tên hiển thị
3. Bấm `Kết nối`
4. Client tham gia phiên chat qua server
5. Thực hiện bắt tay bảo mật theo bài tương ứng
6. Khi handshake hoàn tất, client gửi và nhận tin nhắn thời gian thực
7. Khi người dùng thoát, server phát thông báo rời phòng

### Luồng chi tiết cho UI-AES-RSA

1. Server khởi động và sinh cặp khóa `RSA`
2. Client kết nối, server gửi `RSA public key`
3. Client sinh `AES session key`
4. Client mã hóa `AES session key` bằng `RSA public key` rồi gửi lại server
5. Server giải mã để lấy khóa AES của client đó
6. Khi client gửi tin nhắn:
   - Client mã hóa bằng AES
   - Server giải mã
   - Server mã hóa lại bằng AES key tương ứng của từng client nhận
7. Các client nhận và giải mã trước khi hiển thị

### Luồng chi tiết cho UI-DH-AES

1. Server khởi động và sinh cặp khóa `Diffie-Hellman`
2. Client kết nối, nhận `DH public key` hoặc thông số cần thiết
3. Client sinh cặp khóa của riêng mình
4. Client gửi `DH public key` lên server
5. Hai bên dẫn xuất `shared secret`
6. Từ `shared secret`, mỗi phía dẫn xuất `AES key`
7. Khi client gửi tin nhắn:
   - Client mã hóa bằng AES
   - Server giải mã
   - Server mã hóa lại cho từng client nhận bằng key phiên tương ứng
8. Các client nhận và giải mã trước khi hiển thị

## Thành phần backend

Mỗi ứng dụng cần các nhóm thành phần sau:

### 1. Web app

- Phục vụ HTML/CSS/JS
- Expose route chính `/`

### 2. Socket event handlers

- `connect`
- `join`
- `send_message`
- `disconnect`

### 3. Session manager

Lưu cho từng client:

- socket/session id
- display name
- trạng thái handshake
- crypto material theo bài tương ứng

### 4. Crypto helpers

Tách logic:

- sinh khóa
- serialize/deserialize public key
- derive AES key
- AES encrypt/decrypt

## Thành phần frontend

### 1. Form kết nối

- Nhập tên hiển thị
- Bấm kết nối
- Khóa form sau khi vào phiên

### 2. Chat view

- Hiển thị lịch sử tin nhắn trong phiên hiện tại
- Tin nhắn mới tự cuộn xuống cuối

### 3. Security log view

- Hiển thị các bước kỹ thuật theo thời gian
- Có thể nhóm theo mức `info`, `success`, `error`

### 4. Online users view

- Cập nhật realtime khi có người vào/ra

## Mô hình dữ liệu tối thiểu

### Message

```json
{
  "sender": "An",
  "ciphertext": "...",
  "plaintext": "Xin chao",
  "timestamp": "2026-06-09T13:30:00"
}
```

Lưu ý:

- `plaintext` không nhất thiết gửi thẳng trên wire
- giao diện có thể chỉ hiển thị plaintext sau khi giải mã thành công

### Client session

```json
{
  "client_id": "...",
  "display_name": "An",
  "handshake_ready": true,
  "algorithm": "AES-RSA | DH-AES"
}
```

## Xử lý lỗi

Các trường hợp cần xử lý rõ trên giao diện:

- Chưa nhập tên nhưng bấm kết nối
- Gửi tin nhắn rỗng
- Server chưa chạy hoặc mất kết nối
- Handshake thất bại
- Mã hóa hoặc giải mã thất bại

Nguyên tắc:

- Báo lỗi thân thiện cho người dùng
- Không để exception thô lộ ra giao diện
- Nếu session crypto lỗi, yêu cầu kết nối lại thay vì cố phục hồi

## Kiểm thử chấp nhận

### UI-AES-RSA

- Mở server thành công từ folder `UI-AES-RSA`
- Mở ít nhất 2 tab/cửa sổ trình duyệt
- Hai client nhập tên khác nhau và kết nối thành công
- Log hiển thị đầy đủ bước nhận `RSA public key`, gửi `AES session key`, hoàn tất handshake
- Gửi tin nhắn qua lại thành công
- Một client thoát không làm gián đoạn client còn lại

### UI-DH-AES

- Mở server thành công từ folder `UI-DH-AES`
- Mở ít nhất 2 tab/cửa sổ trình duyệt
- Hai client kết nối và hoàn tất trao đổi `Diffie-Hellman`
- Log hiển thị bước tạo `shared secret` và `AES key`
- Gửi tin nhắn qua lại thành công
- Một client thoát không làm sập server

## Những gì không làm

- Không dùng chung backend giữa hai folder
- Không sửa bài gốc để nhúng UI vào
- Không thêm tài khoản, cơ sở dữ liệu, chat room riêng, upload file
- Không tối ưu thành production-grade secure messaging

## Kết quả mong đợi

Sau khi hoàn thành, repo sẽ có hai bài điểm cộng độc lập:

- `lab04/UI-AES-RSA`: demo secure chat web theo cơ chế AES-RSA qua server
- `lab04/UI-DH-AES`: demo secure chat web theo cơ chế Diffie-Hellman + AES qua server

Hai bài này ưu tiên:

- Dễ chạy
- Dễ trình bày
- Đúng tinh thần đề bài
- Giữ nguyên bài gốc
