from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
from .models import GenericResponse, TextResponse, GenericQuestion, TextQuestion, ImageQuestion, Round, User, Game, UserScore, Quiz

admin.site.register(GenericQuestion)
admin.site.register(GenericResponse)
admin.site.register(User)
admin.site.register(UserScore)
admin.site.register(Game)
admin.site.register(Quiz)

@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'number', 'title')

class GenericQuestionInline(GenericTabularInline):
    model = GenericQuestion
    max_num = 1
    min_num = 1
    verbose_name_plural = "Generic Question"

@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
    ]

@admin.register(ImageQuestion)
class ImageQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
    ]


@admin.register(TextResponse)
class TextResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'response')
