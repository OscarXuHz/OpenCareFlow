# Home-Visit Mock Samples

用於 `POST /api/home-visit/sessions/mock-demo` 的離線示範。

> 這個資料夾只可包含明確標示的合成資料。內容不對應任何真實人物、
> 電話、地址、個案或機構；請勿把真實服務使用者資料提交到 Git。

- `mock_template.docx` — 使用合成資料的家訪紀錄模板
- `mock_visit.mp3` — 靜音 MP3 placeholder；mock 模式下不會被解碼，
  ASR 直接落回 `tests/visit_note/transcript_example.txt` 的廣東話樣本。
- `mock_transcript.txt` — 與 transcriber fallback 同步的逐字稿（離線備援）。
