# reviews/admin.py
from django.contrib import admin
from .models import Review, ReviewVote

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['title', 'comment', 'user__username', 'product__name']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__title', 'user__username']

