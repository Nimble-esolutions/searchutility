import os
import PyPDF2
import yake
from openai import OpenAI
from langdetect import detect, LangDetectException
from PIL import Image
import pytesseract

# ---------------- API Setup ----------------
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)


# ---------------- PDF Text Extraction ----------------
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

def extract_text_from_image(pdf_path):
    print(f"[🖼] Converting PDF to images for OCR: {pdf_path}")
    text = ""

    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images, start=1):
            print(f"[🖼] Running OCR on page {i}")
            page_text = pytesseract.image_to_string(img, lang="mar+eng")  # OCR directly on PIL image
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
def generate_gpt4_answer(user_question: str, context: str) -> str:
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
