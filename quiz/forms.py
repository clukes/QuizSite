from django import forms
from quiz.models import MultipleChoiceQuestion, MultipleChoiceOption

class TextReponseForm(forms.Form):
    response = forms.CharField(max_length=300, help_text="Enter your answer.")

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=300, help_text="Enter your username.")

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
