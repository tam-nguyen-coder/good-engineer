# 📚 Hướng dẫn thêm bộ câu hỏi mới

## 🚀 Cách thêm bộ câu hỏi mới

### Bước 1: Tạo file JSON
Tạo file JSON mới trong thư mục này với format như sau:

```json
[
  {
    "id": 1,
    "content": "Nội dung câu hỏi?",
    "answers": [
      { "id": 1, "content": "Đáp án A", "correct": true },
      { "id": 2, "content": "Đáp án B", "correct": false },
      { "id": 3, "content": "Đáp án C", "correct": false },
      { "id": 4, "content": "Đáp án D", "correct": false }
    ]
  }
]
```

### Bước 2: Cập nhật code
Mở file `src/utils/question-pool-loader.ts` và:

1. **Thêm tên file vào mảng `AVAILABLE_QUESTION_POOLS`:**
```typescript
const AVAILABLE_QUESTION_POOLS = [
  'scrum-master-1',
  'demo',
  'ten-file-moi'  // ← Thêm tên file mới vào đây
];
```

2. **Không cần thêm tên hiển thị** - hệ thống sẽ tự động lấy tên file làm tên hiển thị

### Bước 3: Restart server
```bash
npm run dev
```

## 📋 Format câu hỏi

### Câu hỏi đơn (1 đáp án đúng):
```json
{
  "id": 1,
  "content": "Câu hỏi?",
  "answers": [
    { "id": 1, "content": "A", "correct": true },
    { "id": 2, "content": "B", "correct": false },
    { "id": 3, "content": "C", "correct": false },
    { "id": 4, "content": "D", "correct": false }
  ]
}
```

### Câu hỏi nhiều đáp án:
```json
{
  "id": 2,
  "content": "Câu hỏi nhiều đáp án?",
  "answers": [
    { "id": 1, "content": "A", "correct": true },
    { "id": 2, "content": "B", "correct": false },
    { "id": 3, "content": "C", "correct": true },
    { "id": 4, "content": "D", "correct": false }
  ]
}
```

## ✅ Ví dụ hoàn chỉnh

File `toan-hoc.json`:
```json
[
  {
    "id": 1,
    "content": "2 + 2 = ?",
    "answers": [
      { "id": 1, "content": "3", "correct": false },
      { "id": 2, "content": "4", "correct": true },
      { "id": 3, "content": "5", "correct": false },
      { "id": 4, "content": "6", "correct": false }
    ]
  },
  {
    "id": 2,
    "content": "Số nào là số chẵn?",
    "answers": [
      { "id": 1, "content": "1", "correct": false },
      { "id": 2, "content": "2", "correct": true },
      { "id": 3, "content": "3", "correct": false },
      { "id": 4, "content": "5", "correct": false }
    ]
  }
]
```

Sau đó cập nhật `question-pool-loader.ts`:
```typescript
const AVAILABLE_QUESTION_POOLS = [
  'scrum-master-1',
  'demo',
  'toan-hoc'  // ← Thêm vào đây
];
```

**Lưu ý**: Tên hiển thị sẽ tự động lấy từ tên file (ví dụ: `toan-hoc` sẽ hiển thị là `toan-hoc`)

## 🎯 Lưu ý

- Tên file không được có dấu cách, sử dụng dấu gạch ngang `-`
- **ID câu hỏi phải là số (number)**, không phải string
- **ID đáp án phải là số (number)**, không phải string
- **Câu hỏi phải dùng `content`**, không phải `question`
- **Đáp án phải dùng `content`**, không phải `text`
- **Mỗi đáp án phải có `correct: boolean`**, không dùng `correctAnswers` array
- ID câu hỏi phải unique trong toàn bộ file
- ID đáp án phải unique trong mỗi câu hỏi
- Restart server sau khi thêm bộ câu hỏi mới
