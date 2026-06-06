# Question #485 - Topic 1

A company is looking for a solution that can store video archives in AWS from old news footage. The company needs to minimize costs and will rarely need to restore these files. When the files are needed, they must be available in a maximum of five minutes. What is the MOST cost-effective solution?

## Options

**A.** Store the video archives in Amazon S3 Glacier and use Expedited retrievals.

**B.** Store the video archives in Amazon S3 Glacier and use Standard retrievals.

**C.** Store the video archives in Amazon S3 Standard-Infrequent Access (S3 Standard-IA).

**D.** Store the video archives in Amazon S3 One Zone-Infrequent Access (S3 One Zone-IA).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lưu trữ video archives (old news footage). Hiếm khi restore, nhưng khi cần thì phải available trong tối đa 5 phút. Cần minimize costs.
- **Existing Resources:** Video archives data.
- **Current Issue/Goal:** Chọn storage class rẻ nhất mà đáp ứng retrieval time ≤5 phút.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `rarely need to restore` | Chi phí lưu trữ là quan trọng nhất. Retrieval cost không đáng kể vì hiếm khi dùng. |
| `available in a maximum of five minutes` | Glacier Expedited: 1-5 phút. Glacier Standard: 3-5 giờ (quá chậm). |
| `most cost-effective` | Glacier có storage cost thấp nhất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective storage class
- **Constraints:** Max 5 phút retrieval time, rare access.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Glacier** có storage cost thấp nhất trong các đáp án.
- **Expedited retrieval:** 1-5 phút, đáp ứng yêu cầu "available in a maximum of five minutes".
- Vì hiếm khi restore, chi phí Expedited retrieval (cao hơn Standard retrieval) không đáng kể so với savings từ storage cost thấp.
- Standard-IA và One Zone-IA có storage cost cao hơn Glacier.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Glacier Standard retrieval: 3-5 giờ → không đáp ứng yêu cầu 5 phút.

**❌ Đáp án C:**
- **S3 Standard-IA:** Storage cost cao hơn Glacier. Phù hợp cho data ít truy cập nhưng cần truy xuất nhanh (milliseconds), không phải archive.

**❌ Đáp án D:**
- **S3 One Zone-IA:** Storage cost thấp hơn Standard-IA nhưng vẫn cao hơn Glacier. Rủi ro mất data nếu AZ bị lỗi. Không tối ưu cho archive.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Archive + hiếm truy cập + 5 phút → Glacier Expedited. Standard-IA = hay dùng nhưng rẻ hơn Standard. Glacier = rẻ nhất."*
