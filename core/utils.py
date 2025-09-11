import os
<<<<<<< HEAD
import fitz  # PyMuPDF
import easyocr
import yake
from openai import OpenAI
from langdetect import detect, DetectorFactory, LangDetectException
from django.conf import settings

# ---------------- Seed for consistent language detection ----------------
DetectorFactory.seed = 0

# ---------------- OpenAI Setup ----------------
client = None
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"[🔑] OpenAI API Key loaded: Yes")
else:
    print("[❌] OpenAI API key not found")

# ---------------- EasyOCR Reader ----------------
# Initialize once (English + Marathi)
easyocr_reader = easyocr.Reader(['en', 'mr'], gpu=False)  # Set gpu=True if GPU is available
=======
import PyPDF2
import yake
from openai import OpenAI
from langdetect import detect, LangDetectException
from PIL import Image
import pytesseract

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
    

>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc

# ---------------- PDF Text Extraction ----------------
def extract_text_from_pdf(file_path: str) -> str:
    """
<<<<<<< HEAD
    Extract text from PDF using PyMuPDF.
    Falls back to EasyOCR if no text is found.
=======
    Extracts text from a PDF file safely.
    Falls back to OCR if the PDF is scanned.
>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc
    """
    if not os.path.exists(file_path):
        print(f"[❌] File not found: {file_path}")
        return ""

    text = ""
    try:
<<<<<<< HEAD
        print(f"[📄] Opening PDF with PyMuPDF: {file_path}")
        doc = fitz.open(file_path)
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text + "\n"
            else:
                print(f"[⚠️] Page {i} has no text, will use OCR later")
        doc.close()
    except Exception as e:
        print(f"[❌] PyMuPDF extraction failed: {e}")
        text = ""

    # If no text extracted → try OCR
    if not text.strip():
        print("[🖼] No text found in PDF, using EasyOCR...")
        try:
            result = easyocr_reader.readtext(file_path, detail=0)
            text = "\n".join(result)
            print(f"[🖼] OCR extracted {len(text)} chars")
        except Exception as e:
            print(f"[❌] EasyOCR failed: {e}")
            text = ""
=======
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
>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc

    print(f"[✅] Final extracted text length: {len(text)} chars")
    return text.strip()

<<<<<<< HEAD
# ---------------- Keyword Extraction ----------------
def extract_keywords(text: str) -> list:
    """
    Extract all possible keywords using YAKE.
    """
    if not text.strip():
=======

# ---------------- OCR from Image ----------------
import pytesseract
from pdf2image import convert_from_path

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

def extract_keywords(text: str) -> list:
    """
    Extracts ALL possible keywords (not limited to top N).
    Uses YAKE for scoring but returns the entire keyword list.
    """
    if not text.strip():
        print("[⚠️] Empty text, no keywords extracted")
>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc
        return []

    try:
        lang_code = detect(text)
<<<<<<< HEAD
        if lang_code not in ['en', 'mr']:
            lang_code = 'en'
    except LangDetectException:
        lang_code = 'en'

    try:
        kw_extractor = yake.KeywordExtractor(lan=lang_code, n=2, top=100000)
        keywords_with_scores = kw_extractor.extract_keywords(text)
        keywords = list(set([kw.lower() for kw, _ in keywords_with_scores]))
        return keywords
=======
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

>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc
    except Exception as e:
        print(f"[❌] Keyword extraction failed: {e}")
        return []

<<<<<<< HEAD
# ---------------- GPT-4 Answer Generation ----------------
def generate_gpt4_answer(user_question: str, context: str, references: list = None) -> str:
    """
    Generate GPT-4 answer using PDF context and optionally append reference files.
    """
    if not client:
        return "OpenAI API key not configured. Set OPENAI_API_KEY to enable AI responses."

    try:
        lang = detect(user_question)
    except LangDetectException:
        lang = "en"

    # Prepare system & user messages
    if lang == "mr":
        system_msg = "तू एक मदत करणारा सहाय्यक आहेस. प्रश्नाचे उत्तर फक्त मराठीत द्या."
        prompt = (
            f"खाली दिलेल्या PDF संदर्भांचा वापर करून प्रश्नाचे उत्तर द्या.\n\n"
            f"प्रश्न: {user_question}\n\n"
            f"संदर्भ:\n{context}"
        )
    else:
        system_msg = "You are a helpful assistant. Answer in English only."
        prompt = (
            f"Using the following PDF references, answer the question in English.\n\n"
            f"Question: {user_question}\n\n"
            f"Reference:\n{context}"
        )

    # Add reference list explicitly to the prompt
    if references:
        ref_list = "\n".join([f"- {ref.get('title')} ({ref.get('url')})" for ref in references if ref.get("title")])
        prompt += f"\n\nAlso, cite these reference files where useful:\n{ref_list}"

    try:
=======


# ---------------- GPT-4 Answer Generation ----------------
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
>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content.strip()
<<<<<<< HEAD
        return answer
    except Exception as e:
        print(f"[❌] OpenAI API Error: {e}")
        return f"[OpenAI Error] {str(e)}"

# ---------------- Language Detection ----------------
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "en"


#==============================search_pdfs=========================
import difflib

# ---------------- Search PDFs ----------------
def search_pdfs(user_query: str, pdf_files: list) -> tuple:
    """
    Search PDFs for matches with user query.
    Returns (matched_context, matched_files_metadata)
    matched_files_metadata: list of dicts with title, folder, url, uploaded_at
    """
    query_keywords = extract_keywords(user_query)
    print(f"[DEBUG] User Query: {user_query}")
    print(f"[DEBUG] Extracted Keywords: {query_keywords}")

    matched_contexts = []
    matched_files_metadata = []

    for pdf in pdf_files:
        pdf_path = pdf.file.path  # assumes model has FileField
        pdf_name = pdf.file.name
        print(f"[DEBUG] Checking PDF: {pdf_name}")

        try:
            pdf_text = extract_text_from_pdf(pdf_path)
        except Exception as e:
            print(f"[❌] Failed to extract {pdf_name}: {e}")
            continue

        if not pdf_text.strip():
            continue

        pdf_text_lower = pdf_text.lower()
        score = 0
        for kw in query_keywords:
            if kw.lower() in pdf_text_lower:
                score += 1

        match_ratio = score / len(query_keywords) if query_keywords else 0
        print(f"[DEBUG] → Match ratio for {pdf_name}: {match_ratio:.2f}")

        if match_ratio >= 0.3:
            snippet = pdf_text[:2000]  # limit context size
            matched_contexts.append(snippet)

            # Add full PDF metadata
            matched_files_metadata.append({
                "title": pdf.title,
                "folder": pdf.folder.name if pdf.folder else None,
                "url": pdf.file.url if pdf.file else None,
                "uploaded_at": pdf.uploaded_at.strftime("%Y-%m-%d") if pdf.uploaded_at else None,
            })

    combined_context = "\n\n".join(matched_contexts) if matched_contexts else ""
    return combined_context, matched_files_metadata
=======
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
>>>>>>> e72d0398de10fdc822853defe165fa8b525fc1fc
