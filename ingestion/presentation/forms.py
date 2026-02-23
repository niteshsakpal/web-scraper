from django import forms


class JobSubmitForm(forms.Form):
    url = forms.URLField(
        label="Regulatory URL",
        max_length=2048,
        widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "https://example.gov/regulation"}),
    )
