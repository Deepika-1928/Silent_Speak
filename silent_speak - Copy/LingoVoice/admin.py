from django.contrib import admin
from .models import Feedback  # Imports your exact Feedback model

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # Columns that will display in your admin dashboard grid
    list_display = ('id', 'user', 'message', 'created_at')
    
    # Filters on the right sidebar to sort by date or user
    list_filter = ('created_at', 'user')
    
    # Search bar to instantly look through feedback messages
    search_fields = ('message', 'user__username')