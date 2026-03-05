# YouTube Video Summary Generator (AI Chrome Extension)

A premium, AI-powered Chrome Extension that generates intelligent summaries of YouTube videos in seconds. Built with a **FastAPI** backend using **LangChain**, **RAG**, and **Google's Free Gemini API**.

---

## 🚀 Features

- **Instant Summaries**: Get a structured, comprehensive summary of any YouTube video.
- **AI-Powered (RAG)**: Uses Retrieval-Augmented Generation for more accurate and context-aware summaries.
- **Premium UI**: A sleek, dark-mode Chrome Extension interface.
- **Fast & Lightweight**: Minimal overhead with a fast response time using `gemini-1.5-flash`.

---

## 🛠️ Tech Stack

- **Extension**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla ES6).
- **Backend**: FastAPI (Python).
- **AI/LLM**: LangChain, Google Gemini API, FAISS (Vector DB).
- **Transcript**: `youtube-transcript-api`.

---

## ⚙️ Installation & Setup

### 1. Backend Setup (FastAPI)

1. Navigate to the `backend` directory.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend` folder and add your Google Gemini API Key:
   ```env
   GOOGLE_API_KEY="your_actual_api_key_here"
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be running at `http://127.0.0.1:8000`.

### 2. Extension Installation (Chrome)

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** (top right corner).
4. Click **Load unpacked**.
5. Select the `frontend` folder from this repository.
6. The "AI Summarizer" icon should appear in your extensions list.

---

## 📖 Usage

1. Open any YouTube video you want to summarize.
2. Click the **AI Summarizer** extension icon.
3. Click the **Summarize Video** button.
4. Wait a few seconds for the AI to process the transcript and generate your summary!

---

## 🔒 Privacy & Safety

- Your API key is stored locally in your `.env` file and is never committed to version control.
- Transcripts are processed locally on your backend server.

---

## 🤝 Contributing

Feel free to fork this project and submit PRs for any improvements!

---

## 📄 License

MIT License.
