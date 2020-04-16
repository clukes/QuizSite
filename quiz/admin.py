from django.contrib import admin

# Register your models here.
from .models import TextResponse, Question, Round, User, Game

admin.site.register(TextResponse)
admin.site.register(Question)
admin.site.register(Round)
admin.site.register(User)
admin.site.register(Game)
