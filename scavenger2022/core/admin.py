from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, QrCode, Hint


class HintsInLine(admin.StackedInline):
    model = Hint


class QrCodeAdmin(admin.ModelAdmin):
    fields = ["location"]
    inlines = [HintsInLine]


admin.site.register(User, UserAdmin)

admin.site.register(QrCode, QrCodeAdmin)
