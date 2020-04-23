from django.contrib import admin

# Register your models here.
from .models import TextResponse, GenericQuestion, TextQuestion, Round, User, Game, UserScore

admin.site.register(GenericQuestion)
admin.site.register(TextQuestion)
admin.site.register(TextResponse)
admin.site.register(Round)
admin.site.register(User)
admin.site.register(UserScore)
admin.site.register(Game)
