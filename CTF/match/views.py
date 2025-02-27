#ecoding=utf-8
import datetime

from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
import json
from .tool import *
from tool import models
def map_tools(x):
    x.create_time = x.create_time.strftime("%Y-%m-%d %H:%M:%S")
    # x.apply_start_time= x.apply_start_time.strftime("%Y-%m-%d %H:%M:%S")
    # x.apply_end_time= x.apply_end_time.strftime("%Y-%m-%d %H:%M:%S")
    # x.answer_start_time= x.answer_start_time.strftime("%Y-%m-%d %H:%M:%S")
    # x.answer_end_time= x.answer_end_time.strftime("%Y-%m-%d %H:%M:%S")

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def re_megagame_intro(request):

    temp = models.MatchInfo.objects.filter().all()
    return render(request, 'megagame_intro.html', {'megagame_list': temp})


def re_megagame_detail(request):
    user_uid = request.GET.get('user_uid')
    if not user_uid:
        user_uid == '11fafawf'
    id = request.GET.get('id')
    temp = models.MatchInfo.objects.filter(id=id).first()
    person1 = PersonMegagame(user_uid)
    state = 1  #person1.re_state(megagame_id)
    if state:
        return render(request, 'mega_detail.html', {
            'state': '已参赛',
            'megagame_detail': temp
        })
    else:
        return render(request, 'mega_detail.html', {
            'state': '我要参加',
            'megagame_detail': temp
        })


def re_join_megagame(request):
    if request.method == 'POST':
        temp = request.POST
        uid = temp.get('uid')
        user_ID = temp.get('user_ID')
        if not user_ID:
            dict = {'code': -1, 'msg': '请登录'}
            return HttpResponse(json.dumps(dict))
        name = temp.get('name')
        person1 = PersonMegagame(user_ID)
        state = person1.join_megagame(name, uid)
        print state
        if state:
            dict = {'code': 200, 'msg': '参加成功', 'uid': uid}
        else:
            dict = {'code': -100, 'msg': '参加失败', 'uid': uid}
        return HttpResponse(json.dumps(dict))


def re_operation(request):
    if request.method == "GET":
        uid = request.GET.get("contest_id")
        user_ID = request.GET.get("user_ID")
        print uid
        question_temp = models.MatchInfo.objects.filter(
            uid=uid, type__gt=1).order_by('id')
        paginator = Paginator(question_temp, 20)
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page',1)
        try:
            question_list = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            question_list = paginator.page(1)
        except InvalidPage:
            # 如果请求的页数不存在, 重定向页面
            return HttpResponse('找不到页面的内容')
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            question_list = paginator.page(paginator.num_pages)
        return render(
            request, 'megagame_list.html', {
                'question_list': question_list,
                'page': page,
                'num_pages': paginator.num_pages,
                'uid': uid,
                'user_ID': user_ID
            })


def re_competition(request):
    if request.method == 'GET':
        qid = request.GET.get('qid')
        uid = request.GET.get('uid')
        query = models.Challenge.objects.filter(qid=qid, uid=uid)
        render(request, 'megagame_competition.html', {'question': query})


def re_megagame_choice(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        query = models.Challenge.objects.filter(uid=uid, type__lt=2)
        strquery = json.dumps(list(query.values()),
                              ensure_ascii=False,
                              cls=DateEncoder)
        return render(request, 'megagame_choice.html', {
            'list': strquery,
            'question_list': query
        })
    if request.method == 'POST':
        return render(request, 'megagame_list.html')


def re_megagame_questions_detail(request):
    if request.method == 'GET':
        qid = request.GET.get('qid')
        print '------------->', qid
        query = models.Challenge.objects.filter(qid=qid)
        if query:
            return render(request, 'megagame_questions_detail.html',
                          {'question': query[0]})
    if request.method == 'POST':
        return render(request, 'megagame_list.html')


def re_megagame_questions_list(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        type = request.GET.get('type')
        print uid, type, '-----------'
        query = models.Challenge.objects.filter(uid=uid, type=type)
        return render(request, 'megagame_question_list.html',
                      {'questions_list': query})
    if request.method == 'POST':
        return render(request, 'megagame_list.html')


def re_megagame_operator_check(request):
    if request.method == 'POST':
        print request.POST
        qid = request.POST.get('qid')
        user_ID = '888-8-8+88'
        uid = request.POST.get('uid')
        answer = request.POST.get('answer')
        query = models.Challenge.objects.filter(qid=qid).first()
        if answer == query.correction:
            dict = {
                'code': 200,
                'AnswerIsRight': 'true',
            }
            query1 = models.Answer.objects.filter(qid=qid, user_ID=user_ID)
            if not query1.exists():
                query2 = models.Members.objects.filter(user_ID=user_ID).first()
                reply_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.localtime(time.time()))
                answer = models.Answer(qid=qid,
                                       user_answer=answer,
                                       user_ID=user_ID,
                                       reply_time=reply_time)
                answer.member_id = query2.id
                answer.member.user_score = query.q_score + answer.member.user_score
                answer.save()
                answer.member.save()
        else:
            dict = {
                'code': 200,
                'AnswerIsRight': 'false',
            }
        return HttpResponse(json.dumps(dict))


def re_megagame_choice_check(request):
    if request.method == 'POST':
        answers = json.loads(request.body).get("answers", [])
        print answers
        user_ID = '888-8-8+88'
        for question in answers:
            answer = question.get("answer")
            qid = question.get("qid")
            query = models.Challenge.objects.filter(qid=qid).first()
            if answer == query.correction:
                query1 = models.Answer.objects.filter(qid=qid, user_ID=user_ID)
                if not query1.exists():
                    query2 = models.Members.objects.filter(
                        user_ID=user_ID).first()
                    reply_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime(time.time()))
                    answer = models.Answer(qid=qid,
                                           user_answer=answer,
                                           user_ID=user_ID,
                                           reply_time=reply_time)
                    answer.member_id = query2.id
                    answer.member.user_score = query.q_score + answer.member.user_score
                    answer.save()
                    answer.member.save()


        else:
            dict = {
                'code': 200,
                'AnswerIsRight': 'True',
            }
        return HttpResponse(json.dumps(dict))


def re_megagame_ctf2018(request):
    return render(request, 'ctf2018.html')


def m_session(request):
    return render(request,"match/session.html")

def m_login(request):
    if request.method == "GET":
        id=request.GET.get("id")
        return render(request,"match/m_login.html",{'id':id})

def m_match(request):
    temp = models.MatchInfo.objects.filter().order_by("-id")
    if temp:
        map(map_tools, temp)
    return render(request, "match/m_match.html", {'match_list': temp})

def m_ctf(request):
    if request.method == "GET":
        id = request.GET.get("id")
        temp= models.MatchInfo.objects.filter(id=id).first()
        return render(request,"match/m_ctf.html",{"match":temp})

def challenge_list(request):
    if request.method == "GET":
        id = request.GET.get("id")
        temp= models.Challenge.objects.filter(match_id=id)
        match = models.MatchInfo.objects.filter(id=id).first()
        return render(request,"match/challenge_list.html",{"challenge":temp,"match":match})

def oapi(request):
    return


def xctf(request):
    return render(request, 'match/xctf.html')

def auth_user(request):
    data={"success": True, "message": {"user": {"logo": "/media/uploads/assets/img/def_icon.jpg", "username": "cy123456", "id": 49347, "short_introduce": "", "level": {"level_zh": "\u65b0\u624b", "level_en": "Novice"}, "point": 0, "coin": 0, "nickname": "cy123456"}}}
    return HttpResponse(json.dumps(data))

def auth_login(request):
    data={}
    return HttpResponse(json.dumps(data))