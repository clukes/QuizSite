from django import forms
from quiz.models import MultipleChoiceQuestion, MultipleChoiceOption
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

no_space_validator = RegexValidator(
    r' ',
    _('No spaces allowed'),
    inverse_match=True,
    code='invalid_username')

alphanumeric = RegexValidator(
    r'^[0-9a-zA-Z]*$',
    'Only alphanumeric characters are allowed.')

class TextReponseForm(forms.Form):
    response = forms.CharField(max_length=300, help_text="Enter your answer.")

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=300, help_text="Enter your username.", validators=[no_space_validator, alphanumeric])

class JoinRoomForm(forms.Form):
    room_Code = forms.IntegerField(help_text="Enter the room code.")

class MultipleChoiceForm(forms.ModelForm):
    response = forms.ModelChoiceField(MultipleChoiceOption.objects.all(),
                                    widget=forms.RadioSelect,
                                    empty_label=None,
                                    label="")

    class Meta:
        model = MultipleChoiceQuestion
        exclude=["image_url"]

    def __init__(self, instance, *args, **kwargs):
        super(MultipleChoiceForm, self).__init__(*args, **kwargs)
        self.fields['response'].queryset = MultipleChoiceOption.objects.filter(question=instance)
