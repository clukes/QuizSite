from django import forms

class TextReponseForm(forms.Form):
    response = forms.CharField(max_length=300, help_text="Enter your answer.")
