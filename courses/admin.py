from django.contrib import admin
from .models import (
            Course, 
            CourseDetail, 
            LectureDetail, 
            Quiz,
            QuizDetail,
            QuestionForum,
            AnswerForum,
            UserQuiz,
            UserAnswer,
            UserCourse,
        )

# Register your models here.
admin.site.register(Course)
admin.site.register(CourseDetail)
admin.site.register(LectureDetail)
admin.site.register(Quiz)
admin.site.register(QuizDetail)
admin.site.register(QuestionForum)
admin.site.register(AnswerForum)
admin.site.register(UserQuiz)
admin.site.register(UserAnswer)
admin.site.register(UserCourse)