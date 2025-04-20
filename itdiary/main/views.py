from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, ProjectForm, OfferForm, MessageForm, ReviewForm
from .models import Project, Offer, Message, Review, User
from django.db.models import Avg, Q


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'welcome.html')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def profile_view(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        user = request.user

    reviews = Review.objects.filter(reviewed=user)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    has_shared_project = Project.objects.filter(
        Q(client__in=[request.user, user]) &
        Q(executor__in=[request.user, user])
    ).exists() if user != request.user else False

    return render(request, 'profile.html', {
        'user_profile': user,
        'average_rating': round(average_rating, 1),
        'reviews': reviews,
        'can_review': has_shared_project,
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})


def project_list(request):
    search_query = request.GET.get('q')
    min_budget = request.GET.get('min_budget')
    max_budget = request.GET.get('max_budget')

    projects = Project.objects.all()

    if search_query:
        projects = projects.filter(title__icontains=search_query)

    if min_budget:
        projects = projects.filter(budget__gte=min_budget)

    if max_budget:
        projects = projects.filter(budget__lte=max_budget)

    return render(request, 'project_list.html', {
        'projects': projects,
        'search_query': search_query,
        'min_budget': min_budget,
        'max_budget': max_budget
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    offers = project.offers.all()

    if request.user.is_authenticated and request.user != project.client:
        if request.method == 'POST':
            form = OfferForm(request.POST)
            if form.is_valid():
                offer = form.save(commit=False)
                offer.project = project
                offer.freelancer = request.user
                offer.save()
                return redirect('project_detail', pk=pk)
        else:
            form = OfferForm()
    else:
        form = None

    return render(request, 'project_detail.html', {
        'project': project,
        'offers': offers,
        'form': form,
    })


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'edit_project.html', {'form': form, 'project': project})


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    return render(request, 'delete_project.html', {'project': project})


@login_required
def accept_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    project = offer.project

    if request.user != project.client:
        return redirect('project_detail', pk=project.pk)

    project.executor = offer.freelancer
    project.save()

    return redirect('project_detail', pk=project.pk)


@login_required
def project_chat(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user != project.client and request.user != project.executor:
        return redirect('home')

    messages = Message.objects.filter(
        sender__in=[project.client, project.executor],
        receiver__in=[project.client, project.executor]
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = project.executor if request.user == project.client else project.client
            msg.save()
            return redirect('project_chat', pk=pk)
    else:
        form = MessageForm()

    return render(request, 'project_chat.html', {
        'project': project,
        'messages': messages,
        'form': form
    })


@login_required
def leave_review(request, user_id, project_id):
    reviewed_user = get_object_or_404(User, pk=user_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed = reviewed_user
            review.project = project
            review.save()
            return redirect('profile', user_id=reviewed_user.id)
    else:
        form = ReviewForm()

    return render(request, 'leave_review.html', {
        'form': form,
        'reviewed_user': reviewed_user,
        'project': project
    })
