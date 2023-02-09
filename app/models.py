# -*- coding: UTF-8 -*-

import secrets
import qrcode
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site

PROTOCOLO_SITIO = f"{settings.USE_HTTPS and 'https' or 'http'}://{Site.objects.get_current().domain}"


def custom_id():
    return secrets.token_urlsafe(8)


class URL(models.Model):
    from sorl.thumbnail import ImageField as sorl_thumbnail_ImageField

    class ErrorCorrect(models.IntegerChoices):
        ERROR_CORRECT_L = 1, "Se pueden corregir alrededor del 7% o menos de los errores"
        ERROR_CORRECT_M = 0, "Se pueden corregir alrededor del 15% o menos de los errores"
        ERROR_CORRECT_Q = 3, "Se pueden corregir alrededor del 25% o menos de los errores"
        ERROR_CORRECT_H = 2, "Se pueden corregir alrededor del 30% o menos de los errores"

    id = models.CharField(max_length=11, primary_key=True, default=custom_id, editable=False)
    url = models.URLField(max_length=512)
    logo = sorl_thumbnail_ImageField(max_length=255, upload_to="qr-codes/logos/", null=True, blank=True)
    qr = sorl_thumbnail_ImageField(max_length=255, null=True, blank=True, editable=False)
    error_correct = models.SmallIntegerField(choices=ErrorCorrect.choices, default=0)

    class Meta:
        verbose_name, verbose_name_plural = "URL", "URLs"

    def __str__(self):
        return f"{self.id}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        self.make_qr()

    def short_url(self):
        return f"{PROTOCOLO_SITIO}/{self.id}"

    def make_qr(self):
        import pyshorteners
        from PIL import Image
        from string import ascii_lowercase, digits
        from random import choice
        from django.conf import settings
        from os import path

        s = pyshorteners.Shortener()
        filename = path.join(f'qr-codes/', f"qr-{''.join(choice(ascii_lowercase + digits) for x in range(10))}.jpg")
        qr_big = qrcode.QRCode(
            # version=1,
            # box_size=20,
            # border=1,
            # error_correction=qrcode.constants.ERROR_CORRECT_H
            error_correction=self.error_correct
        )
        qr_big.add_data(self.short_url())
        img_qr_big = qr_big.make_image().convert('RGB')
        if self.logo.name:
            logo = Image.open(f"{settings.BASE_DIR}{self.logo.url}").resize((120, 120))
            pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
            img_qr_big.paste(logo, pos)
        img_qr_big.save(settings.MEDIA_ROOT / filename)
        self.qr = filename
        super().save(update_fields=['qr'])

    def thumb_qr(self):
        from django.utils.safestring import mark_safe
        from sorl.thumbnail import get_thumbnail

        if not self.qr:
            self.make_qr()
        return mark_safe(
            f'<a href="{self.qr.url}" target="_blank">'
            f'<img src="{get_thumbnail(self.qr, "160", crop="center", quality=95).url}" /></a>')
    thumb_qr.short_description = 'Código QR'