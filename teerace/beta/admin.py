from django.contrib import admin

from beta.models import BetaKey


class BetaKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "is_used")
    list_display_links = ("key",)
    list_filter = ("is_used",)


admin.site.register(BetaKey, BetaKeyAdmin)
