import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Langchain and Gemini imports
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

load_dotenv()  # Load API keys from .env

app = FastAPI(title="YouTube Video Summary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    """Extracts the 11-character YouTube video ID from various URL formats."""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_transcript_text(video_id: str) -> str:
    """Helper to fetch and concatenate transcript from YouTube."""
    try:
        api = YouTubeTranscriptApi()
        # The list method gives access to available transcripts, and fetch() retrieves it.
        # Alternatively, api.fetch(video_id) defaults to 'en' but it's more robust to grab available english first.
        transcript_list = api.list(video_id)
        # Find transcript prioritizing english, or auto fallback
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()
        
        return " ".join([segment.text for segment in transcript_data])
    except Exception as e:
        # For simplicity, catch all and return 500 or 404
        raise HTTPException(status_code=404, detail=f"Error fetching transcript: {str(e)}")

@app.post("/api/transcript")
async def get_transcript(request: VideoRequest):
    """Endpoint simply to fetch the transcript."""
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
        
    full_transcript = fetch_transcript_text(video_id)
    return {
        "video_id": video_id,
        "transcript": full_transcript
    }

@app.post("/api/summarize")
async def summarize_video(request: VideoRequest):
    """Endpoint that fetches transcript and uses LangChain + RAG + Gemini to summarize."""
    # 1. Check API Key
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Google API Key is not configured in backend.")

    # 2. Extract Video ID and Fetch Transcript
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
    
    transcript_text = fetch_transcript_text(video_id)
    
    # 3. LangChain RAG Setup
    try:
        # Step A: Chunk the transcript
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        docs = text_splitter.create_documents([transcript_text])

        # Step B: Create Embeddings and Vector Store (FAISS)
        # We use Google's embedding model
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever()

        # Step C: Setup the LLM (Gemini)
        # Using gemini-1.5-flash which is free and fast, suitable for text summarization
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

        # Step D: Create Prompt Template
        system_prompt = (
            "You are an expert assistant who summarizes YouTube videos based on their transcripts. "
            "Use the following pieces of retrieved context to generate a comprehensive, structured summary. "
            "Include key takeaways, main topics discussed, and a brief overview. "
            "If the context is empty or doesn't make sense, just state that you cannot summarize it. "
            "\n\n"
            "{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Step E: Construct the Chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # Step F: Run the Chain
        # The 'input' here is basically a command, while the actual transcript is retrieved as context
        response = rag_chain.invoke({"input": "Please provide a detailed summary of this video transcript."})
        
        return {
            "video_id": video_id,
            "summary": response["answer"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "YouTube Video Summary and RAG API is running."}
