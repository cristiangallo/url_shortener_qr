# -*- coding: UTF-8 -*-

from django.contrib import admin
from .models import URL


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ["url", "thumb_qr"]
