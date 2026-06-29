from django.contrib import admin
from django.db.models import Count
from .models import Movie, Genre, Review

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text')
    ordering = ('-created_at',)

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Text'

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('movies.can_moderate_reviews'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('movies.can_moderate_reviews'):
            return True
        return super().has_delete_permission(request, obj)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'review_count')
    list_filter = ('genres',)
    search_fields = ('title',)
    ordering = ('title',)
    filter_horizontal = ('genres',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_review_count=Count('reviews'))
        return queryset

    def review_count(self, obj):
        return obj._review_count
    review_count.short_description = 'Reviews Count'
    review_count.admin_order_field = '_review_count'

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser