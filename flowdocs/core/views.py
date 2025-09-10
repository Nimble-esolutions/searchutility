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
from .utils import extract_text_from_pdf, extract_keywords, generate_gpt4_answer,extract_text_from_image
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
@login_required(login_url='login') 
def dashboard(request, folder_id=None, subfolder_id=None):
    role = getattr(request.user, 'role', 'user')

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

    categories = Folder.objects.filter(parent=None)\
                               .annotate(subcategory_count=Count('subfolders'))\
                               .order_by('name')
    return render(request, "dashboard.html", {
        "folders": categories,
        "role": role,
    })


# ---------------- Create Folder / Subcategory ----------------
@login_required
def create_folder(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name", "").strip()
        subcategory_name = request.POST.get("subcategory_name", "").strip()

        if category_name and subcategory_name:
            category, _ = Folder.objects.get_or_create(
                name=category_name,
                parent=None,
                defaults={'created_by': request.user}
            )
            subcategory, _ = Folder.objects.get_or_create(
                name=subcategory_name,
                parent=category,
                defaults={'created_by': request.user}
            )
            messages.success(request, f"Category '{category_name}' and Subcategory '{subcategory_name}' created successfully.")
        else:
            messages.error(request, "Both Category and Subcategory names are required.")

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


@login_required
def delete_folder(request, folder_id):
    if request.user.role not in ["admin", "superadmin"]:
        messages.error(request, "You don't have permission to delete categories.")
        return redirect("dashboard")

    folder = get_object_or_404(Folder, id=folder_id)
    folder.delete()
    messages.success(request, f"Category '{folder.name}' deleted successfully!")
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
from rapidfuzz import fuzz

CACHE_TTL = 3600  # 1 hour
MAX_CACHE_QUERIES = 10
MAX_SNIPPET_LENGTH = 1500  # max chars per PDF snippet


def search_query(request):
    if request.method == "GET":
        # Show welcome message with categories/subcategories for authenticated users
        categories = Folder.objects.filter(parent__isnull=True).order_by("name")
        welcome_message = "👋 Hello! I am your AI assistant.\n\nYou can:\n💬 Chat generally OR\n❓ Ask questions by categories:\n"
        for cat in categories:
            welcome_message += f"📂 {cat.name}\n"
            for sub in cat.subfolders.all():
                welcome_message += f"   └── 📁 {sub.name}\n"
        return render(request, "search.html", {"welcome_message": welcome_message})

    elif request.method == "POST":
        try:
            query = request.POST.get("query", "").strip()
            if not query:
                print("⚠️ Empty query received")
                return JsonResponse({"error": "Query cannot be empty"}, status=400)

            # ✅ Extract query keywords (all possible, not limited)
            query_keywords = extract_keywords(query)
            print(f"🔎 Query keywords: {query_keywords}")

            # Prepare cache
            user_id = getattr(request.user, "id", "public")
            user_cache_list_key = f"user_{user_id}_cached_queries"
            cached_key = f"user_{user_id}_query_{hash(query)}"
            cached_result = cache.get(cached_key)
            if cached_result:
                print(f"✅ Cache hit for {cached_key}")
                return JsonResponse(cached_result)
            else:
                print(f"🆕 Cache miss for {cached_key}")

            # Detect language
            lang = detect_language(query)
            print(f"🌐 Detected query language: {lang}")
            language_instruction = "Answer in Marathi." if lang == "mr" else "Answer in English."

            # Search PDFs - include both main folders and subfolders
            pdfs = PDFFile.objects.filter(folder__isnull=False).order_by("-uploaded_at")
            print(f"📂 Total PDFs to scan: {pdfs.count()}")

            matched_pdfs, relevant_context = [], ""

            for pdf in pdfs:
                try:
                    print(f"➡️ Checking PDF: {pdf.title}")

                    # Use stored text content if available, otherwise extract from file
                    pdf_text = pdf.text_content or ""
                    if not pdf_text.strip():
                        print(f"📄 No stored text, extracting from file: {pdf.title}")
                        pdf_text = extract_text_from_pdf(pdf.file.path) or ""
                        if not pdf_text.strip():
                            print(f"🖼️ No text found in {pdf.title}, trying OCR...")
                            pdf_text = extract_text_from_image(pdf.file.path) or ""
                        
                        # Save extracted text for future use
                        if pdf_text.strip():
                            pdf.text_content = pdf_text
                            pdf.save()

                    if not pdf_text:
                        print(f"⚠️ Still no text from {pdf.title}")
                        continue

                    # ✅ Ensure keywords are extracted and saved
                    if not pdf.keywords:
                        print(f"🔑 Extracting keywords for {pdf.title}")
                        pdf.keywords = extract_keywords(pdf_text)
                        pdf.save()
                    else:
                        print(f"🔑 Using existing keywords for {pdf.title}")

                    pdf_keywords = pdf.keywords if pdf.keywords else []
                    print(f"📌 Keywords for {pdf.title}: {pdf_keywords}")

                    # --- Matching Logic ---
                    overlap = set(query_keywords).intersection(set(pdf_keywords))
                    fuzzy_match = any(
                        fuzz.partial_ratio(qk.lower(), pk.lower()) > 75
                        for qk in query_keywords for pk in pdf_keywords
                    )

                    if overlap or fuzzy_match:
                        print(f"✅ Match found in {pdf.title}")
                        snippet = pdf_text[:MAX_SNIPPET_LENGTH]
                        relevant_context += f"\n\n[From file: {pdf.title}]\n{snippet}"
                        matched_pdfs.append(
                            {
                                "title": pdf.title,
                                "uploaded_at": pdf.uploaded_at.strftime("%Y-%m-%d"),
                                "folder": pdf.folder.name if pdf.folder else "Uncategorized",
                                "url": pdf.file.url,
                            }
                        )
                    else:
                        print(f"❌ No keyword match in {pdf.title}")

                except Exception as e:
                    print(f"[WARN] Failed to process PDF {pdf.title}: {e}")

            # GPT answer
            if matched_pdfs:
                print(f"🤖 Sending {len(matched_pdfs)} PDFs context to GPT")
                prompt = f"User Question: {query}\n\nContext from PDFs:{relevant_context}\n\n{language_instruction}"
                answer = generate_gpt4_answer(user_question=query, context=prompt)
                result = {"answer": answer, "references": matched_pdfs}
            else:
                print("🤖 No PDF matches, sending query alone to GPT")
                answer = generate_gpt4_answer(user_question=query, context=language_instruction)
                result = {"answer": answer, "references": []}

            # Cache result
            cache.set(cached_key, result, timeout=CACHE_TTL)
            user_queries = cache.get(user_cache_list_key, [])
            user_queries.append(cached_key)
            if len(user_queries) > MAX_CACHE_QUERIES:
                oldest_key = user_queries.pop(0)
                cache.delete(oldest_key)
            cache.set(user_cache_list_key, user_queries, timeout=CACHE_TTL)

            print("💾 Result cached successfully")
            return JsonResponse(result)

        except Exception as e:
            print("[ERROR] search_query exception:", e)
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
