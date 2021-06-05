from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Question, Choice, Comment
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count


@csrf_exempt
def vote(request):
    choiceid = int(request.POST['id'])
    try:
        error = 0
        question_id = Choice.objects.filter(id=choiceid)[0].question_id
        if Comment.objects.filter(user_id=request.user.id,  question_id=question_id).count() != 0:
            error = 1
        elif request.user.is_authenticated == False:
            error = 2
        elif request.user.activate_status == False:
            error = 3
        else:
            selected_choice = list(set(list(Choice.objects.filter(pk=choiceid).values_list('question', flat=True))))
            Comment.objects.create(user_id=request.user.id, choice_id=choiceid, question_id=selected_choice[0])
        comment_count = 1
        user_choice_selected = ''
        survey_choices = Choice.objects.filter(question__is_published=True)
        choices_question = []
        if survey_choices.count() != 0:
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

        if request.is_ajax():
            msg = ''
            if error == 1:
                msg = 'قبلا در نظر سنجی شرکت کرده اید.'
            if error == 2:
                msg = 'برای شرکت در نظر سنجی در سایت ثبت نام کنید.'
            if error == 3:
                msg = 'اکانت شما غیر فعال می باشد.'
            context = { 'choices_question': choices_question, 'comment_count': comment_count, 'user_choice_selected': user_choice_selected, 'msg': msg, }
            html = render_to_string('site_pages/load_pages/survey_form.html', context, request=request)
            return HttpResponse(html)
    except:
        pass
