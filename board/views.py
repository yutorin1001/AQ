from django.shortcuts import render, redirect
from .models import Post, Connection,  Reply, Thread
from .forms import PostForm, ThreadForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from itertools import chain
from django.utils.timezone import now
from .models import UploadImage
from .forms import UploadForm
from .forms import ProfileForm
from django.http import HttpResponseForbidden
from .models import Thread, Post
from .forms import PostForm
from django.db.models import Max
import bleach

ALLOWED_TAGS = ['iframe', 'canvas', 'b', 'i', 'u', 'a', 'span', 'div', 'br', 'p', 'strong', 'em']
ALLOWED_ATTRIBUTES = {
    '*': ['style', 'class'],
    'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen'],
    'a': ['href', 'title', 'target'],
}

def user_profile(request, username):
    # ユーザー情報を取得
    user = get_object_or_404(User, username=username)

    # ユーザーの投稿を取得
    posts = Post.objects.filter(user=user)
    # ユーザーの返信を取得
    replies = Reply.objects.filter(user=user)
    # 投稿と返信を結合して、作成日時でソート
    combined = sorted(
        chain(posts, replies),
        key=lambda instance: instance.created_at,
        reverse=True
    )

    # 指定されたユーザーが「いいね」した投稿を取得（いいね順）
    liked_posts = Post.objects.filter(postlike__user=user).order_by('-postlike__liked_at')
    # プロフィール編集フォーム（本人のみ編集可能）
    form = None
    if request.user == user:
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=user.profile)
            if form.is_valid():
                form.save()
                return redirect('user_profile', username=user.username)  # プロフィールページにリダイレクト
        else:
            form = ProfileForm(instance=user.profile)

    # テンプレートに渡すコンテキスト
    context = {
        'profile_user' : user,
        # プロフィールのユーザー
        'posts': posts,  # ユーザーの投稿のみを表示
        'liked_posts': liked_posts,  # 指定されたユーザーが「いいね」した投稿
        'form': form,          # プロフィール編集フォーム（本人のみ表示）
        'user': request.user, 
    }
    return render(request, 'board/profile.html', context)


def post_list(request):
    # 投稿と画像を取得
    posts = Post.objects.all()
    images = UploadImage.objects.all()
    # スレッドごとに最新の投稿日時を取得し、その順で並べる
    threads = Thread.objects.annotate(
        latest_post=Max('posts__created_at')
    ).order_by('-latest_post', '-created_at')

    # 投稿と画像を結合し、作成日時でソート
    combined = sorted(
        chain(posts, images),
        key=lambda instance: instance.created_at,
        reverse=True
    )
    # 投稿フォーム
    post_form = PostForm()
    # スレッド作成フォーム
    thread_form = ThreadForm()

    # POSTリクエストの処理
    if request.method == 'POST':
        if 'content' in request.POST:  # 投稿フォームからの送信
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user
                
                clean_content = bleach.clean(
                    post_form.cleaned_data['content'],
                    tags=ALLOWED_TAGS,
                    attributes=ALLOWED_ATTRIBUTES,
                    strip=True
                )
                post.content = clean_content
                
                post.save()
                return redirect('post_list')
        elif 'title' in request.POST:  # スレッド作成フォームからの送信
            thread_form = ThreadForm(request.POST)
            if thread_form.is_valid():
                thread = thread_form.save(commit=False)
                thread.user = request.user
                thread.save()
                return redirect('post_list')

    profile_user = request.user.profile if request.user.is_authenticated else None

    return render(request, 'board/post_list.html', {
        'combined': combined,
        'threads': threads,
        'post_form': post_form,
        'thread_form': thread_form,
        'profile_user': profile_user,
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # request.FILESを追加
        if form.is_valid():
            post = form.save(commit=False)  # フォームからインスタンスを作成するが、まだ保存しない
            post.user = request.user        # 現在ログイン中のユーザーを割り当てる
            post.save()                     # インスタンスを保存
            return redirect('post_list')    # 投稿後に投稿一覧にリダイレクト
    else:
        form = PostForm()
    return render(request, 'board/post_list.html', {'form': form})

def post_prof(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'board/prof.html', {'posts' : posts})
    



def like_post(request, post_id=None, image_id=None):
    if post_id:
        # 投稿に対する「いいね」
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.like.all():
            post.like.remove(request.user)  # すでに「いいね」している場合は削除
            liked = False
        else:
            post.like.add(request.user)  # 「いいね」を追加
            liked = True
        like_count = post.like.count()
    elif image_id:
        # 画像に対する「いいね」
        image = get_object_or_404(UploadImage, id=image_id)
        if request.user in image.like.all():
            image.like.remove(request.user)  # すでに「いいね」している場合は削除
            liked = False
        else:
            image.like.add(request.user)  # 「いいね」を追加
            liked = True
        like_count = image.like.count()
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

    return JsonResponse({'liked': liked, 'like_count': like_count})

@login_required
def add_reply(request, post_id=None, image_id=None):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            if post_id:
                post = get_object_or_404(Post, id=post_id)
                reply = Reply.objects.create(post=post, user=request.user, content=content)
            elif image_id:
                image = get_object_or_404(UploadImage, id=image_id)
                reply = Reply.objects.create(image=image, user=request.user, content=content)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid request'})

            return JsonResponse({
                'success': True,
                'reply': {
                    'user': reply.user.username,  # ユーザー名
                    'content': reply.content,  # 返信内容
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 作成日時
                }
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})





class DetailPost(LoginRequiredMixin, DetailView):
    """投稿詳細ページ"""
    model = Post
    template_name = 'board/detail.html'  # 使用するテンプレート
    context_object_name = 'post'





def image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user 
            form.save()  # 画像を保存
            return redirect('post_list')  # アップロード後に投稿一覧にリダイレクト
    else:
        form = UploadForm()
    # アップロード済みの画像を取得
    images = UploadImage.objects.all()

    return render(request, 'board/post_list.html', {
        'upload_form': form,
        'images': images,
    })
    





@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    connection = request.user.connection

    if target_user in connection.following.all():
        connection.following.remove(target_user)  # フォロー解除
        is_following = False
    else:
        connection.following.add(target_user)  # フォロー
        is_following = True

    return JsonResponse({'success': True, 'is_following': is_following})


@login_required
def following_posts(request):
    # 自分がフォローしているユーザー一覧
    following_users = request.user.connection.following.all()
    # そのユーザーたちの投稿だけを取得
    posts = Post.objects.filter(user__in=following_users).order_by('-created_at')
    # そのユーザーたちの返信だけを取得
    replies = Reply.objects.filter(user__in=following_users).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        post_id = request.POST.get('post_id')
        if content and post_id:
            post = get_object_or_404(Post, id=post_id)
            reply = Reply.objects.create(post=post, user=request.user, content=content)
            return JsonResponse({
                'success': True,
                'reply': {
                    'user': reply.user.username,  # ユーザー名
                    'content': reply.content,  # 返信内容
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 作成日時
                }
            })

    return render(request, 'board/following_posts.html', {
        'posts': posts,
        'replies': replies,
    })




@login_required
def create_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.user = request.user
            thread.save()
            return redirect('thread_detail', thread_id=thread.id)  
    else:
        form = ThreadForm()
    return render(request, 'board/th.html', {'form': form})

def thread_list(request):
    threads = Thread.objects.all().order_by('-created_at')
    return render(request, 'board/thread_list.html', {'threads': threads})



def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    posts = Post.objects.filter(thread=thread).order_by('created_at')
    post_form = PostForm()

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.thread = thread
            post.save()
            return redirect('thread_detail', thread_id=thread.id)

    return render(request, 'board/thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'post_form': post_form,
    })



def top(request):
    return render(request, 'top.html')
