from django import forms

class TextReponseForm(forms.Form):
    response = forms.CharField(max_length=300, help_text="Enter your answer.")

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=300, help_text="Enter your username.")

class JoinRoomForm(forms.Form):
    room_Code = forms.IntegerField(help_text="Enter the room code.")
