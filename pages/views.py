from django.shortcuts import render,redirect
from news.models import News
from competition.models import Gallery, User_In_Competition, Honors,Honors_Files
from django.db import connection
import traceback
from django.views.decorators.csrf import csrf_exempt
from .models import Company_Info
from django.template.loader import render_to_string
from django.http import HttpResponse
from polls.models import Question, Choice, Comment
from django.db.models import Count
from competition_project.choices import Honors_Grade


def index(request):
    news_list = News.objects.order_by('id').filter(is_published=True)[0:10]
    gallery_list = Gallery.objects.order_by('id').filter(is_published=True)[0:6]
    company_Info = Company_Info.objects.all()
    if company_Info.count() == 0:
        obj = {'company_name': '', 'manager_name': '', 'phone': '', 'fax': '', 'address': '', 'banner_img': '', 'about': ''}
    else:
        obj = company_Info[0]

    users_ranks_in_cmp = []
    # try:
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT A.uid_id,SUM(B.point),(array_agg(distinct D.first_name))[1] firstname,(array_agg(distinct D.last_name))[1] lastname,(array_agg(distinct E.gender))[1] gender,(array_agg(distinct E.personal_image))[1] personal_image FROM  competition_user_in_competition A  INNER JOIN competition_rank_detail AS B ON A.place_id_id = B.id  INNER JOIN competition_competition C  ON A.cid_id = C.id INNER JOIN auth_user D ON A.uid_id = D.id INNER JOIN account_profile E ON A.uid_id = E.user_id where B.point!=0 and A.status=true and A.reject_status=false and  E.gender =0 GROUP BY  A.uid_id;")
    #     columns = [column[0] for column in cursor.description]  # find key  of cursor
    #     for row in cursor.fetchall():
    #         users_ranks_in_cmp.append(dict(zip(columns, row)))
    # except:
    #     print(traceback.format_exc())
    #     pass
    # finally:
    # connection.close()
    # context = {'news_list':news_list,'gallery_list':gallery_list,'users_ranks_in_cmp':users_ranks_in_cmp,'company_info':obj}

    selected_news = News.objects.order_by('-pk').filter(category_id=1, is_published=True)
    if selected_news.count() != 0:
        selected_news = selected_news[0]
    else:
        selected_news = ''
    comment_count = 1
    user_choice_selected = ''
    question = ''
    survey_choices = Choice.objects.filter(question__is_published=True)
    choices_question = []
    if survey_choices.count() != 0:
        question = survey_choices[0].question
        question_id = survey_choices[0].question_id
        comment = Comment.objects.filter(question_id=question_id)
        survey_choices = survey_choices.values('choice_text', 'id')

        choices_question = []
        for i in survey_choices:
            choices_question.append({'choice_text': i['choice_text'], 'choice_id': i['id'], 'comment': 0})
        if comment.count() != 0:
            user_choice_selected = comment.filter(user_id=request.user.id)
            if user_choice_selected.count() != 0:
                user_choice_selected = user_choice_selected[0]
            comment_count = comment.count()
            choices_count = comment.values('choice_id').annotate(dcount=Count('choice_id')).values('choice_id', 'dcount')
            for index, i in enumerate(choices_question):
                for j in choices_count:
                    if i['choice_id'] == j['choice_id']:
                        choices_question[index].update({'choice_text': i['choice_text'], 'choice_id': i['choice_id'], 'comment': j['dcount']})
    honors = Honors.objects.order_by('-pk').filter(is_published=True)[0:9]
    context = {'news_list': news_list, 'gallery_list': gallery_list, 'company_info': obj, 'choices_question': choices_question, 'question': question,
               'user_choice_selected': user_choice_selected,
               'comment_count': comment_count, 'selected_news': selected_news, 'honors_list': honors, 'grades': Honors_Grade}
    return render(request, 'site_pages/pages/index.html', context)


def about(request):
    company_Info = Company_Info.objects.all()
    if company_Info.count() == 0:
        obj = ''
    else:
        obj = company_Info[0].about
    return render(request, 'site_pages/pages/about.html', {'about': obj})


def contact(request):
    company_Info = Company_Info.objects.all()
    if company_Info.count() == 0:
        obj = {'phone': '', 'fax': '', 'address': ''}
    else:
        obj = company_Info[0]

    return render(request, 'site_pages/pages/contact_us.html', {'info': obj})


def honors_list(request):
    honors = Honors.objects.order_by('-pk').filter(is_published=True)
    cat = request.GET.get('cat', None)
    if not (cat == None or cat == ''):
        honors = honors.filter(grade__iexact=cat)

    context = {'honors_list': honors, 'grades': Honors_Grade, 'selected_cat': cat}
    return render(request, 'site_pages/honors/honors_list.html', context)

def honors_detail(request, honors_id):
    try:
        honors_files = Honors_Files.objects.filter(honors_id=honors_id,honors_id__is_published=True)
        context = {
            'honors_files': honors_files
        }
        return render(request, 'site_pages/honors/honors_detail.html', context)
    except:
        return redirect('pages:honors_list')


@csrf_exempt
def filter_gender(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        gender = request.POST['id']
        if gender == '1':
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT A.uid_id,SUM(B.point),(array_agg(distinct D.first_name))[1] firstname,(array_agg(distinct D.last_name))[1] lastname,(array_agg(distinct E.gender))[1] gender,(array_agg(distinct E.personal_image))[1] personal_image FROM  competition_user_in_competition A  INNER JOIN competition_rank_detail AS B ON A.place_id_id = B.id  INNER JOIN competition_competition C  ON A.cid_id = C.id INNER JOIN auth_user D ON A.uid_id = D.id INNER JOIN account_profile E ON A.uid_id = E.user_id where B.point!=0 and A.status=true and A.reject_status=false and  E.gender =0 GROUP BY  A.uid_id;")
                columns = [column[0] for column in cursor.description]  # find key  of cursor
                users_ranks_in_cmp = []
                for row in cursor.fetchall():
                    users_ranks_in_cmp.append(dict(zip(columns, row)))
            except:
                print(traceback.format_exc())
                pass
            finally:
                connection.close()
        else:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT A.uid_id,SUM(B.point),(array_agg(distinct D.first_name))[1] firstname,(array_agg(distinct D.last_name))[1] lastname,(array_agg(distinct E.gender))[1] gender,(array_agg(distinct E.personal_image))[1] personal_image FROM  competition_user_in_competition A  INNER JOIN competition_rank_detail AS B ON A.place_id_id = B.id  INNER JOIN competition_competition C  ON A.cid_id = C.id INNER JOIN auth_user D ON A.uid_id = D.id INNER JOIN account_profile E ON A.uid_id = E.user_id where B.point!=0 and A.status=true and A.reject_status=false and  E.gender =1 GROUP BY  A.uid_id;")
                columns = [column[0] for column in cursor.description]  # find key  of cursor
                users_ranks_in_cmp = []
                for row in cursor.fetchall():
                    users_ranks_in_cmp.append(dict(zip(columns, row)))
            except:
                print(traceback.format_exc())
                pass
            finally:
                connection.close()

        if request.is_ajax():
            context = {'users_ranks_in_cmp': users_ranks_in_cmp}
            html = render_to_string('site_pages/pages/load_gender.html', context)
            return HttpResponse(html)
    else:
        pass
