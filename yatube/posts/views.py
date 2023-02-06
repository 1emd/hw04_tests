from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


TEN_POSTS_IN_PAGE = 10


def get_page(request, post_list):
    paginator = Paginator(post_list, TEN_POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = get_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group').all()
    page_obj = get_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = get_page(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id
    )
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {'form': form, }
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'is_edit': True,
    }
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, 'posts/post_create.html', context)
    return redirect('posts:post_detail', post_id=post_id)
