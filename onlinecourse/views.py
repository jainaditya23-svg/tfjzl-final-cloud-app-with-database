from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import logging

# Import models
from .models import Course, Enrollment, Question, Choice, Submission

logger = logging.getLogger(__name__)


# ================================
# Registration
# ================================
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")

        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


# ================================
# Login
# ================================
def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)

    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


# ================================
# Logout
# ================================
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# ================================
# Enrollment check
# ================================
def check_if_enrolled(user, course):
    if user.id is None:
        return False
    return Enrollment.objects.filter(user=user, course=course).exists()


# ================================
# Course List View
# ================================
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]

        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)

        return courses


# ================================
# Course Detail View
# ================================
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# ================================
# Enroll
# ================================
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if user.is_authenticated and not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# ================================
# Extract Answers
# ================================
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answers.append(int(request.POST[key]))
    return submitted_answers


# ================================
# Submit Exam
# ================================
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = extract_answers(request)

    submission.choices.set(selected_ids)
    submission.save()

    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result',
                args=(course.id, submission.id))
    )


# ================================
# Show Exam Result
# ================================
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]

    total_score = 0
    question_results = []

    for question in course.question_set.all():
        if question.is_get_score(selected_ids):
            total_score += question.grade
            question_results.append((question, True))
        else:
            question_results.append((question, False))

    context = {
        'course': course,
        'score': total_score,
        'question_results': question_results,
        'submission': submission
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)