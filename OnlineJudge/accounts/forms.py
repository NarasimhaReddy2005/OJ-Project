from django import forms
from .models import UserMetadata

class UserMetadataForm(forms.ModelForm):
    class Meta:
        model = UserMetadata
        fields = ['bio', 'email', 'linkedin', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: make picture input pretty
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
