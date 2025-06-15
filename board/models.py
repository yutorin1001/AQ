from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now



# Create your models here.


class Thread(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 必要に応じてカテゴリや説明文なども追加可能

    def __str__(self):
        return self.title


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='img/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, through='PostLike', related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "投稿"


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(default=now)  # いいねをした日時

    def __str__(self):
        return f"{self.user.username} liked {self.post.id} at {self.liked_at}"

    class Meta:
        ordering = ["-liked_at"]  




class Connection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='connection')
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    def __str__(self):
        return self.user.username

class UploadImage(models.Model):
    image = models.ImageField(upload_to='img/')  # 画像を保存するディレクトリを指定
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時を記録
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name='related_post_2', blank=True) 


    def __str__(self):
        return self.image.name





class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    image = models.ForeignKey(UploadImage, on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 返信したユーザー
    content = models.TextField()  # 返信内容
    created_at = models.DateTimeField(auto_now_add=True)  # 返信日時

    def __str__(self):
        if self.post:
            return f"Reply by {self.user.username} on Post {self.post.id}"
        elif self.image:
            return f"Reply by {self.user.username} on Image {self.image.id}"
        return f"Reply by {self.user.username}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "返信"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    icon = models.ImageField(upload_to='icons/', blank=True, null=True, default='icons/default_icon.png')  
    bio = models.TextField(blank=True, null=True)
     
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_user_connection(sender, instance, created, **kwargs):
    if created:
        Connection.objects.create(user=instance)