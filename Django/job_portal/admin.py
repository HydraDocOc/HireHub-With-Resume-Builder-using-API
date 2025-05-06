from django.contrib import admin
from .models import (
    CustomUser , Company
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'mobile', 'role')
    search_fields = ('email', 'name')
    list_filter = ('role',)


@admin.register(Company)
class company(admin.ModelAdmin):
    list_display = ('name','description','logo_url')