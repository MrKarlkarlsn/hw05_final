from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm

MY_SLICE = 10


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
    all_posts = post.author.posts.count()
    context = {
        'post': post,
        'all_posts': all_posts
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
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'is_edit': True,
        'post': post,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)
