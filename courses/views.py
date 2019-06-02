from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import Course, CourseDetail, LectureDetail, Quiz, QuizDetail, QuestionForum, AnswerForum, UserAnswer, UserQuiz, UserCourse
from clovinsti import settings
import json
from .forms import QuestionForm, AnswerForm
from datetime import datetime
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist

from clovinsti.forms import LoginForm

# Create your views here.
class CourseListView(ListView):
    template_name = "courses/course_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        return Course.objects.all()

# Create your views here.
class CourseDetailListView(ListView):
    template_name = "courses/coursedetail_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        title = self.kwargs.get('slug')
        course = Course.objects.get(title=title)
        try:
            return course.coursedetail_set.all()
        except CourseDetail.DoesNotExist:
            raise Http404("Course details don't exist for "+ title)
        except:
            raise Http404("Hummm")

class LectureDetailListView(ListView):
    template_name = "courses/Lecturedetail_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        context['qform'] = QuestionForm()
        context['aform'] = AnswerForm()
        context['lform'] = LoginForm()
        context['subjectId'] = self.kwargs.get('subjectId')
        
        if not self.request.user.is_authenticated :
            context['lectureId'] = 0
            context['lectureUrl'] = ""
            context['lectureTitle'] = ""
        else:
            try:
                userCourse = UserCourse.objects.get(user=self.request.user,
                                subject=CourseDetail.objects.get(id=self.kwargs.get('subjectId')))
                context['lectureId'] = userCourse.lecture.id
                context['lectureUrl'] = userCourse.lecture.url
                context['lectureTitle'] = userCourse.lecture.title

            except UserCourse.DoesNotExist:
                context['lectureId'] = 0
                context['lectureUrl'] = ""
                context['lectureTitle'] = ""

        return context

    def get_queryset(self, *args, **kwargs):
        subjectId = self.kwargs.get('subjectId')
        coursedetail = CourseDetail.objects.get(id=subjectId)
        section_list = []
        section_detail = []
        try:
            lecturedetail = coursedetail.lecturedetail_set.all()
            for obj in lecturedetail:
                if ( obj.section not in section_list):
                    section_list.append(obj.section) 
                    d = dict(section=obj.section, lectures=[], qalist={})
                    print("1")
                    d["lectures"].append(dict(id=obj.id, title=obj.title, url=obj.url))   
                    print("2")
                    section_detail.append(d)
                else:
                    section_detail[-1]["lectures"].append(dict(id=obj.id, title=obj.title, url=obj.url, qalist=get_qa(obj.id)))
            return section_detail
        except LectureDetail.DoesNotExist:
            raise Http404("Lecture details don't exist for "+ subjectId)
        except:
            raise Http404("Hummm")

    def post(self, request, **kwargs):
        print(request.POST)
        if not request.user.is_authenticated:
            print("user is unauthenticated")
            return HttpResponse(json.dumps({'data': None}), content_type="application/json", status=401, reason="login is required")        
        
        subjectId = self.kwargs.get('subjectId')
        print("slug: ", subjectId)
        if request.POST.get('post_request') == 'question':
            question = request.POST.get('question')
            lectureid = request.POST.get('lectureId')
            q = QuestionForum() #model
            q.question = question
            q.lecture = LectureDetail.objects.get(id=lectureid)
            q.author = request.user
            q.pub_date =  datetime.now()
            q.save()
            #subject = q.lecture.course_detail.subject
        elif request.POST.get('post_request') == 'answer':
            answer = request.POST.get('answer')
            print(f"answer {answer}")
            qid = request.POST.get('questionId')
            lectureid = request.POST.get('lectureId')
            a = AnswerForum() #model
            a.answer = answer
            a.question = QuestionForum.objects.get(id=qid)
            a.author = request.user
            a.pub_date =  datetime.now()
            a.save()
            #subject = a.question.lecture.course_detail.subject
        elif request.POST.get('post_request') == 'studing':
            print(f"post studing {request.POST}")
            try:
                userCourse = UserCourse.objects.get(user=request.user,
                             subject=CourseDetail.objects.get(id=request.POST.get('subjectId')))
            except UserCourse.DoesNotExist:
                userCourse = UserCourse()
            except:
                return HttpResponse("", content_type="text/html", status=404, reason="bad parameters")            
            
            userCourse.user = request.user
            userCourse.subject = CourseDetail.objects.get(id=request.POST.get('subjectId'))
            userCourse.lecture = LectureDetail.objects.get(id=request.POST.get('lectureId'))
            userCourse.section_loop_id = request.POST.get('sectionLoopId')
            userCourse.lecture_loop_id = request.POST.get('lectureLoopId')
            userCourse.lastAccessed = datetime.now()
            userCourse.save()
            return HttpResponse("", content_type="text/html", status=200)        

        data = None
        if(lectureid):
            data = get_qa(lectureid)
        return HttpResponse(json.dumps({'data': data}), content_type="application/json")    

        #return HttpResponseRedirect(reverse('lecturedetail_list',kwargs={'slug': subject}))    

def lectureQAForumData(request):
    lectureid = request.GET.get('lectureid')
    data = None
    if(lectureid):
        data = get_qa(lectureid)
    
    return HttpResponse(json.dumps({'data': data}), content_type="application/json")

#This function populates QA forum of the lecture
def get_qa(lectureid):
    lecture = LectureDetail.objects.get(id=lectureid)
    qalist = []
    try:
        question = lecture.questionforum_set.all()
        for q in question:
            #print(q.dict_obj())
            qa = dict(question="", answers=[])
            qa["question"] = q.dict_obj()
            #print("get_qa3")
            answers = q.answerforum_set.all()
            #print("get_qa4")
            for ans in answers:
           #     print(ans.dict_obj())
                qa["answers"].append(ans.dict_obj())
          #  print("get_qa5")
         #   print(qa)
            qalist.append(qa)
        #print("get_qa6")
    except QuestionForum.DoesNotExist:
        print(f"Question for lecture {lecture.title} in section {lecture.section} doesn't exist")
    except AnswerForum.DoesNotExist:
        print("Answers dont exist")
    except:
        raise Http404("Hummm")
    #print("get_qa7")
    json_str = json.dumps(qalist)
    #print("get_qa8")
    #print("QA forum.............")
    #print(json_str)

    return json_str

class QuizCourseListView(ListView):
    template_name = "quizes/quiz_course_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        return Course.objects.all()

class QuizCourseDetailListView(ListView):
    template_name = "quizes/quiz_coursedetail_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get('slug')
        course = Course.objects.get(id=id)
        try:
            return course.coursedetail_set.all()
        except CourseDetail.DoesNotExist:
            raise Http404("Course details don't exist for "+ id)
        except:
            raise Http404("Hummm")

class QuizNamesListView(ListView):
    template_name="quizes/quiz_names_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get('slug')
        coursedetail = CourseDetail.objects.get(id=id)
        try:
            return coursedetail.quiz_set.all()
        except Quiz.DoesNotExist:
            raise Http404(f"Quiz for {coursedetail.subject} doesn't exist")
        except:
            raise Http404("Hummm")

class QuizQuestions(DetailView):
    template_name="quizes/questions.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        context['title'] = "Quiz question"
        return context

    def get_object(self, *args, **kwargs):
        print(self.kwargs)
        quizid = self.kwargs.get('quizid')
        qid   = self.kwargs.get('qid')
        action = self.kwargs.get('action')
        choices = list()
        try:
            quiz = Quiz.objects.get(id=quizid)
            #accessing all the elements is a costly operation
            # for last question id explore cookies and only query once
            question = {}
            question['quizid'] = quizid
                
            q = quiz.quizdetail_set.all()
            last = q.last().id
            first = q.first().id

            if qid == 0:
                qid = first
            if(action == "next"):
                if(qid == last):
                    qid = qid
                else:
                    qid = qid + 1
                if(qid == last):
                    question["next_disable"] = "1"
                else:
                    question["next_disable"] = "0"

            elif(action == 'prev'):
                if(qid == first):
                    qid = first
                else:
                    qid = qid - 1
                if(qid == first):
                    question["prev_disable"] = "1"
                else:
                    question["prev_disable"] = "0"

            obj = quiz.quizdetail_set.get(id=qid)
            question["qid"]      = qid
            question["qno"] = obj.questionNo
            question["question"] = obj.question
            question["mcq"]      = obj.mcq
            for choice in obj.choices.split(";") :
                choices.append({"choice":choice, "answered":False})
        except QuizDetail.DoesNotExist:
            raise Http404(f"Quiz for {quiz.title} doesn't exist")
        except:
            raise Http404("Hummm")

        answers = list()
        try:
            if self.request.user.is_authenticated:
                ansStr = UserAnswer.objects.get(user=self.request.user, qid=qid).answer
                print(f"answers from model: {ansStr}")
                answers = json.loads(ansStr)
        except UserAnswer.DoesNotExist:
            pass    
        except UserAnswer.MultipleObjectsReturned:
            ansStr = UserAnswer.objects.filter(user=self.request.user, qid=qid).first().answer
            answers = json.loads(ansStr)
        # except:
        #     raise Http404("Humm...question is not answered")
        print(f"answers: {answers}")
        for ans in answers:
            choices[int(ans)-1]["answered"] = True
        question["choices"]  = choices
        return question

    def post(self, request, **kwargs):
        print(request.POST)
        if not request.user.is_authenticated:
            print("user is unauthenticated")
            html = "You need to Sign in to submit answers"
            return HttpResponse(html, status=401, reason="login is required")        

        quizid = request.POST.get('quizId')
        qid   =  request.POST.get('questionId')
        quizDetailObj = QuizDetail.objects.get(id=qid)

        try:
            userAns = UserAnswer.objects.get(user=request.user, qid=quizDetailObj)
            print(f"UserAns is found {userAns}")
            userAns.answer = json.dumps(request.POST.getlist('answer'))
            print(f"request.POST.get('answer') {request.POST.getlist('answer')}, userAns.answer {userAns.answer}")
            userAns.pub_date = datetime.now()
            userAns.save()
        except UserAnswer.DoesNotExist:
            print(f"UserAns is newly created")
            userAns = UserAnswer() #model
            userAns.user = request.user
            userAns.qid = quizDetailObj
            userAns.answer =  json.dumps(request.POST.getlist('answer'))
            print(f"request.POST.get('answer') {request.POST.getlist('answer')}, userAns.answer {userAns.answer}")
            userAns.pub_date =  datetime.now()
            userAns.save()
            
        #logic for updating userQuiz
        quizObj = userAns.qid.quiz
        try:
            userQuiz = UserQuiz.objects.get(user=request.user, quiz=quizObj)
            userQuiz.lastAccessed = datetime.now()
            userQuiz.save()  
        except UserQuiz.DoesNotExist:
            userQuiz = UserQuiz()
            userQuiz.user = request.user
            userQuiz.quiz = quizObj
            userQuiz.competionStatus = UserQuiz.COMPLETIONSTATUS_ATTEMPTED
            userQuiz.lastAccessed = datetime.now()
            userQuiz.save()

        #todo this is performance killer to check eachtime if the qid is lastid or not
        if( int(qid) == QuizDetail.objects.filter(quiz=Quiz.objects.get(id=quizid)).last().id):
            return HttpResponseRedirect(reverse('quiz_result', kwargs={'quizid':quizid})) 
        else:
            return HttpResponseRedirect(reverse('quiz_questions', kwargs={'quizid':quizid, 'qid':qid,'action':'next'}))
            
class QuizResult(LoginRequiredMixin, DetailView):
    login_url = '/login'
    template_name="quizes/result.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        context['title'] = "Quiz result"
        return context

    def get_object(self, *args, **kwargs):
        quizid = self.kwargs.get('quizid')
        print("prepareResult============")
        quiz=Quiz.objects.get(id=quizid)
        try:
            userQuiz = UserQuiz.objects.get(user=self.request.user, quiz=quiz)
            userQuiz.competionStatus = UserQuiz.COMPLETIONSTATUS_COMPLETED
            userQuiz.save()
        except UserQuiz.DoesNotExist:
            raise Http404("User has not answered the quiz yet!")

        questions = QuizDetail.objects.filter(quiz=quiz)
        quiz.totalQuestion = questions.count()
        quiz.save()
        print("pr0")
        quizResult = dict(name=quiz.title,
                        totalQuestions=quiz.totalQuestion,
                        correctAnswers=0,
                        questionDetail=list())
        for question in questions:
            try:
                ans = UserAnswer.objects.get(user=self.request.user, qid=question)
            except UserAnswer.DoesNotExist:
                continue
            singleResult = dict()
            print("pr1")
            singleResult['question'] = question.question
            singleResult['qno'] = question.questionNo
            singleResult['mcq'] = question.mcq
            singleResult['choices'] = list()
            singleResult['isCorrectAns'] = True
            print("pr2")
            choices = question.choices.split(';')
            print("pr3")
            expectedAns = sorted(question.answer.split(';'))
            print("pr4")
            for choice in choices:
                singleResult['choices'].append(dict(choice=choice, actual=False, expected=False))

            actualAns = json.loads(ans.answer)
            print(f"actualAns: {actualAns} ans.answer {ans.answer}")
            print(f"pr5 len(expectedAns) {len(expectedAns)} len(actualAns) {len(actualAns)}")
            i=0
            while( i < len(expectedAns) and i < len(actualAns)):
                print(f"pr6  {i} {int(expectedAns[i])-1} {int(actualAns[i])-1}")
                singleResult['choices'][int(expectedAns[i])-1]['expected'] = True
                print("pr6.1")
                singleResult['choices'][int(actualAns[i])-1]['actual'] = True
                print("pr6.2")
                if(expectedAns[i] != actualAns[i]):
                    print("pr6.3")
                    singleResult['isCorrectAns'] = False
                print("pr6.4")
                i+=1

            while(i < len(expectedAns)):
                singleResult['choices'][int(expectedAns[i])-1]['expected'] = True
                singleResult['isCorrectAns'] = False
                print("pr7")
                i+=1

            while(i < len(actualAns)):
                singleResult['choices'][int(actualAns[i])-1]['actual'] = True
                singleResult['isCorrectAns'] = False
                print("pr8")
                i+=1

            if(singleResult['isCorrectAns']):
                quizResult['correctAnswers'] +=1
            quizResult['questionDetail'].append(singleResult)    

        print("quiz result ==================================")
        print(quizResult)
        return quizResult

class QuizAttemptedListView(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name="quizes/quiz_completed_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        context['title'] = "My quizes"
        return context

    def get_queryset(self, *args, **kwargs):
        try:
            return UserQuiz.objects.filter(user=self.request.user)
        except UserQuiz.DoesNotExist:
            raise Http404(f"Quiz for {coursedetail.subject} doesn't exist")
        except:
            raise Http404("Hummm")



#TODO yet to be implemented
class QAForumListView(ListView):
    template_name="quizes/qaforum_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        return context

    def get_queryset(self, *args, **kwargs):
        lectureid = self.kwargs.get('slug')
        lecture = LectureDetail.objects.get(id=lectureid)
        qa = { 'question': "", 'answers':[] }
  
        try:
            question = lecture.questionforum_set.all()
            for q in question:
                qa["question"] = q
                answers = q.answerforum_set.all()
                qa["answers"] = answers
        except QuestionForum.DoesNotExist:
            raise Http404(f"Question for lecture {lecture.title} in section {lecture.section} doesn't exist")
        except AnswerForum.DoesNotExist:
            print("Answers dont exist")
        except:
            raise Http404("Hummm")
        return qa


class CourseStudingListView(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name="courses/courses_studing_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_name'] = settings.brand_name
        context['title'] = "My courses"
        return context

    def get_queryset(self, *args, **kwargs):
        try:
            myCourses = UserCourse.objects.filter(user=self.request.user)
            return myCourses
        except:
           raise Http404("Hummm")
