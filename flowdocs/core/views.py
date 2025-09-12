# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
import traceback

from .forms import UploadForm, FolderForm
from .models import PDFFile, Folder
from .utils import extract_text_from_pdf, extract_keywords, generate_gpt4_answer
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # consistent language detection

CACHE_TTL = getattr(settings, "CACHE_TTL", 120)  # seconds
MAX_CACHE_QUERIES = 10  # keep last 10 queries per user


# ---------------- Language Detection ----------------
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


# ---------------- Authentication -------------------
def logout_view(request):
    logout(request)
    return redirect('login')
#===========================Registration view====================
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

#===========================Login view==========================
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url or 'dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    # GET request: show login page even if already logged in
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})



# ---------------- Dashboard ------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .forms import UploadForm
from .models import PDFFile, Folder
from .utils import extract_text_from_pdf, extract_keywords
from .vectorstore import pdf_collection
import uuid

@login_required(login_url='login') 
def dashboard(request, folder_id=None, subfolder_id=None):
    role = getattr(request.user, 'role', 'user')

    # ---------------- Upload PDFs to a subcategory ----------------
    if subfolder_id:
        subcategory = get_object_or_404(Folder, id=subfolder_id)
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                pdf = form.save(commit=False)
                pdf.folder = subcategory
                pdf.uploaded_by = request.user

                # Extract text & keywords once
                try:
                    pdf_text = extract_text_from_pdf(pdf.file.path)
                    pdf.text_content = pdf_text
                    pdf.keywords = extract_keywords(pdf_text, max_keywords=15)

                    # ---------------- Store embeddings in ChromaDB ----------------
                    # Split text into chunks (~500 chars each)
                    chunks = [pdf_text[i:i+500] for i in range(0, len(pdf_text), 500)]
                    for chunk in chunks:
                        pdf_collection.add(
                            documents=[chunk],
                            metadatas=[{
                                "pdf_id": str(pdf.id),
                                "title": pdf.title,
                                "folder": pdf.folder.name if pdf.folder else "Uncategorized",
                                "user_id": str(request.user.id)
                            }],
                            ids=[str(uuid.uuid4())]
                        )

                except Exception as e:
                    print(f"[WARN] PDF parsing failed: {e}")
                    pdf.text_content = ""
                    pdf.keywords = []

                pdf.save()
                messages.success(request, f"PDF '{pdf.title}' uploaded successfully!")
                return redirect('dashboard', subfolder_id=subcategory.id)
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = UploadForm()

        pdfs = PDFFile.objects.filter(folder=subcategory).order_by('-uploaded_at')
        return render(request, "dashboard_pdfs.html", {
            "subcategory": subcategory,
            "pdfs": pdfs,
            "form": form,
            "role": role,
        })

    # ---------------- Show subfolders under a category ----------------
    if folder_id:
        category = get_object_or_404(Folder, id=folder_id)
        subfolders = Folder.objects.filter(parent=category)\
                                   .annotate(pdf_count=Count('files'))\
                                   .order_by('name')
        return render(request, "dashboard_subcategories.html", {
            "category": category,
            "subfolders": subfolders,
            "role": role,
        })

    # ---------------- Show top-level categories ----------------
    categories = Folder.objects.filter(parent=None)\
                               .annotate(subcategory_count=Count('subfolders'))\
                               .order_by('name')
    return render(request, "dashboard.html", {
        "folders": categories,
        "role": role,
    })



# ---------------- Create Folder / Subcategory ----------------
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Folder

@login_required
def create_folder(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name", "").strip()
        subcategory_name = request.POST.get("subcategory_name", "").strip()

        if not category_name or not subcategory_name:
            messages.error(request, "Both Category and Subcategory names are required.")
            return redirect("dashboard")

        # Create or get category (root folder)
        try:
            category, created = Folder.objects.get_or_create(
                name=category_name,
                parent=None,
                defaults={'created_by': request.user}
            )
        except IntegrityError:
            category = Folder.objects.filter(name=category_name, parent=None).first()
            if category:
                messages.warning(request, f"Category '{category_name}' already exists.")
            else:
                messages.error(request, f"Category '{category_name}' could not be created.")
                return redirect("dashboard")

        # Create or get subcategory (child folder)
        try:
            subcategory, created = Folder.objects.get_or_create(
                name=subcategory_name,
                parent=category,
                defaults={'created_by': request.user}
            )
        except IntegrityError:
            subcategory = Folder.objects.filter(name=subcategory_name, parent=category).first()
            if subcategory:
                messages.warning(request, f"Subcategory '{subcategory_name}' already exists under '{category.name}'.")
            else:
                messages.error(request, f"Subcategory '{subcategory_name}' could not be created.")
                return redirect("dashboard")

        messages.success(request, f"Category '{category.name}' and Subcategory '{subcategory.name}' processed successfully.")

    return redirect("dashboard")



# ---------------- Delete PDF / Folder ----------------
@login_required
def delete_pdf(request, file_id):
    pdf = get_object_or_404(PDFFile, pk=file_id)
    try:
        if pdf.file:
            pdf.file.delete(save=False)
        pdf.delete()
        messages.success(request, "PDF deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting PDF: {e}")
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Folder, PDFFile  # assuming you also have a File model

@login_required
def delete_folder(request, folder_id):
    # Only admin or superadmin can delete
    if request.user.role not in ["admin", "superadmin"]:
        messages.error(request, "You don't have permission to delete categories.")
        return redirect("dashboard")

    folder = get_object_or_404(Folder, id=folder_id)

    # Optional: delete all files linked to this folder (if required)
    PDFFile.objects.filter(folder=folder).delete()

    # If files are stored in GCS or local storage, add cleanup logic here
    # Example for GCS/local: delete files from bucket before removing DB entry

    folder_name = folder.name  # save before deleting
    folder.delete()

    messages.success(request, f"Category '{folder_name}' deleted successfully!")
    return redirect("dashboard")



# ---------------- Add Subcategory ----------------
@login_required
def add_subcategory(request):
    if request.method == "POST":
        parent_id = request.POST.get("parent_id")
        sub_name = request.POST.get("subcategory_name", "").strip()

        if parent_id and sub_name:
            parent = get_object_or_404(Folder, id=parent_id)
            subcategory, created = Folder.objects.get_or_create(
                name=sub_name,
                parent=parent,
                defaults={'created_by': request.user}
            )
            if created:
                messages.success(request, f"Subcategory '{sub_name}' added under '{parent.name}'.")
            else:
                messages.info(request, f"Subcategory '{sub_name}' already exists under '{parent.name}'.")
        else:
            messages.error(request, "Subcategory name is required.")

    return redirect('dashboard')


# ---------------- Home View ----------------
def home_view(request):
    return render(request, 'home.html')


# ---------------- Search Query ----------------
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
import traceback
from rapidfuzz import fuzz

from .models import PDFFile, Folder
from .utils import extract_keywords, generate_gpt4_answer, detect_language

CACHE_TTL = 3600  # 1 hour
MAX_SNIPPET_LENGTH = 1500  # max chars per PDF snippet
CATEGORY_MATCH_THRESHOLD = 70
SUBCATEGORY_MATCH_THRESHOLD = 70
PDF_MATCH_THRESHOLD = 50  # Minimum match ratio to consider PDF relevant


def truncate_snippet(text: str, max_len=MAX_SNIPPET_LENGTH) -> str:
    snippet = text[:max_len]
    if len(text) > max_len:
        last_dot = snippet.rfind(".")
        if last_dot != -1:
            snippet = snippet[:last_dot + 1]
    return snippet

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
import traceback
from rapidfuzz import fuzz

from .models import PDFFile, Folder
from .utils import extract_keywords, generate_gpt4_answer, detect_language

CACHE_TTL = 3600  # 1 hour
MAX_SNIPPET_LENGTH = 1500  # max chars per PDF snippet
CATEGORY_MATCH_THRESHOLD = 70
SUBCATEGORY_MATCH_THRESHOLD = 70
#PDF_MATCH_THRESHOLD = 10  # Minimum match ratio to consider PDF relevant


def truncate_snippet(text: str, max_len=MAX_SNIPPET_LENGTH) -> str:
    snippet = text[:max_len]
    if len(text) > max_len:
        last_dot = snippet.rfind(".")
        if last_dot != -1:
            snippet = snippet[:last_dot + 1]
    return snippet

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
from langdetect import detect, DetectorFactory
import traceback
from rapidfuzz import fuzz

from .models import PDFFile, Folder
from .utils import extract_keywords, generate_gpt4_answer,search_pdfs
from .vectorstore import pdf_collection

DetectorFactory.seed = 0  # consistent language detection

CACHE_TTL = 3600  # 1 hour
MAX_SNIPPET_LENGTH = 1500  # max chars per PDF snippet
CATEGORY_MATCH_THRESHOLD = 70
SUBCATEGORY_MATCH_THRESHOLD = 70
PDF_MATCH_THRESHOLD = 50  # Minimum match ratio to consider PDF relevant


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


def truncate_snippet(text: str, max_len=MAX_SNIPPET_LENGTH) -> str:
    snippet = text[:max_len]
    if len(text) > max_len:
        last_dot = snippet.rfind(".")
        if last_dot != -1:
            snippet = snippet[:last_dot + 1]
    return snippet



def search_query(request):
    if request.method == "GET":
        categories = Folder.objects.filter(parent__isnull=True).order_by("name")
        category_names = ", ".join([cat.name for cat in categories])
        welcome_message = (
            f"👋 Hello! I am your AI assistant. I can help you by answering your questions. "
           
        )
        return render(request, "search.html", {"welcome_message": welcome_message})

    elif request.method == "POST":
        try:
            query = request.POST.get("query", "").strip()
            if not query:
                return JsonResponse({"error": "Query cannot be empty"}, status=400)

            # ---------------- Caching ----------------
            user_id = getattr(request.user, "id", "public")
            cached_key = f"user_{user_id}_query_{hash(query)}"
            cached_result = cache.get(cached_key)
            if cached_result:
                return JsonResponse(cached_result)

            # ---------------- Language Detection ----------------
            lang = detect_language(query)
            language_instruction = "Answer in Marathi." if lang == "mr" else "Answer in English."

            session = request.session
            last_category_id = session.get("last_selected_category")
            last_subcategory_id = session.get("last_selected_subcategory")

            categories = Folder.objects.filter(parent__isnull=True)
            result = {}
            matched_pdfs = []

            # ---------------- Step 1: Previous category/subcategory ----------------
            if last_category_id:
                last_category = Folder.objects.filter(id=last_category_id).first()
                subcategories = last_category.subfolders.all() if last_category else []
                subcategory_matched = None

                for subcat in subcategories:
                    score = fuzz.partial_ratio(query.lower(), subcat.name.lower())
                    if score >= SUBCATEGORY_MATCH_THRESHOLD:
                        subcategory_matched = subcat
                        break

                if subcategory_matched:
                    pdfs = PDFFile.objects.filter(folder=subcategory_matched).order_by("-uploaded_at")
                    context, matched_pdfs = search_pdfs(query, pdfs)

                    prompt = (
                        f"Category: {last_category.name}\n"
                        f"Subcategory: {subcategory_matched.name}\n"
                        f"User Question: {query}\n\n"
                        f"Context: {context}\n\n"
                        f"{language_instruction}"
                    )

                    answer = generate_gpt4_answer(user_question=query, context=prompt, references=matched_pdfs)
                    result = {"answer": answer, "references": matched_pdfs}

                    session["last_selected_subcategory"] = subcategory_matched.id
                    cache.set(cached_key, result, timeout=CACHE_TTL)
                    return JsonResponse(result)

            # ---------------- Step 2: Check category match ----------------
            matched_category = None
            for cat in categories:
                score = fuzz.partial_ratio(query.lower(), cat.name.lower())
                if score >= CATEGORY_MATCH_THRESHOLD:
                    matched_category = cat
                    break

            if matched_category:
                subcats = matched_category.subfolders.all()
                subcat_list = ", ".join([sub.name for sub in subcats])
                answer_prefix = (
                    f"Got it! You asked about '{matched_category.name}'. This is large topic can you provide further relevence i.e. related to {subcat_list}\n\n"
                    if subcats.exists()
                    else f"Got it! You asked about '{matched_category.name}', but it has no relevence.\n\n"
                )

                result = {"answer": answer_prefix, "references": []}
                session["last_selected_category"] = matched_category.id
                session["last_selected_subcategory"] = None
                cache.set(cached_key, result, timeout=CACHE_TTL)
                return JsonResponse(result)

            # ---------------- Step 3: General GPT fallback ----------------
            pdfs = PDFFile.objects.all()  # Optionally, limit scope if needed
            context, matched_pdfs = search_pdfs(query, pdfs)
           
            prompt = f"{context}\n\n{language_instruction}" if context else language_instruction
            answer = generate_gpt4_answer(user_question=query, context=prompt, references=matched_pdfs)

            result = {"answer": answer, "references": matched_pdfs}
            session["last_selected_category"] = None
            session["last_selected_subcategory"] = None
            cache.set(cached_key, result, timeout=CACHE_TTL)
            return JsonResponse(result)

        except Exception:
            traceback.print_exc()
            return JsonResponse(
                {"answer": "⚠️ Something went wrong. Please try again later.", "references": []},
                status=500,
            )

    return HttpResponseBadRequest("Invalid request")




#===========================user list=================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import CustomUser

@login_required
def user_list_view(request):
    # Fetch all users
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})


#============================================ activate deactivate users ====================================


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser

@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active  # toggle active/inactive
    user.save()
    messages.success(request, f"{user.username} status updated successfully.")
    return redirect('user_list')


#=============================delete user======================
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@login_required
def delete_user(request, user_id):
    current_user = request.user
    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    # Only superadmins can delete other users
    if current_user.role != 'superadmin':
        messages.error(request, "You do not have permission to delete users.")
        return redirect('user_list')

    # Prevent superadmin from deleting themselves
    if user_to_delete == current_user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')

    user_to_delete.delete()
    messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
    return redirect('user_list')
