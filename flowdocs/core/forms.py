from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import PDFFile, CustomUser, Folder

# ---------------- Upload Form ----------------
class UploadForm(forms.ModelForm):
    """
    Form to upload PDFs. Folder is assigned automatically in the view.
    """
    class Meta:
        model = PDFFile
        fields = ['title', 'file']  # only title and file
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PDF Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ---------------- Folder Form ----------------
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']   # ✅ only keep name field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter folder name'}),
        }

# ---------------- User Register Form ----------------
DEPARTMENT_CHOICES = [
    ('finance', 'Finance'),
    ('admin', 'Admin'),
    ('operations', 'Operations'),
    ('hr', 'HR'),
    # Add more departments as needed
]

class UserRegisterForm(UserCreationForm):
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'department', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter username', 'autofocus': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter email'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter password', 'id': 'id_password1'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control', 'placeholder': 'Confirm password', 'id': 'id_password2'
            }),
        }
