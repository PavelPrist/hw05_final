from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic import ListView

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow
from .utils import paginator_page


@cache_page(5, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related("group")
    page_obj = paginator_page(request, posts)

    template = 'posts/index.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.filter(group=group)
    page_obj = paginator_page(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_page(request, posts)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists
    else:
        following = False
    template = 'posts/profile.html'
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):

    post = Post.objects.get(id=post_id)
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.is_published = False
        form.save()
        return redirect('posts:profile', request.user.username)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:

        return redirect('posts:post_detail', post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    posts = (
        Post.objects
        .select_related('author', 'group')
        .filter(author__following__user=request.user)
    )
    page_obj = paginator_page(request, posts)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    following_author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(
        user=request.user,
        author=following_author
    )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect('posts:profile', post.author.username)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author == request.user:
        comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.pk)


class SearchResultsView(ListView):
    model = Post
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Post.objects.filter(
            Q(text__icontains=query) | Q(
                author__username__icontains=query)
        )
        return object_list
