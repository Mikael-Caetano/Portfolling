from django.contrib import admin
from .models import Portfoller, Project

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 3

class PortfollerAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['username', 'profile_picture']}),
        ('Personal Information', {'fields': ['first_name', 'last_name', 'birthdate', 'country_of_birth', 'biography']}),
        ('Job And Contact Information', {'fields': ['career', 'email'], 'classes': ['collapse']}),
    ]
    inlines = [ProjectInline]
    list_display = ('username', 'first_name', 'last_name', 'career')
    list_filter = ['birthdate', 'career', 'country_of_birth']
    search_fields = ['first_name', 'last_name']

admin.site.register(Portfoller, PortfollerAdmin)