from django.contrib import admin

from .models import Author, Module, Release


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('module', 'version')
    search_fields = ('version',
                     'module__name',
                     'module__author__name',
                     'module__tags',
                     'module__desc')


class ReleaseInline(admin.TabularInline):
    model = Release
    extra = 1


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    search_fields = ('name', 'author__name', 'tags', 'desc')

    inlines = [
        ReleaseInline,
    ]


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    inlines = [
        ModuleInline,
    ]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Release, ReleaseAdmin)
