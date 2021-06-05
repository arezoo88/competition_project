from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Competition, Gallery, Weight_Classification, User_In_Competition, Rank_Detail
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from competition_project import jalali
from django.template.loader import render_to_string
from django.contrib.auth.decorators import user_passes_test
from account.models import User
import base64
from competition_project.choices import  Age_Period


def competition_list(request):
    try:
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
        date_new = date_to_shamsi.split('-')
        month = date_new[1]
        day = date_new[2]
        if len(month) == 1: month = '0' + month
        if len(day) == 1: day = '0' + day
        date_to_shamsi = str(date_new[0]) + '/' + str(month) + '/' + str(day)
        cursor = connection.cursor()
        cursor.execute("select cmp_id, (array_agg(distinct title))[1] title,(array_agg(distinct poster_image))[1] AS image,array_agg(distinct register_from) register_from,array_agg(distinct register_to) register_to,array_agg(distinct subtitle order by subtitle desc) ages, array_agg(distinct gender order by gender desc) genders from competition_competition where is_published = True AND register_to >= '%s'  group by cmp_id" % date_to_shamsi)
        columns = [column[0] for column in cursor.description]  # find key  of cursor
        records = []
        for row in cursor.fetchall():
            records.append(dict(zip(columns, row)))
    except:
        import traceback
        print(traceback.format_exc())
        records = []
    finally:
        connection.close()

    return render(request, 'site_pages/competition/competition_list.html', {'competition_list': records})


def gallery_list(request):
    gallery = Gallery.objects.all().filter(is_published=True)
    context = {'gallery': gallery}
    return render(request, 'site_pages/gallery/gallery_list.html', context)


@csrf_exempt
def filter_competition_list(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        if request.method == 'POST':
            gender = request.POST['gender']
            age = request.POST['age']
            if gender == '' or gender not in ['0', '1']:
                gender = [0, 1]
            else:
                gender = [int(gender)]
            if age == '' or age not in ['0', '1', '2', '3']:
                age = [0, 1, 2, 3]
            else:
                age = [int(age)]
            year = datetime.now().year
            month = datetime.now().month
            day = datetime.now().day
            date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
            date_new = date_to_shamsi.split('-')
            month = date_new[1]
            day = date_new[2]
            if len(month) == 1: month = '0' + month
            if len(day) == 1: day = '0' + day
            date_to_shamsi = str(date_new[0]) + '/' + str(month) + '/' + str(day)
            competition_list = Competition.objects.filter(gender__in=gender, subtitle__in=age, register_to__gte=date_to_shamsi)
            if request.is_ajax():
                html = render_to_string('site_pages/competition/dynamic_data.html', {'result': competition_list})
                return HttpResponse(html)
    else:
        return redirect('competition:competition_list')


def check_condition_for_register(user):
    if user.is_authenticated:
        if user.is_staff == False:  # agar admin bashe ejaze nadare varede marhale sabtenam beshe
            profile_info = Profile.objects.get(user_id=user.id)
            if profile_info.user.first_name != '' and profile_info.user.last_name != '' and profile_info.birth_date != '' and profile_info.national_code != '' and profile_info.qform_document != '' and profile_info.national_document_image != '':
                return True


@csrf_exempt
def register(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        if request.user.is_authenticated:
            if request.user.is_staff == False:

                try:
                    id = int(request.POST['id'])
                except:
                    return JsonResponse({'error': 'با خطا مواجه شدید.'})
                try:
                    cmp_id = int(request.POST['cmp_id'])
                except:
                    return JsonResponse({'error': 'با خطا مواجه شدید.'})
                try:
                    age = int(request.POST['age'])
                except:
                    return JsonResponse({'error': 'با خطا مواجه شدید.'})
                if id == 0:
                    gender = request.POST.getlist('gender[]')
                else:
                    gender = [str(request.POST['gender'])]

                profile = Profile.objects.get(user_id=request.user.id)
                if profile.user.first_name == '' or profile.user.last_name == '' or profile.birth_date == '' or profile.national_code == '' or profile.qform_document == '' or profile.national_document_image == '':
                    return JsonResponse({'error': 'اطلاعات پروفایل خود را تکمیل کنید.'})

                if str(profile.gender) not in gender:
                    return JsonResponse({'error': 'جنسیت شما با شرایط مسابقه مطابقت ندارد.'})

                id_ = base64.b64encode(bytes(str(str(id) + '-' + str(cmp_id) + '-' + str(age) + '-' + str(gender)), "utf-8"))
                id_ = id_.decode("utf-8")

                url = '/competition/register/register_in_competition/' + id_
                return JsonResponse({'code': 100, 'url': url})

            else:
                return JsonResponse({'error': 'ابتدا در سایت ثبت نام کنید.'})
        else:
            return JsonResponse({'error': 'ابتدا در سایت ثبت نام کنید.'})

    else:
        return redirect('competition:competition_list')


@user_passes_test(check_condition_for_register, login_url='/competition/competition_list')
def register_in_competition(request, cmpt_id):
    try:
        cmp_id_decode = base64.b64decode(cmpt_id).decode()
        cmp_id_decode = cmp_id_decode.split('-')
        gender = eval(cmp_id_decode[3])
        profile_info = Profile.objects.get(user_id=request.user.id)
        if profile_info.user.first_name == '' or profile_info.user.last_name == '' or profile_info.birth_date == '' or profile_info.national_code == '' or profile_info.qform_document == '' or profile_info.national_document_image == '':
            return redirect('account:dashboard')
        if str(profile_info.gender) not in gender:
            return redirect('competition:competition_list')

        id = int(cmp_id_decode[0])
        cmpid = int(cmp_id_decode[1])
        age = int(cmp_id_decode[2])
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
        date_new = date_to_shamsi.split('-')
        month = date_new[1]
        day = date_new[2]
        if len(month) == 1: month = '0' + month
        if len(day) == 1: day = '0' + day
        date_to_shamsi = str(date_new[0]) + '/' + str(month) + '/' + str(day)

        cursor = connection.cursor()
        if id == 0:  # yani kolle mosabeghe biad
            cursor.execute("select cmp_id, (array_agg(distinct title))[1] title,(array_agg(distinct poster_image))[1] AS image,array_agg(distinct user_from_birtday) user_from_birtday,array_agg(distinct user_to_birthday) user_to_birthday,array_agg(distinct subtitle order by subtitle desc) ages,array_agg(distinct weight_id ) weight_id, array_agg(distinct gender order by gender desc) genders from competition_competition where is_published = True AND register_to >= '%s' AND  cmp_id= '%d' AND subtitle='%d'  group by cmp_id" % (date_to_shamsi, cmpid, age))
        else:
            cursor.execute("select cmp_id, (array_agg(distinct title))[1] title,(array_agg(distinct poster_image))[1] AS image,array_agg(distinct user_from_birtday) user_from_birtday,array_agg(distinct user_to_birthday) user_to_birthday,array_agg(distinct subtitle order by subtitle desc) ages,array_agg(distinct weight_id ) weight_id, array_agg(distinct gender order by gender desc) genders from competition_competition where is_published = True AND register_to >= '%s' AND id = '%d' AND  cmp_id= '%d' AND subtitle='%d'   group by cmp_id " % (date_to_shamsi, id, cmpid, age))

        columns = [column[0] for column in cursor.description]  # find key  of cursor
        records = []
        for row in cursor.fetchall():
            records.append(dict(zip(columns, row)))
        weight_classification = Weight_Classification.objects.all()
    except:
        return redirect('competition:competition_list')
    context = {'profile_info': profile_info, 'cmp_info': records, 'weight_classification': weight_classification, 'age_period': Age_Period}

    return render(request, 'site_pages/competition/register_in_competition.html', context)


@csrf_exempt
def final_register(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):

        if request.user.is_authenticated:

            if request.user.is_staff == False:

                try:
                    profile = Profile.objects.get(user_id=request.user.id)

                    if profile.user.first_name == '' or profile.user.last_name == '' or profile.birth_date == '' or profile.national_code == '' or profile.qform_document == '' or profile.national_document_image == '':
                        return JsonResponse({'error': 'اطلاعات پروفایل خود را تکمیل کنید.'})

                    weight = request.POST['user_weight_cat']
                    gender = request.POST['gender']
                    subtitle = request.POST['user_age_cat']
                    cmp_id = request.POST['cmp']

                    try:
                        user_img = request.FILES['user_img']
                        if str(user_img.content_type).startswith('image'):
                            if user_img.size < 5000000:
                                pass
                            else:
                                return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از 5 مگابایت باشد.'})

                        else:
                            return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})
                    except:
                        user_img = ''

                    subtitle_split = subtitle.split('_')
                    sub_title = subtitle_split[0]

                    if user_img == '':
                        user_img = profile.personal_image
                        if user_img == '':
                            return JsonResponse({'error': 'انتخاب عکس برای شرکت در مسابقه الزامی است.'})

                    try:
                        cmp_info = Competition.objects.get(cmp_id=cmp_id, subtitle=int(sub_title), gender=int(gender), weight_id=int(weight))
                    except Competition.DoesNotExist:
                        cmp_info = None

                    if cmp_info is None:
                        return JsonResponse({'error': 'با خطا مواجه شدید.'})
                    birthday_from = cmp_info.user_from_birtday
                    birthday_to = cmp_info.user_to_birthday

                    if profile.gender != cmp_info.gender:
                        return JsonResponse({'error': 'جنسیت شما با شرایط مسابقه مطابقت ندارد.'})

                    if cmp_info.capacity != '':
                        capacity = cmp_info.capacity
                        print(333, capacity)
                        try:
                            user_in_cmp_registerd = User_In_Competition.objects.filter(reject_status=False, cid_id=cmp_info.id)
                        except User_In_Competition.DoesNotExist:
                            user_in_cmp_registerd = None
                        error = 0

                        print(67867878, profile.birth_date)

                        if birthday_from != '':
                            if profile.birth_date < birthday_from:
                                return JsonResponse({'error': 'تاریخ تولد شما با شرایط مسابقه مطابقت ندارد.'})

                        if birthday_to != '':
                            if profile.birth_date > birthday_to:
                                return JsonResponse({'error': 'تاریخ تولد شما با شرایط مسابقه مطابقت ندارد.'})

                        try:
                            check_user_in_cmp_group = User_In_Competition.objects.filter(cid_id__cmp_id=cmp_info.cmp_id, uid_id=request.user.id)
                        except User_In_Competition.DoesNotExist:
                            check_user_in_cmp_group = None
                        if check_user_in_cmp_group != None and len(check_user_in_cmp_group) != 0:
                            error = 1
                        if error == 1:
                            return JsonResponse({'error': 'شما قبلا در این گروه مسابقه ثبت نام کرده اید.'})

                        if user_in_cmp_registerd != None and len(user_in_cmp_registerd) != 0:
                            if capacity != '':
                                remaind_capacity = int(capacity) - len(user_in_cmp_registerd)
                                if remaind_capacity == 0:
                                    return JsonResponse({'error': 'ظرفیت شرکت در مسابقه تکمیل شده است.'})

                    rank_info = Rank_Detail.objects.get(place=0, point=0)
                    user_in_cmp = User_In_Competition(uid=profile, image=user_img, cid=cmp_info, place_id=rank_info)
                    user_in_cmp.save()
                    return JsonResponse({'code': 100, 'result': 'ثبت نام با موفقیت انجام شد.'})


                except:
                    pass


            else:
                return JsonResponse({'error': 'ابتدا در سایت ثبت نام کنید.'})
        else:
            return JsonResponse({'error': 'ابتدا در سایت ثبت نام کنید.'})

    else:
        return redirect('competition:competition_list')




def ranking_list(request):
    users_ranks_in_cmp = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT A.uid_id,SUM(B.point),(array_agg(distinct D.first_name))[1] firstname,(array_agg(distinct D.last_name))[1] lastname,(array_agg(distinct E.gender))[1] gender,(array_agg(distinct E.personal_image))[1] personal_image FROM  competition_user_in_competition A  INNER JOIN competition_rank_detail AS B ON A.place_id_id = B.id  INNER JOIN competition_competition C  ON A.cid_id = C.id INNER JOIN auth_user D ON A.uid_id = D.id INNER JOIN account_profile E ON A.uid_id = E.user_id where B.point!=0 and A.status=true and A.reject_status=false  GROUP BY  A.uid_id;")
        columns = [column[0] for column in cursor.description]  # find key  of cursor
        for row in cursor.fetchall():
            users_ranks_in_cmp.append(dict(zip(columns, row)))
    except:
        pass
    finally:
        connection.close()
    return render(request, 'site_pages/competition/ranking_list.html', {'users_ranks_in_cmp': users_ranks_in_cmp})