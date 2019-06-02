from django.urls import path
from .views import (
        CourseListView, 
        CourseDetailListView,
        LectureDetailListView,
        QuizCourseListView,
        QuizCourseDetailListView,
        QuizNamesListView,
        QuizQuestions,
        QuizResult,
        lectureQAForumData,
        QuizAttemptedListView,
        CourseStudingListView,
        )

urlpatterns = [
                path('courses', CourseListView.as_view(), name='course_list'),
                path('courses/coursedetail/<slug:slug>', CourseDetailListView.as_view(), name='coursedetail_list'),
                path('courses/lecturedetail/<slug:subjectId>', LectureDetailListView.as_view(), name='lecturedetail_list'),
                path('courses/lectureqaforum', lectureQAForumData, name='lecture_qaforum'),
                path("courses/studying",CourseStudingListView.as_view(),name='courses_studing'),
                path('quiz/courses', QuizCourseListView.as_view(), name='quiz_course_list'),
                path('quiz/courses/coursedetail/<slug:slug>', QuizCourseDetailListView.as_view(), name='quiz_coursedetail_list'),
                path('quiz/names/<slug:slug>',QuizNamesListView.as_view(),name='quiz_names_coursedetail_list'),
                path('quiz/questions/<slug:quizid>/<int:qid>/<str:action>',QuizQuestions.as_view(),name='quiz_questions'),
                path("quiz/<slug:quizid>/result",QuizResult.as_view(),name='quiz_result'),
                path("quiz/attempted",QuizAttemptedListView.as_view(),name='quiz_attempted'),
            ]

