# -*- coding: UTF-8 -*-

import qrcode
from django.db import models
from django.conf import settings
# from django.contrib.sites.models import Site
#
# PROTOCOLO_SITIO = f"{settings.USE_HTTPS and 'https' or 'http'}://{Site.objects.get_current().domain}"


class URL(models.Model):
    from sorl.thumbnail import ImageField as sorl_thumbnail_ImageField

    url = models.URLField(max_length=512)
    qr = sorl_thumbnail_ImageField(max_length=255, null=True, blank=True, editable=False)

    class Meta:
        verbose_name, verbose_name_plural = "URL", "URLs"

    def __str__(self):
        return f"{self.url}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        self.make_qr()

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
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        qr_big.add_data(s.tinyurl.short(self.url))
        img_qr_big = qr_big.make_image().convert('RGB')

        logo = Image.open(settings.MEDIA_ROOT / 'LOGOBLC.jpg').resize((120, 120))

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