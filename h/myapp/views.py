from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.views.generic import CreateView, FormView, TemplateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from myapp.models import UserProfile, Posts, Comments
from myapp.forms import SignUpForm, LoginForm, ProfileEditForm, PostForm, CoverPicForm

class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "register.html"
    success_url = reverse_lazy("signin")


    def form_valid(self, form):
        messages.success(self.request,"account has been created")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"failed to create account")
        return super().form_invalid(form)


class SignInView(FormView):
    form_class = LoginForm
    template_name = "login.html"
    
    def post(self, request, *args, **kw):
        form = self.form_class(request.POST)
        if form.is_valid():
            uname = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password')
            usr = authenticate(request, username = uname, password = pwd)
            if usr:
                login(request, usr)
                return redirect("index")            
            messages.error(request, "invalkid credentials")
        return render(request, self.template_name, {'form':form})




class IndexView(CreateView, ListView):
    template_name = "index.html"
    form_class = PostForm
    model = Posts
    context_object_name = "posts"
    success_url = reverse_lazy("index")
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



class ProfileEditView(UpdateView):
    model = UserProfile
    form_class = ProfileEditForm
    template_name = "profileedit.html"
    success_url = reverse_lazy("index")

def add_like_view(request,*args,**kw):
    id = kw.get("pk")
    post_obj = Posts.objects.get(id = id)
    post_obj.liked_by.add(request.user)
    return redirect("index")

def add_comment_view(request, *args, **kw):
    id = kw.get('pk')
    post_obj = Posts.objects.get(id = id)
    comment = request.POST.get('comment')
    Comments.objects.create(user = request.user, comment_text = comment, post = post_obj)
    return redirect("index")

def remove_comment_view(request,*args,**kw):
    id = kw.get('pk')
    comment_obj = Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect("index")
    else:
        messages.error(request, "pls contact admin")
        return redirect("signin")
    
# localhost:8000/profiles/id
class ProfileDetailView(DetailView):
    template_name = "profile.html"
    model = UserProfile
    context_object_name = 'profile'
    

def change_cover_pic_view(request,*args,**kw):
    id = kw.get('pk')
    prof_obj = UserProfile.objects.get(id = id)
    form = CoverPicForm(instance = prof_obj, data = request.POST, files = request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profiledetail", pk=id)
    return redirect("profiledetail", pk=id)

class ProfileListView(ListView):
    model = UserProfile
    template_name = "profile-list.html"
    context_object_name = "profiles"

    
