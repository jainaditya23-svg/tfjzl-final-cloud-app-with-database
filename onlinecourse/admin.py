from django.contrib import admin

# ✅ Import ALL required models (added 3 new ones)
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


# Inline for Lesson inside Course
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# ✅ NEW: Inline for Choice inside Question
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


# ✅ NEW: Inline for Question
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


# Course Admin
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# ✅ NEW: Question Admin (IMPORTANT)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content']


# Lesson Admin
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


# ✅ Register all models
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

# ✅ NEW registrations
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)