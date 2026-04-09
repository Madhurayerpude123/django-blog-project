from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Post, Comment, Contact


# 🏠 HOME
def index(request):
    return render(request, "index.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id"),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


# 📝 SIGNUP
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists")
                return redirect('signup')

            User.objects.create_user(username=username, email=email, password=password)
            return redirect('signin')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('signup')

    return render(request, "signup.html")


# 🔐 SIGNIN
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, 'Invalid credentials')
            return redirect("signin")

    return render(request, "signin.html")


# 🚪 LOGOUT
def logout(request):
    auth.logout(request)
    return redirect('index')


# 📚 BLOG PAGE
def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.all().order_by("-id"),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


# ✍️ CREATE BLOG (🔥 FIXED)
@login_required
def create(request):
    if request.method == 'POST':
        postname = request.POST.get('postname')
        content = request.POST.get('content')
        category = request.POST.get('category')
        image = request.FILES.get('image')  # ✅ SAFE

        if not postname or not content or not category:
            messages.error(request, "All fields are required!")
            return redirect('create')

        try:
            Post.objects.create(
                postname=postname,
                content=content,
                category=category,
                image=image,
                user=request.user
            )
            messages.success(request, "Blog created successfully!")
            return redirect('profile', request.user.id)

        except Exception as e:
            print("ERROR:", e)
            messages.error(request, "Error creating blog")
            return redirect('create')

    return render(request, "create.html")


# 👤 PROFILE (🔥 FIXED)
@login_required
def profile(request, id):
    return render(request, 'profile.html', {
        'user': User.objects.get(id=id),
        'posts': Post.objects.filter(user_id=id),  # ✅ FIXED
        'media_url': settings.MEDIA_URL,
    })


# ✏️ PROFILE EDIT
@login_required
def profileedit(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.email = request.POST.get('email')
        user.save()

        messages.success(request, "Profile updated!")
        return redirect('profile', id)

    return render(request, "profileedit.html", {'user': user})


# ❤️ LIKE POST
@login_required
def increaselikes(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()

    return redirect("index")


# 📄 SINGLE POST
def post(request, id):
    post_obj = Post.objects.get(id=id)

    comments = Comment.objects.filter(post_id=id)

    return render(request, "post-details.html", {
        "user": request.user,
        'post': post_obj,
        'recent_posts': Post.objects.all().order_by("-id"),
        'media_url': settings.MEDIA_URL,
        'comments': comments,
        'total_comments': comments.count()
    })


# 💬 SAVE COMMENT
@login_required
def savecomment(request, id):
    if request.method == 'POST':
        content = request.POST.get('message')

        Comment.objects.create(
            post_id=id,
            user_id=request.user.id,
            content=content
        )

    return redirect("post", id)


# ❌ DELETE COMMENT
@login_required
def deletecomment(request, id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()

    return redirect("post", postid)


# ✏️ EDIT POST
@login_required
def editpost(request, id):
    post = Post.objects.get(id=id)

    if request.method == 'POST':
        post.postname = request.POST.get('postname')
        post.content = request.POST.get('content')
        post.category = request.POST.get('category')
        post.save()

        messages.success(request, "Post updated!")
        return redirect('profile', request.user.id)

    return render(request, "postedit.html", {'post': post})


# 🗑️ DELETE POST
@login_required
def deletepost(request, id):
    Post.objects.get(id=id).delete()
    messages.success(request, "Post deleted!")
    return redirect('profile', request.user.id)


# 📩 CONTACT
def contact_us(request):
    context = {}

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        context['message'] = f"Dear {name}, Thanks for your time!"

    return render(request, "contact.html", context)