from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import PDFFile, CustomUser, Folder


from django import forms
from .models import PDFFile

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


from django import forms
from .models import Folder

class FolderForm(forms.ModelForm):
    subcategories = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter subcategories, comma separated',
            'class': 'form-control mb-2'
        }),
        label="Subcategories"
    )

    class Meta:
        model = Folder
        fields = ['name', 'parent', 'subcategories']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only top-level categories can be parents
        self.fields['parent'].queryset = Folder.objects.filter(parent__isnull=True)
        self.fields['parent'].required = False



from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

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
        fields = ['username', 'email', 'password1', 'password2', 'department','role']
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
