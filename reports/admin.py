# reports/admin.py
from django.contrib import admin
from .models import Category, Report

admin.site.register(Category)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "category", "owner", "created_at"]
    list_filter = ["report_type", "status", "category"]
