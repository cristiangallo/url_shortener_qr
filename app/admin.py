# -*- coding: UTF-8 -*-

from django.contrib import admin
from .models import URL


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ["id", "url", "short_url", "error_correct", "thumb_qr"]
