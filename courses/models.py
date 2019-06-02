from django.db import models
from django.urls import reverse
import random, os
from django.contrib.auth.models import User
from datetime import datetime
import json

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1,3910209312)
    name, ext = get_filename_ext(filename)
    final_name = f'{new_filename}{ext}'
    return f'products/{new_filename}/{final_name}'

def pub_date_pretty(pub_date):
    return pub_date.strftime('%b %e %Y')


# Create your models here.
#Name of the Competitive exams
class Course(models.Model):
    title       = models.CharField(max_length=120)
    description = models.TextField()
    image       = models.ImageField(upload_to=upload_image_path, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        #return f"/products/{self.slug}/"
        return reverse('coursedetail_list',kwargs={'slug':self.title})

    def get_quiz_absolute_url(self):
        return reverse('quiz_coursedetail_list',kwargs={'slug':self.id})

#Subject in the competitive exam
class CourseDetail(models.Model):
    subject     = models.CharField(max_length=120)
    description = models.TextField()
    image       = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    course      = models.ForeignKey(Course,on_delete=models.CASCADE)

    def __str__(self):
        return self.subject
    
    def get_absolute_url(self):
        return reverse('lecturedetail_list',kwargs={'subjectId':self.id})

    def get_quiz_absolute_url(self):
        return reverse('quiz_names_coursedetail_list',kwargs={'slug':self.id})

class LectureDetail(models.Model):
    url =   models.CharField(max_length=1024)
    title = models.CharField(max_length=120)
    section = models.CharField(max_length=120)
    course_detail = models.ForeignKey(CourseDetail,on_delete=models.CASCADE)

    def __str__(self):
        return self.course_detail.subject + " : "+ self.section + " : "+ self.title

class Quiz(models.Model):
    title = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    course_detail = models.ForeignKey(CourseDetail,on_delete=models.CASCADE)
    totalQuestion =   models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.course_detail.subject + " : "+ self.title

    def get_absolute_url(self):
        return reverse('quiz_questions', kwargs={'quizid':self.id, 'qid':0,'action':'none'} )

class QuizDetail(models.Model):
    question =   models.CharField(max_length=1024)
    choices  =   models.TextField()
    mcq      =   models.BooleanField(default=False) 
    answer   =   models.CharField(max_length=16)
    quiz     =   models.ForeignKey(Quiz,on_delete=models.CASCADE)
    questionNo = models.IntegerField()     

    def __str__(self):
        return self.quiz.title + " : "+ self.question



class UserQuiz(models.Model):
    COMPLETIONSTATUS_NOTATTEMPTED = 0
    COMPLETIONSTATUS_ATTEMPTED = 1
    COMPLETIONSTATUS_COMPLETED = 2

    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz  = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    competionStatus = models.IntegerField(blank=True)
    lastAccessed = models.DateTimeField(default=datetime.now, blank=True)

    def get_result_absolute_url(self):
        return reverse('quiz_result', kwargs={'quizid':self.quiz.id} )

    
class UserAnswer(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE)
    qid    = models.ForeignKey(QuizDetail, on_delete=models.CASCADE)
    answer = models.CharField(max_length=16)
    pub_date    = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.qid.quiz.title + " : "+ self.qid.question

class QuestionForum(models.Model):
    lecture     = models.ForeignKey(LectureDetail, on_delete=models.CASCADE)
    question    = models.CharField(max_length=4096)
    author      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pub_date    = models.DateTimeField(default=datetime.now, blank=True)
    votes_total = models.IntegerField(default=1)
    answered    = models.BooleanField(default=False)

    def __str__(self):
        return self.lecture.title + " : " + self.question
    def dict_obj(self):

        if self.author is not None:
            auth  = self.author.username
        else:
            auth = "anonymous"
        try:
            return {
                "qid"         : self.id,
                "question"    : self.question,
                "author"      : auth,
                "pub_date"    : pub_date_pretty(self.pub_date), 
                "votes"       : self.votes_total,
                "answered"    : self.answered
            }
        except Exception as e: 
                print(e)

class AnswerForum(models.Model):
    answer   = models.TextField()
    question = models.ForeignKey(QuestionForum, on_delete=models.CASCADE)
    author   = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    pub_date = models.DateTimeField(default=datetime.now, blank=True)
    votes_total = models.IntegerField(default=1)
    
    
    def dict_obj(self):
        if self.author is not None:
            auth  = self.author.username
        else:
            auth = "anonymous"
        try:
            return {
                "answer"   : self.answer,
                "qid"      : self.question.id,
                "author"   :  auth,
                "pub_date" : pub_date_pretty(self.pub_date), 
                "votes"    : self.votes_total 
            }
        except Exception as e: 
            print(e)

class UserCourse(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    subject         = models.ForeignKey(CourseDetail, on_delete=models.CASCADE)
    lecture         = models.ForeignKey(LectureDetail, on_delete=models.CASCADE)
    lastAccessed    = models.DateTimeField(default=datetime.now, blank=True)

    def get_lecturedetail_absolute_url(self):
        return reverse('lecturedetail_list', kwargs={'subjectId':self.subject.id} )
