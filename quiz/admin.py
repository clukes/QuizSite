from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

# Register your models here.
from .models import *

admin.site.register(GenericQuestion)
admin.site.register(GenericResponse)
admin.site.register(User)
admin.site.register(UserScore)
admin.site.register(Game)
class GenericQuestionInline(GenericStackedInline):
    model = GenericQuestion
    max_num = 1
    min_num = 1
    verbose_name_plural = "Generic Question"

@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
    ]

class MultipleChoiceOptionInline(admin.TabularInline):
    model = MultipleChoiceOption
    min_num = 2
    extra = 2

@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
        MultipleChoiceOptionInline,
    ]

class ProgressiveStageInline(admin.TabularInline):
    model = ProgressiveStage
    min_num = 2
    extra = 2

@admin.register(ProgressiveQuestion)
class ProgressiveQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
        ProgressiveStageInline
    ]
    readonly_fields = ["step"]

class OrderingElementInline(admin.TabularInline):
    model = OrderingElement
    min_num = 2
    extra = 2

@admin.register(OrderingQuestion)
class OrderingQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
        OrderingElementInline,
    ]

    def save_related(self, request, form, formsets, change):
        super(OrderingQuestionAdmin, self).save_related(request, form, formsets, change)
        try:
            if(form.instance.generic_question.id):
                generic = GenericQuestion.objects.get(id=form.instance.generic_question.id)
                answer = ', '.join([str(i) for i in form.instance.elements.order_by('correct_ordering')])
                generic.answer = answer
                generic.save()
        except GenericQuestion.DoesNotExist:
            pass


@admin.register(TextResponse)
class TextResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'response')

@admin.register(MapQuestion)
class MapQuestionAdmin(admin.ModelAdmin):
    inlines = [
        GenericQuestionInline,
    ]

class GenericQuestionRoundInline(admin.TabularInline):
    model = GenericQuestion
    readonly_fields = ["get_edit_link", "content_type", "object_id"]

    def get_edit_link(self, obj=None):
        obj = obj.detail
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[str(obj.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=_("Edit this %s separately") % obj._meta.verbose_name,
            ))
        return _("(save and continue editing to create a link)")
    get_edit_link.short_description = _("Edit link")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'number', 'title')
    inlines = [
        GenericQuestionRoundInline,
    ]

class RoundInline(admin.TabularInline):
    model = Round
    readonly_fields = ["get_edit_link"]
    extra = 3

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[str(obj.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=_("Edit this %s separately") % obj._meta.verbose_name,
            ))
        return _("(save and continue editing to create a link)")
    get_edit_link.short_description = _("Edit link")

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'description')
    inlines = [
        RoundInline,
    ]
