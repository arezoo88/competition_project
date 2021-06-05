from django.shortcuts import render, redirect, get_object_or_404
from news.models import News, Category_News
from competition.models import Gallery, Weight_Classification, Competition, User_In_Competition, Rank_Detail, Honors, Honors_Files

from polls.models import Question, Choice
from account.models import Profile_Judo, Profile_Jujitso
from competition_project import jalali
from django.contrib.auth import get_user_model
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from competition_project.choices import Genders, Positions, Age_Period, Genders_in_Cmp,Honors_Grade
import re
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from django.contrib import auth
import traceback
from django.db import connection
from pages.models import Company_Info
from django.template.loader import render_to_string
from django.http import HttpResponse
from news.forms import NewsForm
from django.db.models import Q


def check_staff(user):
    if user.is_staff:
        return True
    return False


# ------------------PROFILE METHODS-------------


@user_passes_test(check_staff, login_url='/')
def panel(request):
    try:
        User = get_user_model()
        news = News.objects.order_by('-id')[:10]
        profile_info = User.objects.get(pk=request.user.id)
        cursor = connection.cursor()
        cursor.execute(
            'select cmp_id AS id,(array_agg(distinct title))[1] title,(array_agg(distinct competition_date))[1] competition_date,(array_agg(distinct create_date))[1] create_date,(array_agg(distinct is_published))[1] is_published from competition_competition group by cmp_id order by create_date desc LIMIT 10;')
        columns = [column[0] for column in cursor.description]  # find key  of cursor

        competition_list = []
        for row in cursor.fetchall():
            competition_list.append(dict(zip(columns, row)))
        context = {'news_list': news, 'profile_info': profile_info, 'competition_list': competition_list}
        return render(request, 'admin_panel_pages/panel_dashboard.html', context)
    except:
        return redirect('panel:panel_dashboard')
    finally:
        connection.close()


@user_passes_test(check_staff, login_url='/')
def panel_profile(request):
    User = get_user_model()
    profile_info = User.objects.get(pk=request.user.id)
    context = {'profile_info': profile_info, 'genders': Genders}
    return render(request, 'admin_panel_pages/panel_profile.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_profile_edit(request):
    User = get_user_model()
    profile_info = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        if first_name == '':
            return JsonResponse({'error': 'فیلد نام را تکمیل نمائید.'})
        if last_name == '':
            return JsonResponse({'error': 'فیلد نام خانوادگی را تکمیل نمائید.'})
        gender = request.POST['gender']
        if gender not in ["1", "0"]:
            gender = 0
        birth_date = request.POST['birth_date']
        mobile_number = request.POST['mobile']
        postal_code = request.POST['postal_code']
        email = request.POST['email']
        address = request.POST['address']
        if email != '':
            try:
                validate_email(email)
                valid_email = True
            except:
                valid_email = False
            if valid_email == False:
                return JsonResponse({'error': 'ایمیل معتبر وارد کنید.'})

        rule = re.compile(r'([12]\d{3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01]))')
        validate_date = rule.search(birth_date)

        if birth_date != '' and validate_date == None:
            return JsonResponse({'error': 'تاریخ تولد را از تقویم انتخاب کنید.'})

        personal_image = ''
        try:
            personal_image = request.FILES['admin_img']
            if str(personal_image.content_type).startswith('image'):
                if personal_image.size < 5000000:
                    pass
                else:

                    return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

        except:
            pass
        if personal_image != '':
            profile_info.personal_image.delete()
            profile_info.personal_image = personal_image
        profile_info.first_name = first_name
        profile_info.last_name = last_name
        profile_info.email = email
        profile_info.gender = gender
        profile_info.phone = mobile_number
        profile_info.birth_date = birth_date
        profile_info.postal_code = postal_code
        profile_info.address = address
        profile_info.save()
        return JsonResponse({'code': 100, 'url': '/panel/panel_profile'})
    else:
        context = {'profile_info': profile_info, 'genders': Genders, 'positions': Positions}
        return render(request, 'admin_panel_pages/panel_profile_edit.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_profile_change_pass(request):
    User = get_user_model()
    if request.method == 'POST':
        password_old = request.POST['passwordold']
        password = request.POST['password']
        passwordrepeat = request.POST['passwordrepeat']
        if len(password) < 6:
            return JsonResponse({'error': 'طول پسورد حداقل باید ۶ کاراکتر باشد.'})
        if len(password) > 20:
            return JsonResponse({'error': 'طول پسورد حداکثر باید 20 کاراکتر باشد.'})
        if password == '' or passwordrepeat == '' or password_old == '':
            return JsonResponse({'error': 'همه فیلد ها را پر کنید.'})

        user = User.objects.get(pk=request.user.id)
        if user.check_password(password_old) == False:
            return JsonResponse({'error': 'پسورد قبلی خود را اشتباه وارد کرده اید.'})
        else:
            if password != passwordrepeat:
                return JsonResponse({'error': 'پسوردهای وارد شده یکسان نیستند.'})
        user.password = make_password(password)
        user.save()
        auth.logout(request)
        return JsonResponse({'code': 100, 'url': '/'})

    profile_user = User.objects.get(pk=request.user.id)
    context = {'profile_user': profile_user}
    return render(request, 'admin_panel_pages/panel_profile_change_password.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_company(request):
    company_Info = Company_Info.objects.all()
    if company_Info.count() == 0:
        obj = {'company_name': '', 'manager_name': '', 'phone': '', 'fax': '', 'address': '', 'banner_img': '', 'about': ''}
    else:
        obj = company_Info[0]

    if request.method == 'POST':
        company_name = request.POST['company_name']
        manager_name = request.POST['manager_name']
        phone = request.POST['phone']
        fax = request.POST['fax']
        address = request.POST['address']
        about = request.POST['about']
        try:

            img = request.FILES['img']
            if str(img.content_type).startswith('image'):
                if img.size < 5000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})
        except:
            img = ''
        try:
            logo = request.FILES['logo']

            if str(logo.content_type).startswith('image'):
                if logo.size < 5000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})
        except:
            logo = ''
        # if len(request.FILES) != 0:

        if company_name == '' and manager_name == '' and phone == '' and fax == '' and address == '' and about == '':
            return JsonResponse({'code': 102, 'url': '/panel/panel_company'})
        if company_Info.count() == 0:
            infos = Company_Info(company_name=company_name, manager_name=manager_name, phone=phone,
                                 fax=fax, address=address, about=about, banner_img=img, logo_img=logo
                                 )
            infos.save()
            return JsonResponse({'code': 100, 'result': 'اطلاعات با موفقیت ثبت شد.', 'url': '/panel/panel_company'})
        else:
            infos = get_object_or_404(Company_Info, ~Q(pk=None))
            if img != '':
                infos.banner_img.delete()
                infos.banner_img = img
            if logo != '':
                infos.logo_img.delete()
                infos.logo_img = logo

            infos.company_name = company_name
            infos.manager_name = manager_name
            infos.phone = phone
            infos.fax = fax
            infos.address = address
            infos.about = about
            infos.save()
            return JsonResponse({'code': 100, 'result': 'اطلاعات با موفقیت به روز رسانی شد.', 'url': '/panel/panel_company'})

    return render(request, 'admin_panel_pages/panel_company.html', {'company_info': obj})


# ------------------GALLERY METHODS-------------
@user_passes_test(check_staff, login_url='/')
def panel_gallery_list(request):
    galery_list = Gallery.objects.order_by('-id')
    context = {'galery_list': galery_list}
    return render(request, 'admin_panel_pages/panel_gallery_list.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_gallery_add(request):
    try:
        if request.method == 'POST':
            title = request.POST['title']
            description = request.POST['text']
            small_image = ''
            big_image = ''
            try:
                small_image = request.FILES['img_small']
            except:
                pass

            try:
                big_image = request.FILES['img_big']
            except:
                pass
            if small_image == '' or big_image == '' or title == '' or description == '':
                return JsonResponse({"error": 'فیلد ها را پر کنید.'})

            if str(small_image.content_type).startswith('image'):
                if small_image.size < 5000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})

            if str(big_image.content_type).startswith('image'):
                if big_image.size < 5000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})
            gallery = Gallery(title=title, description=description, small_img=small_image, big_img=big_image)
            gallery.save()
            return JsonResponse({'code': 100, 'url': '/panel/panel_gallery/panel_gallery_list'})
        return render(request, 'admin_panel_pages/panel_gallery_add.html')

    except:
        return redirect('panel:panel_gallery_list')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_gallery_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        gallery_id = request.POST['id']
        status = request.POST['status']
        if status == '0':
            status = False
        else:
            status = True

        Gallery.objects.filter(pk=gallery_id).update(is_published=status)

        # User.objects.filter(pk=user_id).update(is_active=status)
        return JsonResponse({'code': 100})
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_gallery_delete(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):

        try:
            gallery_id = request.POST['id']
            gallery_selected = get_object_or_404(Gallery, pk=gallery_id)
            gallery_selected.big_img.delete()
            gallery_selected.small_img.delete()
            gallery_selected.delete()
            return JsonResponse({'code': 100, 'url': '/panel/panel_gallery/panel_gallery_list'})
        except:

            return JsonResponse({'error': 'خطا رخ داده است.'})
    else:
        return redirect('/')


@user_passes_test(check_staff, login_url='/')
def panel_gallery_edit(request, image_id):
    try:
        image_selected = get_object_or_404(Gallery, pk=image_id)
        if request.method == 'POST':
            title = request.POST['title']
            text = request.POST['text']

            big_img = ''
            small_img = ''
            try:
                big_img = request.FILES['big_img']
            except:
                pass
            try:
                small_img = request.FILES['small_img']
            except:
                pass

            if title == '' or text == '':
                return JsonResponse({'error': 'فیلد های خالی را پر کنید.'})

            if big_img != '':
                if str(big_img.content_type).startswith('image'):
                    if big_img.size < 5000000:
                        pass
                    else:

                        return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

                else:
                    return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})
                image_selected.big_img.delete()
                image_selected.big_img = big_img

            if small_img != '':
                if str(small_img.content_type).startswith('image'):
                    if small_img.size < 5000000:
                        pass
                    else:

                        return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

                else:
                    return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})
                image_selected.small_img.delete()
                image_selected.small_img = small_img

            image_selected.title = title
            image_selected.description = text
            image_selected.save()
            return JsonResponse({'code': 100, 'url': '/panel/panel_gallery/panel_gallery_list'})

        return render(request, 'admin_panel_pages/panel_galler_edit.html', {'image_selected': image_selected})
    except:
        return redirect('panel:panel_gallery_list')


# ---------------------------- SURVEY METHODS -----------

@user_passes_test(check_staff, login_url='/')
def panel_survey_list(request):
    questions = Question.objects.order_by('-pk')
    context = {'questions': questions}
    return render(request, 'admin_panel_pages/panel_survey_list.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_survey_edit(request, survey_id):
    try:
        survey_selected = Question.objects.get(pk=survey_id)
        items = Choice.objects.filter(question_id=survey_id)
        if request.method == 'POST':
            title_survey = request.POST['title_survey']
            question_survey = request.POST['question_survey']
            choices = request.POST.getlist('choice_survey')
            if title_survey == '' or question_survey == '':
                return JsonResponse({'error': 'فیلد های خالی را پر کنید.'})
            for choice in choices:
                Choice.objects.create(question=survey_selected, choice_text=choice)

            survey_selected.title = title_survey
            survey_selected.question_text = question_survey
            survey_selected.save()
            return JsonResponse({'code': 100, 'url': '/panel/panel_survey/panel_survey_edit/' + str(survey_id)})

        return render(request, 'admin_panel_pages/panel_survey_edit.html', {'survey_selected': survey_selected, 'items': items})
    except:
        return render(request, 'admin_panel_pages/panel_survey_list.html')


@user_passes_test(check_staff, login_url='/')
def panel_survey_add(request):
    if request.method == 'POST':
        title = request.POST['title_survey']
        question = request.POST['question_survey']
        choices = request.POST.getlist('choice_survey')
        if title == '' or question == '':
            return JsonResponse({'error': 'فیلد ها را پر نمائید.'})
        else:
            year = datetime.now().year
            month = datetime.now().month
            day = datetime.now().day
            date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
            date_to_shamsi = date_to_shamsi.replace('-', '/')
            get_data, create = Question.objects.get_or_create(title=title, question_text=question, create_date=date_to_shamsi, is_published=False)
            for choice in choices:
                Choice.objects.create(question=get_data, choice_text=choice)
            return JsonResponse({'code': 100, 'url': '/panel/panel_survey/panel_survey_list'})
    return render(request, 'admin_panel_pages/panel_survey_add.html')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_survey_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        question_id = request.POST['id']
        status = request.POST['status']

        if status == '0':
            status = False
        else:
            status = True
        if status == True:
            Question.objects.filter(is_published=True).update(is_published=False)
            Question.objects.filter(pk=question_id).update(is_published=True)
        else:
            Question.objects.filter(pk=question_id).update(is_published=False)
        return JsonResponse({'code': 100, 'url': '/panel/panel_survey/panel_survey_list'})

    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_survey_delete(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            polls_id = request.POST['id']
            polls_selected = get_object_or_404(Question, pk=polls_id)
            polls_selected.delete()
            return JsonResponse({'code': 100, 'url': '/panel/panel_survey/panel_survey_list'})
        except:
            return JsonResponse({'error': 'خطا رخ داده است.'})
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_items_edit(request, survey_id):
    try:
        items = Choice.objects.filter(question_id=survey_id)
        if request.method == "POST":
            if request.POST['type'] == 'edit':
                item_id = request.POST['item']
                item_text = request.POST['text']
                if item_text == '':
                    return JsonResponse({'error': 'فیلد را پر کنید.'})
                Choice.objects.filter(question_id=survey_id, pk=item_id).update(choice_text=item_text)
                return JsonResponse({'code': 100, 'text': 'رکورد با موفقیت آپدیت شد.'})

            elif request.POST['type'] == 'delete':
                item_id = request.POST['item']
                if len(items) == 1:
                    return JsonResponse({'error': 'امکان حذف تمامی آیتم ها وجود ندارد.'})

                Choice.objects.get(pk=item_id).delete()
                return JsonResponse({'code': 100, 'text': 'رکورد با موفقیت حذف شد.'})


            else:
                return JsonResponse({'error': 'با خطا مواجه شدید.'})

        return render(request, 'admin_panel_pages/panel_survey_items_edit.html', {'items': items})
    except:
        return JsonResponse({'error': 'با خطا مواجه شدید.'})


# ----------------------------------Honors METHODS -------------
@user_passes_test(check_staff, login_url='/')
def panel_honors_list(request):
    news = News.objects.order_by('-id')
    honors_list = Honors.objects.order_by('-id')
    context = {'honors_list': honors_list,'grades':Honors_Grade}
    return render(request, 'admin_panel_pages/panel_honors_list.html', context)


@user_passes_test(check_staff, login_url='/')
def panel_honors_add(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        grade = request.POST['honors_grade']
        if full_name == '' or grade == '':
            return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})
        if grade not in ['0','1','2','3']:
            grade = 0

        try:
            image = request.FILES['img']
            if str(image.content_type).startswith('image'):
                if image.size < 5000000:
                    pass
                else:

                    return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

        except:
            return JsonResponse({'error': 'افزودن غکس الزامی است.'})

        try:

            file_content = request.FILES['file_content']
        except:
            return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})
        file_title = request.POST['file_title']
        if file_title == '':
            return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})

        if str(file_content.content_type).startswith('video'):
            if file_content.size < 15000000:
                pass
            else:
                return JsonResponse({'error': 'سایز ویدئو نمی تواند بیش تر از ۱۵ مگابایت باشد.'})

        elif str(file_content.content_type).startswith('application/pdf'):
            if file_content.size < 5000000:
                pass
            else:
                return JsonResponse({'error': 'سایز پی دی اف نمی تواند بیش تر از ۵ مگابایت باشد.'})
        elif str(file_content.content_type).startswith('image'):
            if file_content.size < 5000000:
                pass
            else:
                return JsonResponse({'error': 'سایز عکس نمی تواند بیش تر از ۵ مگابایت باشد.'})

        elif str(file_content.content_type).startswith('text/plain'):
            if file_content.size < 5000000:
                pass
            else:
                return JsonResponse({'error': 'سایز فایل متنی نمی تواند بیش تر از ۵ مگابایت باشد.'})
        get_data, create = Honors.objects.get_or_create(full_name=full_name, image=image, grade=int(grade))
        Honors_Files.objects.create(title=file_title, file=file_content, honors_id=get_data)
        return JsonResponse({'code': 100, 'url': '/panel/panel_honor/panel_honor_list'})
    return render(request, 'admin_panel_pages/panel_honors_add.html',{'grades':Honors_Grade})


@user_passes_test(check_staff, login_url='/')
def panel_honors_edit(request, honors_id):
    try:
        honors_selected = get_object_or_404(Honors, pk=honors_id)
        honors_files = Honors_Files.objects.filter(honors_id=honors_id)
        if request.method == 'POST':
            if request.POST['type'] == 'edit':
                full_name = request.POST['full_name']
                grade = request.POST['honors_grade']
                if full_name == '' or grade == '':
                    return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})

                if grade not in ['0', '1', '2', '3']:
                    grade = 0
                image = ''
                try:
                    image = request.FILES['img']
                    if str(image.content_type).startswith('image'):
                        if image.size < 5000000:
                            pass
                        else:
                            return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})
                    else:
                        return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})
                except:
                    pass
                file_content = ''
                try:
                    file_content = request.FILES['file_content']
                except:
                    pass

                file_title = request.POST['file_title']

                if file_content != '':
                    if str(file_content.content_type).startswith('video'):
                        if file_content.size < 15000000:
                            pass
                        else:
                            return JsonResponse({'error': 'سایز ویدئو نمی تواند بیش تر از ۱۵ مگابایت باشد.'})

                    elif str(file_content.content_type).startswith('application/pdf'):
                        if file_content.size < 5000000:
                            pass
                        else:
                            return JsonResponse({'error': 'سایز پی دی اف نمی تواند بیش تر از ۵ مگابایت باشد.'})
                    elif str(file_content.content_type).startswith('image'):
                        if file_content.size < 5000000:
                            pass
                        else:
                            return JsonResponse({'error': 'سایز عکس نمی تواند بیش تر از ۵ مگابایت باشد.'})

                    elif str(file_content.content_type).startswith('text/plain'):
                        if file_content.size < 5000000:
                            pass
                        else:
                            return JsonResponse({'error': 'سایز فایل متنی نمی تواند بیش تر از ۵ مگابایت باشد.'})
                    else:
                        return JsonResponse({'error': 'امکان بارگذاری عکس فیلم و پی دی اف وجود دارد.'})

                if image != '':
                    honors_selected.image.delete()
                    honors_selected.image = image
                honors_selected.full_name = full_name
                honors_selected.grade = int(grade)
                honors_selected.save()
                if file_content != '' and file_title != '':
                    Honors_Files.objects.create(title=file_title, file=file_content, honors_id=honors_selected)
                else:
                    if file_content != '' or file_title != '':
                        return JsonResponse({'error': 'در صورت بارگذاری فایل برای آن عنوان تعریف کنید.'})

                return JsonResponse({'code': 100})
            elif request.POST['type'] == 'delete':
                item_id = request.POST['item']
                if len(honors_files) == 1:
                    return JsonResponse({'error': 'امکان حذف تمامی آیتم ها وجود ندارد.'})

                file = Honors_Files.objects.get(pk=item_id)
                file.file.delete()
                file.delete()
                return JsonResponse({'code': 100, 'text': 'رکورد با موفقیت حذف شد.'})
            else:
                return JsonResponse({'error': 'با خطا مواجه شدید.'})
        return render(request, 'admin_panel_pages/panel_honors_edit.html', {'honors_selected': honors_selected, 'honors_files': honors_files,'grades':Honors_Grade})
    except:
        return redirect('panel:panel_honors_list')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_honors_delete(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):

        try:
            honors_id = request.POST['id']
            honors_selected = get_object_or_404(Honors, pk=honors_id)
            honors_selected.image.delete()
            honors_selected.delete()
            return JsonResponse({'code': 100, 'url': '/panel/panel_honor/panel_honor_list'})
        except:
            return JsonResponse({'error': 'خطا رخ داده است.'})
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_honors_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        honors_id = request.POST['id']
        status = request.POST['status']
        if status == '0':
            status = False
        else:
            status = True

        Honors.objects.filter(pk=honors_id).update(is_published=status)
        return JsonResponse({'code': 100})
    else:
        return redirect('/')

# @csrf_exempt
# @user_passes_test(check_staff, login_url='/')
# def honors_files(request):

# -----------------NEWS METHODS -----------------------
@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_news_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        news_id = request.POST['id']
        status = request.POST['status']

        if status == '0':
            status = False
        else:
            status = True

        News.objects.filter(pk=news_id).update(is_published=status)
        return JsonResponse({'code': 100})
    else:
        return redirect('/')


@user_passes_test(check_staff, login_url='/')
def panel_news_add(request):  # متد مربوط به افزودن خبر
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        short_text = request.POST['short_text']
        if title == '' or description == '' or short_text == '':
            return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
        date_to_shamsi = date_to_shamsi.replace('-', '/')

        form = NewsForm(request.POST)
        if form.is_valid():
            try:
                pic = request.FILES['image_1']
                if str(pic.content_type).startswith('image'):
                    if pic.size < 5000000:
                        post_item = form.save()
                        post_item.create_date = date_to_shamsi
                        post_item.image_1 = pic
                        post_item.save()
                        return JsonResponse({'code': 100, 'url': '/panel/panel_news/panel_news_list'})
                    else:
                        return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})
                else:
                    return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})
            except:
                return JsonResponse({'error': 'افزودن عکس الزامی می باشد.'})
        else:
            return JsonResponse({'error': 'خطا رخ داده است.'})

    else:
        form = NewsForm()
    return render(request, 'admin_panel_pages/panel_news_add.html', {'form': form})


@user_passes_test(check_staff, login_url='/')
def panel_news_edit(request, news_id):
    try:
        news_selected = get_object_or_404(News, pk=news_id)
        if request.method == 'POST':
            title = request.POST['title']
            description = request.POST['description']
            short_text = request.POST['short_text']
            if title == '' or description == '' or short_text == '':
                return JsonResponse({'error': 'تمامی فیلدهارا پر کنید.'})
            news_selected.title = title
            news_selected.description = description
            news_selected.short_text = short_text
            try:
                picture = request.FILES['image_1']
            except:
                picture = ''
                pass
            if picture != '':
                if str(picture.content_type).startswith('image'):
                    if picture.size < 5000000:
                        news_selected.image_1.delete()
                        news_selected.image_1 = picture
                    else:
                        return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})
                else:
                    return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})
            news_selected.save()
            return JsonResponse({'code': 100, 'url': '/panel/panel_news/panel_news_list'})
        form = NewsForm()
        return render(request, 'admin_panel_pages/panel_news_edit.html', {'news_selected': news_selected, 'form': form})
    except:
        return redirect('panel:panel_news_list')


@user_passes_test(check_staff, login_url='/')
def panel_news_list(request):
    news = News.objects.order_by('-id')
    cats_list = Category_News.objects.order_by('-id')
    context = {'news_list': news, 'cats_list': cats_list}
    return render(request, 'admin_panel_pages/panel_news_list.html', context)


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_news_delete(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            news_id = request.POST['id']
            news_selected = get_object_or_404(News, pk=news_id)
            news_selected.image_1.delete()
            news_selected.delete()
            return JsonResponse({'code': 100, 'url': '/panel/panel_news/panel_news_list'})
        except:

            return JsonResponse({'error': 'خطا رخ داده است.'})
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def add_category_news(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):

        val_cat = request.POST['val']
        if val_cat != '':
            cat_info = Category_News(title=val_cat)
            cat_info.save()
        cats_list = Category_News.objects.all()
        if request.is_ajax():
            context = {'cats_list': cats_list}
            html = render_to_string('admin_panel_pages/load_page/load_cat_news_list.html', context)
            return HttpResponse(html)
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def category_selected(request):
    if Category_News.objects.all().count() == 0:
        cat_info = Category_News(title='دسته برگزیده')
        cat_info.save()
        cats_list = Category_News.objects.all()
        if request.is_ajax():
            context = {'cats_list': cats_list}
            html = render_to_string('admin_panel_pages/load_page/load_cat_selected.html', context)
            return HttpResponse(html)


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def select_cat_news(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            news_ids = request.POST.getlist('newsid_list[]')
            cat_id = request.POST['cat_id']
            cat_news_selected = Category_News.objects.get(pk=int(cat_id))
            for item in news_ids:
                News.objects.filter(pk=int(item)).update(category=cat_news_selected)

            return JsonResponse({'code': 100, 'url': '/panel/panel_news/panel_news_list'})
        except:
            return JsonResponse({'url': '/panel/panel_news/panel_news_list'})

    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def delete_category(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            cat_id = request.POST['cat_id']
            cat_selected = get_object_or_404(Category_News, pk=cat_id)
            cat_selected.delete()
            cats_list = Category_News.objects.all()
            if request.is_ajax():
                context = {'cats_list': cats_list}
                html = render_to_string('admin_panel_pages/load_page/load_cat_news_list.html', context)
                return HttpResponse(html)
        except:
            pass
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def list_category(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            cats_list = Category_News.objects.all()
            if request.is_ajax():
                context = {'cats_list': cats_list}
                html = render_to_string('admin_panel_pages/load_page/cat_news_option.html', context)
                return HttpResponse(html)
        except:
            pass
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def delete_cat_news(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            cat_id = request.POST['cat_id']
            news_change = News.objects.filter(category__id=int(cat_id))
            if news_change.count() == 0:
                return JsonResponse({'code': 103})
            else:
                list_change_news_cat = list(set(list(news_change.values_list('pk', flat=True))))
                return JsonResponse({'code': 100, 'list_change_news_cat': list_change_news_cat})
        except:
            pass
    else:
        return redirect('/')


# ------------------------------USER METHODS-------------------

@user_passes_test(check_staff, login_url='/')
def panel_user_list(request):
    User = get_user_model()
    users_list = User.objects.order_by('-pk').filter(is_staff=False)
    context = {'users_list': users_list, 'genders': Genders}
    return render(request, 'admin_panel_pages/panel_user_list.html', context)


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_user_search(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            User = get_user_model()
            type_cmp = request.POST['type_cmp']
            status_user = request.POST['status_user']
            users_list = User.objects.order_by('-pk').filter(is_staff=False)

            if status_user == 'null' and type_cmp == 'null':
                pass
            if type_cmp != 'null':
                users_list = users_list.filter(interest=int(type_cmp))
            if status_user != 'null':
                users_list = users_list.filter(activate_status=status_user)

            if request.is_ajax():
                context = {'users_list': users_list, 'genders': Genders}
                html = render_to_string('admin_panel_pages/load_page/users_list.html', context)
                return HttpResponse(html)
        except:
            pass
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_user_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        User = get_user_model()
        user_id = request.POST['id']
        status = request.POST['status']
        if status == '0':
            status = False
        else:
            status = True
        User.objects.filter(pk=int(user_id)).update(activate_status=status)
        return JsonResponse({'code': 100})
    else:
        return redirect('/')


@user_passes_test(check_staff, login_url='/')
def panel_user_edit(request, user_id):
    User = get_user_model()
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        national_code = request.POST['national_code']


        gender = request.POST['gender']
        address = request.POST['address']
        if first_name == '':
            return JsonResponse({'error': 'فیلد نام را تکمیل نمائید'})
        if last_name == '':
            return JsonResponse({'error': 'فیلد نام خانوادگی را تکمیل نمائید'})
        if birth_date == '':
            return JsonResponse({'error': 'فیلد تاریخ تولد را تکمیل نمائید'})
        if national_code == '':
            return JsonResponse({'error': 'فیلد کدملی را تکمیل نمائید'})
        if gender == '':
            return JsonResponse({'error': 'جنسیت خود را تعیین کنید.'})


        rule = re.compile(r'([12]\d{3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01]))')
        validate_date = rule.search(birth_date)
        if validate_date == None:
            return JsonResponse({'error': 'تاریخ تولد را از تقویم انتخاب کنید.'})

        national_imgage = ''
        try:
            national_imgage = request.FILES['national_img']
            if str(national_imgage.content_type).startswith('image'):
                if national_imgage.size < 5000000:
                    pass
                else:

                    return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

        except:
            pass
        if 'interest' in request.POST:
            if request.POST['interest'] in ["0","2"]:
                profile_judo_info = get_object_or_404(Profile_Judo, user_id=user_id)

                coach_name = request.POST['coach_name_judo']
                club_name = request.POST['club_name_judo']
                position = request.POST['position_judo']
                if position == '':
                    return JsonResponse({'error': 'سمت خود را تعیین کنید.'})
                qform = ''
                try:
                    qform = request.FILES['qform_document_judo']
                    if str(qform.content_type).startswith('image'):
                        if qform.size < 5000000:
                            pass
                        else:

                            return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

                    else:
                        return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

                except:
                    pass

                if profile_judo_info.qform_document == '' and qform == '':
                    return JsonResponse({'error': 'افزودن فایل کمربند الزامی می باشد.'})

                profile_judo_info.club_name = club_name
                profile_judo_info.coach_name = coach_name
                profile_judo_info.position = position
                if qform != '':
                    profile_judo_info.qform_document.delete()
                    profile_judo_info.qform_document = qform
                profile_judo_info.save()
            if request.POST['interest'] in ["1", "2"]:
                Profile_jujitso = get_object_or_404(Profile_Jujitso, user_id=user_id)

                coach_name = request.POST['coach_name_jujitso']
                club_name = request.POST['club_name_jujitso']
                position = request.POST['position_jujitso']
                if position == '':
                    return JsonResponse({'error': 'سمت خود را تعیین کنید.'})
                qform = ''
                try:
                    qform = request.FILES['qform_document_jujitso']
                    if str(qform.content_type).startswith('image'):
                        if qform.size < 5000000:
                            pass
                        else:

                            return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

                    else:
                        return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

                except:
                    pass

                if Profile_jujitso.qform_document == '' and qform == '':
                    return JsonResponse({'error': 'افزودن فایل کمربند الزامی می باشد.'})

                Profile_jujitso.club_name = club_name
                Profile_jujitso.coach_name = coach_name
                Profile_jujitso.position = position
                if qform != '':
                    Profile_jujitso.qform_document.delete()
                    Profile_jujitso.qform_document = qform
                Profile_jujitso.save()

        person_img = ''
        try:
            person_img = request.FILES['person_img']
            if str(person_img.content_type).startswith('image'):
                if person_img.size < 5000000:
                    pass
                else:

                    return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

            else:
                return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

        except:
            pass

        profile = User.objects.get(pk=user_id)

        if profile.national_document_image == '' and national_imgage == '':
            return JsonResponse({'error': 'افزودن عکس مربوط ب کارت ملی الزامی می باشد.'})

        profile.gender = gender
        profile.birth_date = birth_date
        profile.national_code = national_code

        if national_imgage != '':
            profile.national_document_image.delete()
            profile.national_document_image = national_imgage

        if person_img != '':
            profile.personal_image.delete()
            profile.personal_image = person_img

        profile.address = address

        profile.save()
        User.objects.filter(pk=user_id).update(first_name=first_name, last_name=last_name)
        return JsonResponse({'code': 100, 'result': 'اطلاعات با موفقیت ثبت شدند.', 'url': '/panel/panel_users/panel_user_list'})
    try:
        profile_info = get_object_or_404(User, pk=user_id)
        context = {'profile_info': profile_info, 'genders': Genders, 'positions': Positions}
        if profile_info.interest in [0, 2]:
            profile_judo_info = get_object_or_404(Profile_Judo, user_id=user_id)
            context['profile_judo_info'] = profile_judo_info
        if profile_info.interest in [1, 2]:
            profile_jujitso_info = get_object_or_404(Profile_Jujitso, user_id=user_id)
            context['profile_jujitso_info'] = profile_jujitso_info

        return render(request, 'admin_panel_pages/panel_user_edit.html', context)
    except:
        return redirect('panel:panel_user_list')


# ---------------------competition------------

def check_staff_check_weight_table(user):
    if user.is_staff:
        w_t = Weight_Classification.objects.all()
        if len(w_t) != 0:
            return True
    return False


@user_passes_test(check_staff_check_weight_table, login_url='/panel/panel_competition/panel_competition_list')
def panel_competition_add(request):
    try:
        if request.method == 'POST':

            year = datetime.now().year
            month = datetime.now().month
            day = datetime.now().day
            date_to_shamsi = jalali.Gregorian(str(year) + "-" + str(month) + '-' + str(day)).persian_string()
            date_to_shamsi = date_to_shamsi.replace('-', '/')

            title = request.POST['Competition_title']
            competition_date = request.POST['Competition_date']
            register_start_date = request.POST['register_start_date']
            register_end_date = request.POST['register_end_date']

            capacity_ = request.POST['Competition_Capacity']
            try:
                capacity = int(capacity_)
            except:
                capacity = ''

            rule = re.compile(r'([12]\d{3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01]))')
            validate_competition_date = rule.search(competition_date)
            validate_register_start_date = rule.search(register_start_date)
            validate_register_end_date = rule.search(register_end_date)

            if validate_competition_date == None or validate_register_start_date == None or validate_register_end_date == None:
                return JsonResponse({'error': 'تاریخ  را از تقویم انتخاب کنید.'})

            competition_gender = request.POST['Competition_gender']
            if competition_gender not in ["0", "1", "2"]:
                competition_gender = 0
            try:
                poster_image = request.FILES['img_poster']
            except:
                poster_image = ''

            try:
                bakhshname_image = request.FILES['img_bakhshname']
            except:
                bakhshname_image = ''

            if poster_image == '' or bakhshname_image == '':
                return JsonResponse({"error": 'فیلد ها را پر نمائید.'})

            if str(poster_image.content_type).startswith('image'):
                if poster_image.size < 10000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از 10 مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})

            if str(bakhshname_image.content_type).startswith('image'):
                if bakhshname_image.size < 10000000:
                    pass
                else:
                    return JsonResponse({"error": 'سایز فایل نمی تواند بیش تر از 10 مگابایت باشد.'})

            else:
                return JsonResponse({"error": 'فایل پشتیبانی نمی شود.'})

            age_category_list = request.POST['age_category_list']
            error = ''
            i = 0
            competition_id = 0
            if age_category_list != '':
                age_category_list = eval(age_category_list)
                for data in age_category_list:

                    if data['name'] == '' or data['weight'] == '':
                        error = 'empty'
                        break
                    if not isinstance(data['weight'], list):
                        error = 'type'
                        break

                    validate_from_date = rule.search(data['from_date'])
                    validate_to_date = rule.search(data['to_date'])

                    if (data['from_date'] != '' and validate_from_date == None) or (data['to_date'] and validate_to_date == None):
                        error = 'date'
                        break
                    for weight in data['weight']:
                        if competition_gender == "2":
                            gender_list = [0, 1]
                        else:
                            gender_list = [int(competition_gender)]
                        for gender in gender_list:
                            i += 1
                            weight_tbl = Weight_Classification.objects.get(id=int(weight))

                            create_competition = Competition(title=title, subtitle=data['name'],
                                                             user_from_birtday=data['from_date'],
                                                             user_to_birthday=data['to_date'],
                                                             register_from=register_start_date,
                                                             register_to=register_end_date,
                                                             competition_date=competition_date,
                                                             create_date=date_to_shamsi,
                                                             bakhshname_image=bakhshname_image,
                                                             poster_image=poster_image,
                                                             capacity=capacity,
                                                             weight=weight_tbl, gender=gender
                                                             )
                            if i == 1:
                                create_competition.save()
                                competition_id = create_competition.pk
                                create_competition.cmp_id = competition_id

                                create_competition.save()
                                ranks = Rank_Detail(cmp_id=create_competition)
                                ranks.save()
                            else:
                                create_competition.cmp_id = competition_id
                                create_competition.save()

                if error != '':
                    if error == 'date':
                        return JsonResponse({'error': 'فرمت تاریخ به صورت ۱۳۹۸/۰۵/۰۴ می باشد.'})
                    if error == 'empty':
                        return JsonResponse({'error': 'فیلدهارا پر نمائید.'})
                    if error == 'type':
                        return JsonResponse({'error': 'خطا رخ داده است.'})

                return JsonResponse({'code': 100, 'url': '/panel/panel_competition/panel_competition_list'})
            else:
                return JsonResponse({'error': 'فیلد ها را پر نمائید.'})

        weights_list = Weight_Classification.objects.all()
        return render(request, 'admin_panel_pages/panel_competition_add.html', {'weights_list': weights_list,
                                                                                'age_period': Age_Period, 'genders': Genders})
    except:
        return JsonResponse({'error': 'خطا رخ داده است.'})


@user_passes_test(check_staff, login_url='/')
def panel_competition_list(request):
    try:
        cursor = connection.cursor()
        cursor.execute('select cmp_id AS id,(array_agg(distinct title))[1] title,(array_agg(distinct competition_date))[1] competition_date,(array_agg(distinct capacity))[1] capacity,(array_agg(distinct create_date))[1] create_date,(array_agg(distinct is_published))[1] is_published from competition_competition group by cmp_id order by competition_date desc;')
        columns = [column[0] for column in cursor.description]  # find key  of cursor

        competition_list = []
        for row in cursor.fetchall():
            competition_list.append(dict(zip(columns, row)))
        context = {'competition_list': competition_list}
        return render(request, 'admin_panel_pages/panel_competition_list.html', context)
    except:
        return redirect('panel:panel_competition_list')
    finally:
        connection.close()


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_competition_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        cmp_id = request.POST['id']
        status = request.POST['status']

        if status == '0':
            status = False
        else:
            status = True

        Competition.objects.filter(cmp_id=cmp_id).update(is_published=status)
        return JsonResponse({'code': 100})
    else:
        return redirect('/')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def panel_competition_delete(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            cmp_id = request.POST['id']
            cmp_selected = Competition.objects.filter(cmp_id=int(cmp_id))
            user_in_cmp = User_In_Competition.objects.filter(cid_id__cmp_id=int(cmp_id), status=True)  # agar user faal dashte bashe ejaze hazf nemidam
            if len(user_in_cmp) != 0:
                return JsonResponse({'error': 'امکان حذف فعال نمی باشد.'})
            else:
                for cmp in cmp_selected:
                    cmp.bakhshname_image.delete()
                    cmp.poster_image.delete()
                    cmp.delete()
                return JsonResponse({'code': 100, 'url': '/panel/panel_competition/panel_competition_list'})
        except:
            return JsonResponse({'error': 'خطا رخ داده است.'})
    else:
        return redirect('/')


@user_passes_test(check_staff, login_url='/')
def panel_competition_edit(request, cmp_id):  # check
    cmps_selected = Competition.objects.filter(cmp_id=int(cmp_id))
    users_in_cmp = User_In_Competition.objects.filter(cid_id__cmp_id=int(cmp_id))

    if request.method == 'POST':
        Competition_date = request.POST['Competition_date']
        capacity = request.POST['Competition_Capacity']
        register_start_date = request.POST['register_start_date']
        register_end_date = request.POST['register_end_date']

    genders = cmps_selected.values_list('gender', flat=True)
    subtitles = list(set(list(cmps_selected.values_list('subtitle', flat=True))))

    list_category_age_box = []
    for index, subtitle in enumerate(subtitles):
        filters = cmps_selected.filter(subtitle=subtitle)
        # print(5555,filters)

        list_category_age_box.append({'subtitle': subtitle, 'weights': list(set(list(filters.values_list('weight', flat=True)))),

                                      'from_birthday': list(set(list(filters.values_list('user_from_birtday', flat=True)))),
                                      'to_birthday': list(set(list(filters.values_list('user_to_birthday', flat=True)))),
                                      })

    print(list_category_age_box)

    gender_list = []
    for gender in genders:
        if gender not in gender_list:
            gender_list.append(gender)
    if len(gender_list) == 2:
        gender = 2
    else:
        gender = gender_list[0]
    print(5555, cmps_selected)
    title = cmps_selected[0].title
    competition_date = cmps_selected[0].competition_date
    capacity = cmps_selected[0].capacity
    register_from = cmps_selected[0].register_from
    register_to = cmps_selected[0].register_to

    poster_image = cmps_selected[0].poster_image
    bakhshname_image = cmps_selected[0].bakhshname_image

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
    past = 0
    if competition_date < date_to_shamsi:
        past = 1  # tarikhe mosabeghe gozashte ast

    # for cmp in cmps_selected:

    weights_list = Weight_Classification.objects.all()
    context = {'cmp_id': cmp_id, 'title': title, 'competition_date': competition_date, 'capacity': capacity, 'gender': gender,
               'register_from': register_from,
               'register_to': register_to, 'poster_image': poster_image,
               'bakhshname_image': bakhshname_image, 'list_category_age_box': list_category_age_box,
               'age_period': Age_Period, 'genders': Genders_in_Cmp, 'weights_list': weights_list, 'past': past

               }
    if request.method == 'POST':
        pass
    return render(request, 'admin_panel_pages/panel_competition_edit.html', context)


# ---------user in competition ---------

@user_passes_test(check_staff, login_url='/')
def panel_competition_user(request, cmp_id):
    try:
        users_in_cmp = User_In_Competition.objects.filter(cid_id__cmp_id=int(cmp_id)).order_by('-id')
        context = {'users': users_in_cmp}
        return render(request, 'admin_panel_pages/panel_competition_user.html', context)
    except:
        print(traceback.format_exc())
        return redirect('panel:panel_competition_list')


@csrf_exempt
@user_passes_test(check_staff, login_url='/')
def update_weight(request):
    try:
        if 'json' in request.META.get('HTTP_ACCEPT'):
            cmp_id = request.POST['cmp_id']
            id = request.POST['id']
            gender = request.POST['gender']
            list_ = Competition.objects.filter(cmp_id=int(cmp_id), gender=int(gender))
            if 'subtitle_change' in request.POST:
                subtitle = request.POST['subtitle_change']
                weights_period = list(list_.filter(subtitle=int(subtitle)).values('weight__title', 'weight__id'))
                if request.is_ajax():
                    context = {'weights_period': weights_period, }
                    html = render_to_string('admin_panel_pages/load_page/weight_change_period.html', context)
                    return HttpResponse(html)

            subtitle = request.POST['subtitle']
            ages_list = list(set(list(list_.values_list('subtitle', flat=True))))
            age_selected = int(subtitle)

            weight_selected = list(list_.filter(id=id, subtitle=int(subtitle)).values('weight'))[0]
            weights_period = list(list_.filter(subtitle=int(subtitle)).values('weight__title', 'weight__id'))
            if request.is_ajax():
                context = {'weights_period': weights_period, 'weight_selected': weight_selected['weight'],
                           'ages_list': ages_list, 'age_selected': age_selected, 'ages_period': Age_Period}
                html = render_to_string('admin_panel_pages/load_page/weights_period.html', context)
                return HttpResponse(html)
        else:
            return redirect('panel:panel_competition_user')
    except:
        return redirect('panel:panel_competition_user')


@csrf_exempt
def point_save(request):
    try:
        if 'json' in request.META.get('HTTP_ACCEPT'):
            place = (request.POST['place_id'])
            pr_k = int(request.POST['pr_k'])
            cmp_id = int(request.POST['cmp_id'])
            rank_info = Rank_Detail.objects.get(place=int(place), cmp_id=cmp_id)
            User_In_Competition.objects.filter(pk=pr_k).update(place_id=rank_info)
            return JsonResponse({'result': place})



        else:
            pass
    except:
        place_id = User_In_Competition.objects.get(pk=pr_k).place_id.place
        return JsonResponse({'result': place_id})


@csrf_exempt
def panel_user_in_competition_enable(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        id_ = request.POST['id']
        status = request.POST['status']

        if status == '0':
            status = False
        else:
            status = True
        user_in_cmp = User_In_Competition.objects.filter(pk=id_)

        Competition_info = user_in_cmp[0]
        capacity = Competition_info.cid.capacity
        if capacity == '':
            user_in_cmp.update(status=status, reject_status=False, reject_cause='')
        else:
            users_in_cmp = User_In_Competition.objects.filter(cid_id=Competition_info.cid.id, reject_status=False, status=True)

            if int(capacity) - len(users_in_cmp) > 0:
                user_in_cmp.update(status=status, reject_status=False, reject_cause='')

            else:
                user_in_cmp.update(status=False, reject_status=False, reject_cause='')
        return JsonResponse({'code': 100})
    else:
        return redirect('/')


@csrf_exempt
def panel_user_reject(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        try:
            print(33333333333)
            id = int(request.POST['uid'])
            cid = int(request.POST['cid'])
            desc = request.POST['desc']
            print(111, id, 444, cid, 555, desc)
            if desc == '':
                return JsonResponse({'error': 'دلیل ریجکت را وارد نمائید.'})

            User_In_Competition.objects.filter(pk=id, cid=cid).update(reject_status=True, status=False, reject_cause=desc)
            return JsonResponse({'code': 100, 'result': 'کاربر با موفقیت از مسابقه حذف شد.'})

        except:
            return JsonResponse({'error': 'با خطا مواجه شدید.'})
    else:
        print(traceback.format_exc())
        return redirect('panel:panel_competition_list')


@user_passes_test(check_staff, login_url='/')
def panel_competition_rank(request, cmp_id):
    try:
        cmp_info = Competition.objects.filter(cmp_id=int(cmp_id))  # shayad string zad tu input
        if len(cmp_info) == 0:
            return redirect('panel:panel_competition_list')  # agar id alaki zad bere safhe liste mosabeghat
    except:
        return JsonResponse({'error': 'با خطا مواجه شدید.'})
    if request.method == 'POST':
        if len(cmp_info) != 0:
            for rank in eval(request.POST['ranking']):
                if rank['place'] == '' or rank['point'] == '':
                    return JsonResponse({'error': 'فیلد ها را پر نمائید.'})
                try:
                    place = int(rank['place'])
                except:
                    return JsonResponse({'error': 'لطفا عدد وارد نمائید.'})
                try:
                    point = rank['point']
                except:
                    return JsonResponse({'error': 'لطفا عدد وارد نمائید.'})

                rank_detail = Rank_Detail(place=place, point=point, cmp_id=cmp_info[0])
                rank_detail.save()
            return JsonResponse({'code': 100, 'url': request.get_full_path()})

    ranks_for_cmp = Rank_Detail.objects.filter(cmp_id=int(cmp_id))
    return render(request, 'admin_panel_pages/panel_competition_rank.html', {'cmpid': cmp_id, 'ranks_for_cmp': ranks_for_cmp})


# ----------------weight-------

@user_passes_test(check_staff, login_url='/')
def panel_competition_weight(request):
    if request.method == 'POST':
        w_Category_period = request.POST.getlist('w_Category_period')
        len_w = len(w_Category_period)
        i = 0
        for weight in w_Category_period:
            if weight == '':
                i += 1
                pass
            else:
                title = Weight_Classification(title=weight)
                title.save()
        if i == len_w:
            return JsonResponse({'error': 'فیلد ها را پر نمائید.'})
        else:
            return JsonResponse({'code': 100, 'url': '/panel/panel_competition/panel_competition_weight'})

    w_list = Weight_Classification.objects.all()
    context = {'w_list': w_list}
    return render(request, 'admin_panel_pages/panel_competition_weight.html', context)


@csrf_exempt
def check_len_weight_table(request):
    if 'json' in request.META.get('HTTP_ACCEPT'):
        w_t = Weight_Classification.objects.all()
        if len(w_t) != 0:
            return JsonResponse({'code': 100, 'url': '/panel/panel_competition/panel_competition_add'})
        else:
            return JsonResponse({'error': 'ابتدا رده وزنی را تعریف کنید.'})
    else:
        return redirect('panel:panel_competition_weight')
