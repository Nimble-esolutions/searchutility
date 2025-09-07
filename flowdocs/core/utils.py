import os
import PyPDF2
import yake
from openai import OpenAI
from langdetect import detect, LangDetectException
from PIL import Image
import pytesseract
import time

# OpenTelemetry imports
from .observability import (
    trace_pdf_processing, trace_ocr_operation, trace_ai_operation,
    trace_openai_call, search_metrics
)

# ---------------- API Setup ----------------
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

print(f"[🔑] OpenAI API Key loaded: {'Yes' if OPEN_API_KEY else 'No'}")
if OPEN_API_KEY:
    print(f"[🔑] API Key starts with: {OPEN_API_KEY[:20]}...")
    client = OpenAI(api_key=OPEN_API_KEY)
else:
    print("[❌] OpenAI API key not found in environment variables")
    print(f"[🔑] Available env vars: {[k for k in os.environ.keys() if 'OPENAI' in k.upper()]}")
    print(f"[🔑] All environment variables: {list(os.environ.keys())}")
    # Fallback: try to read from a file if env var is not set
    try:
        with open('/app/.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    OPEN_API_KEY = line.split('=', 1)[1].strip()
                    print(f"[🔑] Fallback: Found API key in file: {OPEN_API_KEY[:20]}...")
                    client = OpenAI(api_key=OPEN_API_KEY)
                    break
    except:
        print("[❌] No fallback API key found")
    
    # Final fallback: no hardcoded API key for security
    if not client:
        print("[🔧] FINAL FALLBACK: No API key available")
        print("[❌] Please set OPENAI_API_KEY environment variable")
    


# ---------------- PDF Text Extraction ----------------
@trace_pdf_processing("extract_text_from_pdf")
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file safely.
    Falls back to OCR if the PDF is scanned.
    """
    if not os.path.exists(file_path):
        print(f"[❌] File not found: {file_path}")
        return ""

    text = ""
    try:
        print(f"[📄] Opening PDF: {file_path}")
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            print(f"[📑] PDF has {len(reader.pages)} pages")

            for i, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    print(f"[🔠] Extracted {len(page_text)} chars from page {i}")
                    text += page_text + "\n"
                else:
                    print(f"[⚠️] No text on page {i}")

        # If no text extracted → try OCR
        if not text.strip():
            print("[🖼] No text found in PDF. Trying OCR...")
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            for i, img in enumerate(images, start=1):
                ocr_text = extract_text_from_image(img)
                print(f"[🖼 OCR] Extracted {len(ocr_text)} chars from page {i}")
                text += ocr_text + "\n"

    except Exception as e:
        print(f"[❌] Failed to read PDF {file_path}: {e}")
        return ""

    print(f"[✅] Final extracted text length: {len(text)} chars")
    return text.strip()


# ---------------- OCR from Image ----------------
import pytesseract
from pdf2image import convert_from_path

@trace_ocr_operation("extract_text_from_image")
def extract_text_from_image(pdf_path):
    print(f"[🖼] Converting PDF to images for OCR: {pdf_path}")
    text = ""

    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images, start=1):
            print(f"[🖼] Running OCR on page {i}")
            # Save image to temporary file for OCR
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                try:
                    page_text = pytesseract.image_to_string(tmp_file.name, lang="mar+eng")
                except Exception as ocr_error:
                    print(f"[⚠️] OCR failed for page {i}: {ocr_error}")
                    page_text = ""
                finally:
                    os.unlink(tmp_file.name)  # Clean up temp file
            print(f"[🖼 OCR] Extracted {len(page_text)} chars from page {i}")
            text += page_text + "\n"
    except Exception as e:
        print(f"[❌] OCR failed for {pdf_path}: {e}")

    print(f"[✅] Final extracted text length: {len(text)} chars")
    return text



# ---------------- Keyword Extraction ----------------
import re
import yake
from langdetect import detect, LangDetectException

@trace_ai_operation("extract_keywords")
def extract_keywords(text: str) -> list:
    """
    Extracts ALL possible keywords (not limited to top N).
    Uses YAKE for scoring but returns the entire keyword list.
    """
    if not text.strip():
        print("[⚠️] Empty text, no keywords extracted")
        return []

    try:
        lang_code = detect(text)
        if lang_code not in ["en", "mr"]:
            lang_code = "en"
        print(f"[🌐] Keyword extraction language: {lang_code}")
    except LangDetectException:
        lang_code = "en"
        print("[⚠️] Language detection failed, defaulting to English")

    try:
        # Instead of limiting with top=max_keywords, pass a very large number
        kw_extractor = yake.KeywordExtractor(lan=lang_code, n=2, top=100000)
        keywords_with_scores = kw_extractor.extract_keywords(text)

        # Take all keywords returned
        keywords = [kw for kw, _ in keywords_with_scores]

        # Ensure lowercase + remove duplicates
        final_keywords = list(set([kw.lower() for kw in keywords]))

        print(f"[🔑] Extracted {len(final_keywords)} keywords")
        return final_keywords

    except Exception as e:
        print(f"[❌] Keyword extraction failed: {e}")
        return []



# ---------------- GPT-4 Answer Generation ----------------
@trace_openai_call
def generate_gpt4_answer(user_question: str, context: str) -> str:
    if not client:
        return "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI-powered responses."
    
    # Debug: Print the actual API key being used
    print(f"[🔍] DEBUG: Using API key: {OPEN_API_KEY[:20]}...{OPEN_API_KEY[-10:] if OPEN_API_KEY else 'None'}")
    print(f"[🔍] DEBUG: Client object: {client}")
    print(f"[🔍] DEBUG: Full API key: {OPEN_API_KEY}")
    
    try:
        try:
            lang = detect(user_question)
        except LangDetectException:
            lang = "en"

        if lang == "mr":
            system_msg = "तू एक मदत करणारा सहाय्यक आहेस. प्रश्नाचे उत्तर फक्त मराठीत द्या."
            prompt = f"खाली दिलेल्या PDF दस्तावेजांचा संदर्भ वापरून प्रश्नाचे उत्तर द्या.\n\nप्रश्न: {user_question}\n\nसंदर्भ:\n{context}"
        else:
            system_msg = "You are a helpful assistant. Answer the question in English only."
            prompt = f"Using the following PDFs, answer the question in English only.\n\nQuestion: {user_question}\n\nReference:\n{context}"

        print(f"[🤖] Sending request to GPT-4.1 with lang={lang}")
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content.strip()
        print(f"[✅] GPT Answer length: {len(answer)} chars")
        return answer

    except Exception as e:
        print(f"[❌] OpenAI Error: {e}")
        return f"[OpenAI Error] {str(e)}"


# ---------------- Language Detection ----------------
def detect_language(text: str) -> str:
    try:
        lang_code = detect(text)
        print(f"[🌐] Detected language: {lang_code}")
        return lang_code
    except:
        print("[⚠️] Language detection failed, defaulting to English")
        return "en"
