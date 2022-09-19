from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

MY_SLICE = 10


@cache_page(20)
def index(request):
    templates = 'posts/index.html'
    posts = Post.objects.all().select_related()
    paginator = Paginator(posts, MY_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Это главная страница проекта Yatube',
        'page_obj': page_obj,
    }
    return render(request, templates, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    title = group.title
    templates = 'posts/group_list.html'
    paginator = Paginator(posts, MY_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,

    }
    return render(request, templates, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    all_posts_count = post.author.posts.count()
    context = {
        'post': post,
        'all_posts': all_posts_count,
        'form': CommentForm(request.POST or None),
        'comments': post.comments.all()

    }
    return render(request, 'posts/post_detail.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username).all()
    paginator = Paginator(post_list, MY_SLICE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'post_count': len(post_list),
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', new_post.author)

    form = PostForm()

    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'is_edit': True,
        'post': post,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    post.delete()
    return redirect('posts:profile', username=request.user)


@login_required
def add_comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts_list, MY_SLICE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    template = 'posts/follow.html'
    context = {
        'page': page
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        Follow.objects.get_or_create(author=profile_user)
        return redirect('posts:profile', username=username)
    return redirect('posts:main')


@login_required
def profile_unfollow(request, username):
    profile_user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=profile_user).delete()
    return redirect('posts:profile', username=username)
