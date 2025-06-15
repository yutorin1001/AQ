from django import template
from board.models import Post, UploadImage

register = template.Library()

@register.filter
def instanceof(obj, class_name):
    if class_name == "Post":
        return isinstance(obj, Post)
    elif class_name == "UploadImage":
        return isinstance(obj, UploadImage)
    return False