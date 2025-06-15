from django import forms
from .models import Post
from .models import UploadImage
from .models import Profile
from .models import Thread



class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']  


        
class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadImage
        fields = ['image']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['icon', 'bio']  