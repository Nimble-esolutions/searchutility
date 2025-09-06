from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# ---------------- Custom User ----------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
       
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)  #


# ---------------- Folder ----------------
class Folder(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_by = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subfolders",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------- PDF File ----------------
class PDFFile(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="pdfs/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_pdfs"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey(
        "Folder", on_delete=models.CASCADE, related_name="files", null=True, blank=True
    )
    
    # --- New fields for search optimization ---
    keywords = models.JSONField(default=list, blank=True)  # store keywords safely
    text_content = models.TextField(blank=True, default="")  # store extracted PDF text

    def delete(self, *args, **kwargs):
        """
        Ensure the file is deleted from storage when the database entry is removed.
        """
        if self.file:
            self.file.delete(save=False)  # remove file from storage
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Folder: {self.folder.name if self.folder else 'No Folder'})"
