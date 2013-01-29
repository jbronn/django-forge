from django.contrib import admin

from .models import Author, Module, Release


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    search_fields = ('name', 'author__name', 'tags', 'desc')


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('module', 'version')
    search_fields = ('version',
                     'module__name',
                     'module__author__name',
                     'module__tags',
                     'module__desc')


admin.site.register(Author, AuthorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Release, ReleaseAdmin)
