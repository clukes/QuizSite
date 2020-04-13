from django.contrib import admin

# Register your models here.
from .models import TextResponse, Question, Round

admin.site.register(TextResponse)
admin.site.register(Question)
admin.site.register(Round)
