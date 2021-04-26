from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from yatube.settings import PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author).exists()
    )
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'following': following,
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form,
            'exp_action': 'new_post'
        })
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'post.html', {
            'post': post,
            'author': post.author,
            'comments': comments,
            'form': form
        })
    new_comment = form.save(commit=False)
    new_comment.author = request.user
    new_comment.post = post
    new_comment.save()
    return redirect('post', username, post_id)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username, post_id)
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=request.user.username
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form,
            'exp_action': 'post_edit',
            'post': post
        })
    form.save()
    return redirect('post', username, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'comments.html', {
            'form': form,
            'comments': comments,
        })
    new_comment = form.save(commit=False)
    new_comment.author = request.user
    new_comment.post = post
    new_comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect("profile", username)
    Follow.objects.get_or_create(user=request.user, author=author)
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    dell_follow = get_object_or_404(Follow, user=request.user, author=author)
    dell_follow.delete()
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
