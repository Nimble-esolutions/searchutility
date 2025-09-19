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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Folder, PDFFile
from .forms import UploadForm

@login_required(login_url='login')
def dashboard(request, folder_id=None):
    role = getattr(request.user, 'role', 'user')

    # ---------------- If viewing a specific folder (PDFs) ----------------
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id)
        
        # PDF Upload (Admin/Superadmin only)
        if request.method == "POST" and (role in ["admin", "superadmin"]):
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                pdf = form.save(commit=False)
                pdf.folder = folder
                pdf.uploaded_by = request.user
                pdf.save()
                return redirect('dashboard', folder_id=folder.id)
        else:
            form = UploadForm()

        pdfs = PDFFile.objects.filter(folder=folder).order_by('-uploaded_at')
        return render(request, "dashboard_pdfs.html", {
            "folder": folder,
            "pdfs": pdfs,
            "form": form,
            "role": role,
        })

    # ---------------- Show all folders ----------------
    folders = Folder.objects.annotate(pdf_count=Count('files')).order_by('name')

    return render(request, "dashboard.html", {
        "folders": folders,
        "role": role,
    })




from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Folder, PDFFile

# ---------------- Create Folder / Category ----------------
@login_required
def create_folder(request):
    if request.method == "POST":
        folder_name = request.POST.get("folder_name", "").strip()  # match input name

        if not folder_name:
            messages.error(request, "Category name is required.")
            return redirect("dashboard")

        try:
            folder, created = Folder.objects.get_or_create(
                name=folder_name,
                defaults={'created_by': request.user}
            )
            if created:
                messages.success(request, f"Category '{folder.name}' created successfully.")
            else:
                messages.warning(request, f"Category '{folder.name}' already exists.")

        except IntegrityError:
            messages.error(request, f"Category '{folder_name}' could not be created.")

    return redirect("dashboard")


# ---------------- Delete PDF ----------------
@login_required
def delete_pdf(request, file_id):
    pdf = get_object_or_404(PDFFile, pk=file_id)

    # SCGI users can delete only their own uploads; Admin/Superadmin can delete any
    if request.user.role not in ["admin", "superadmin"] and pdf.uploaded_by != request.user:
        messages.error(request, "You don't have permission to delete this PDF.")
        return redirect(request.META.get("HTTP_REFERER", "dashboard"))

    try:
        if pdf.file:
            pdf.file.delete(save=False)  # delete file from storage
        pdf.delete()
        messages.success(request, "PDF deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting PDF: {e}")

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


# ---------------- Delete Folder / Category ----------------
@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)

    # Only admin or superadmin can delete
    if request.user.role not in ["admin", "superadmin"]:
        messages.error(request, "You don't have permission to delete categories.")
        return redirect("dashboard")

    # Delete all files in folder first (DB + storage)
    pdfs = PDFFile.objects.filter(folder=folder)
    for pdf in pdfs:
        if pdf.file:
            pdf.file.delete(save=False)
    pdfs.delete()

    folder_name = folder.name
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
from .utils import generate_gpt4_answer, search_pdfs, transliterate_marathi_to_english

CACHE_TTL = 3600  # 1 hour
CATEGORY_MATCH_THRESHOLD = 75  # fuzzy match % for category detection

def search_query(request):
    if request.method == "GET":
        categories = Folder.objects.all().order_by("name")
        welcome_message = " Namaskar, I am your AI assistant. I can help you by answering your questions."
        return render(request, "search.html", {"welcome_message": welcome_message, "categories": categories})

    elif request.method == "POST":
        try:
            query = request.POST.get("query", "").strip()
            categories = Folder.objects.all().order_by("name")

            # Length check
            if len(query.split()) > 30:
                return JsonResponse({
                    "answer": "--- Your question is too long. Please ask a shorter question with less than 30 words.",
                    "references": [],
                })

            user_id = getattr(request.user, "id", "public")
            cached_key = f"user_{user_id}_query_{hash(query)}"
            cached_result = cache.get(cached_key)
            if cached_result:
                return JsonResponse(cached_result)

            matched_pdfs, answer_text = [], ""
            query_translit = transliterate_marathi_to_english(query)

            # --- Step 0: Check if this is the first user question ---
            is_first_question = not request.session.get("asked_first_question", False)

            # --- Step 1: Decide folder(s) to search ---
            if is_first_question:
                # First question → only search in common
                search_folders = Folder.objects.filter(name__iexact="common")
                
            else:
                # Follow-up → search across all categories
                search_folders = categories

            # --- Step 2: Search PDFs in chosen folder(s) ---
            for folder in search_folders:
                pdfs = PDFFile.objects.filter(folder=folder).order_by("-uploaded_at")
                context, pdf_matches = search_pdfs(query_translit, pdfs, lang_sensitive=True)
                if pdf_matches:
                    matched_pdfs.extend(pdf_matches)
                    prompt = f"User Question: {query}\nContext: {context}"
                    answer_obj = generate_gpt4_answer(query, prompt, matched_pdfs)
                    answer_text = (
                        f"--- Answer from **{folder.name}** folder:\n\n{answer_obj}\n\n--- Hope this helps."
                    )
                    break  # Stop after first matched folder

            # --- Step 3: Handle no matches on first question ---
            if is_first_question and not matched_pdfs:
                category_names = ", ".join([c.name for c in categories])
                answer_text = (
                    f"🤖 Sorry, I could not find a matching answer in the common folder.\n"
                    f"📚 You can explore these categories: {category_names}"
                )

            # --- Step 4: Mark that first question has been asked ---
            request.session["asked_first_question"] = True

            # --- Step 5: Cache & respond ---
            result = {"answer": answer_text, "references": matched_pdfs}
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
