
# Register your models here.
from django.contrib import admin
from .models import Profile, DiaryEntry, Comment, Like

admin.site.register(Profile)
admin.site.register(DiaryEntry)
admin.site.register(Comment)
admin.site.register(Like)
