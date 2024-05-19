from django import forms

class DateForm(forms.Form):
    date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
