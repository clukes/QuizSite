from django.contrib import admin

# Register your models here.
from .models import TextResponse, GenericQuestion, TextQuestion, Round, User, Game, UserScore, Quiz

admin.site.register(GenericQuestion)
admin.site.register(TextQuestion)
admin.site.register(TextResponse)
admin.site.register(User)
admin.site.register(UserScore)
admin.site.register(Game)
admin.site.register(Quiz)

@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'number', 'title')
