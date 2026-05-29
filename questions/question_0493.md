# Question #493 - Topic 1

A company wants to use artificial intelligence (AI) to determine the quality of its customer service calls. The company currently manages calls in four different languages, including English. The company will offer new languages in the future. The company does not have the resources to regularly maintain machine learning (ML) models. The company needs to create written sentiment analysis reports from the customer service call recordings. The customer service call recording text must be translated into English. Which combination of steps will meet these requirements? (Choose three.)

## Options

**A.** Use Amazon Comprehend to translate the audio recordings into English.

**B.** Use Amazon Lex to create the written sentiment analysis reports.

**C.** Use Amazon Polly to convert the audio recordings into text.

**D.** Use Amazon Transcribe to convert the audio recordings in any language into text.

**E.** Use Amazon Translate to translate text in any language to English. F. Use Amazon Comprehend to create the sentiment analysis reports.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Xác định chất lượng cuộc gọi CS bằng AI. 4 languages (+future). Không có resources maintain ML models. Cần sentiment analysis reports từ recordings. Text phải được translate sang English.
- **Existing Resources:** Customer service call recordings.
- **Current Issue/Goal:** Pipeline: audio → text → translate to English → sentiment analysis.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `convert the audio recordings into text` | Amazon Transcribe (speech-to-text). |
| `translate` | Amazon Translate (text-to-text translation). |
| `sentiment analysis` | Amazon Comprehend (NLP, sentiment detection). |
| `choose three` | 3 đáp án đúng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** AI/ML service selection (choose 3)
- **Constraints:** Multiple languages, serverless (no ML maintenance).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D, E, F**

**Giải thích:**
- **D. Amazon Transcribe:** Speech-to-text, support multiple languages. Chuyển audio recordings thành text.
- **E. Amazon Translate:** Translate text từ bất kỳ ngôn ngữ nào sang English.
- **F. Amazon Comprehend:** NLP service, tạo sentiment analysis reports từ text.

Pipeline: Audio recordings → Transcribe → text → Translate → English text → Comprehend → sentiment reports.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Amazon Comprehend** không làm translation. Comprehend là NLP service (sentiment, entities, key phrases), không phải translation.

**❌ Đáp án B:**
- **Amazon Lex** là conversational AI (chatbots), không phải sentiment analysis tool.

**❌ Đáp án C:**
- **Amazon Polly** là text-to-speech (ngược chiều). Cần speech-to-text là Transcribe.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Audio → Transcribe (text). Translate (English). Comprehend (sentiment). Polly = TTS, Lex = chatbot."*
