import os
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

# ---------------- PDF Text Extraction ----------------
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    Falls back to EasyOCR if no text is found.
    """
    if not os.path.exists(file_path):
        print(f"[❌] File not found: {file_path}")
        return ""

    text = ""
    try:
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

    print(f"[✅] Final extracted text length: {len(text)} chars")
    return text.strip()

# ---------------- Keyword Extraction ----------------
def extract_keywords(text: str) -> list:
    """
    Extract all possible keywords using YAKE.
    """
    if not text.strip():
        return []

    try:
        lang_code = detect(text)
        if lang_code not in ['en', 'mr']:
            lang_code = 'en'
    except LangDetectException:
        lang_code = 'en'

    try:
        kw_extractor = yake.KeywordExtractor(lan=lang_code, n=2, top=100000)
        keywords_with_scores = kw_extractor.extract_keywords(text)
        keywords = list(set([kw.lower() for kw, _ in keywords_with_scores]))
        return keywords
    except Exception as e:
        print(f"[❌] Keyword extraction failed: {e}")
        return []

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
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content.strip()
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
