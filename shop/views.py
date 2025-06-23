from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate , logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.db.models import Q

def post_search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    return render(request, 'search_results.html', {
        'results': results,
        'query': query
    })
def home(request):
    posts = Post.objects.all().order_by('-created_at')  # Lấy bài viết mới nhất
    return render(request, 'index.html', {'posts': posts})

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', '/'))

def product_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.views += 1
    post.save(update_fields=['views'])
    comments = post.comments.all()  # Lấy tất cả bình luận của bài viết
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('product_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(request, 'product_detail.html', {'post': post, 'comments': comments, 'form': form})
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Đăng nhập luôn sau khi đăng ký
            messages.success(request, "Tài khoản đã được tạo thành công!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# View đăng nhập
def sign_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    else:
        form = AuthenticationForm()
    return render(request, 'sign_in.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')  # Chuyển hướng về trang chủ hoặc trang đăng nhậpdef logout_view(request):

@login_required
def like_post(request, post_id):
    # Kiểm tra nếu người dùng chưa đăng nhập, redirect đến trang đăng nhập
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
     
    post = get_object_or_404(Post, id=post_id)

    # Nếu người dùng đã like, bỏ like; nếu chưa like, thêm like
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('product_detail', post_id=post.id) 

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=['views'])  # Chỉ cập nhật trường 'views'
        return obj
        