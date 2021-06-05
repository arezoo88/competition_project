from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .models import Profile_Judo, Profile_Jujitso
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import traceback
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import re
from competition_project.choices import Genders, Positions, Age_Period
from competition.models import User_In_Competition, Weight_Classification
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.http import HttpResponse
from .validate_national_code import is_valid_national_code


# etebare code ersali
# ------------------------register and login------------------
class CustomPasswordValidator:

    def __init__(self, min_length=1):
        self.min_length = min_length

    def validate(self, password):
        if len(password) < 6:
            return {'error': 'طول پسورد حداقل باید ۶ کاراکتر باشد.'}
        if len(password) > 20:
            return {'error': 'طول پسورد حداکثر باید 20 کاراکتر باشد.'}
        else:
            return {'success': '1'}

    def get_help_text(self):
        return ""


def check_time_for_send_sms(datetime_db, date_time_now):
    diff = datetime_db - date_time_now
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minute = (seconds % 3600) // 60

    total_minutes = abs(hours * 60 + minute)

    if total_minutes < 30:
        return 1
    else:
        return 0


def register(request):
    User = get_user_model()
    if request.user.is_authenticated:  # resirect to profile
        if request.user.is_staff == False:
            return redirect('account:dashboard')
        else:
            return redirect('panel:panel_profile')

    if request.method == 'POST':
        password = request.POST['password']
        mobile_number = request.POST['mobile']
        nationalcode = request.POST['nationalcode']
        if password == '' or mobile_number == '' or nationalcode == '':
            return JsonResponse({'result': 'فیلد های مورد نظر را پر کنید.'})

        rule = re.compile(r'^(?:\+?)?[0]\d{10}$')  # validate mobile number
        validate_phone = rule.search(mobile_number)
        if is_valid_national_code(nationalcode) == False:
            return JsonResponse({'result': 'کد ملی معتبر وارد کنید.'})

        if validate_phone == None:
            return JsonResponse({'result': 'شماره موبایل را با فرمت (09121111111) وارد کنید.'})
        #
        try:
            Judo_interes = request.POST['f_Judo']
        except:
            Judo_interes = 'off'
        try:
            Jujitso_interes = request.POST['f_Self_Defense']
        except:
            Jujitso_interes = 'off'

        interest = 0
        if Judo_interes == 'off' and Jujitso_interes == 'off':
            return JsonResponse({'result': 'لطفا یکی از گرایش ها را انتخاب کنید.'})

        elif Judo_interes == 'on' and Jujitso_interes == 'on':
            interest = 2
        elif Judo_interes == 'on':
            interest = 0
        elif Jujitso_interes == 'on':

            interest = 1
        else:
            return JsonResponse({'result': 'با خطا مواجه شده اید.'})

        pass_validate = CustomPasswordValidator().validate(password)
        if 'error' in pass_validate:
            return JsonResponse({'result': pass_validate['error']})






        else:
            if User.objects.filter(username=nationalcode).exists():
                return JsonResponse({'result': 'این کد ملی قبلا ثبت شده است'})
            else:
                user = User.objects.create_user(username=nationalcode, phone=mobile_number,
                                                password=password, interest=interest)
                user.refresh_from_db()
                user.save()
                authenticate(username=mobile_number, password=password)
                auth.login(request, user)
                if request.user.is_staff == False:

                    return JsonResponse({'code': 1, 'url': '/user/dashboard'})
                else:
                    return JsonResponse({'code': 1, 'url': '/panel/panel_profile'})

    else:
        return render(request, 'account/register&login.html')


def forget_password(request):
    if request.user.is_authenticated:
        return redirect('pages:index')
    if request.method == 'POST':
        mobile_number = request.POST['mobile']
        nationalcode = request.POST['nationalcode']
        if mobile_number == '' or nationalcode == '':
            return JsonResponse({'result': 'فیلد های مورد نظر را پر کنید.'})

        rule = re.compile(r'^(?:\+?)?[0]\d{10}$')  # validate mobile number
        validate_phone = rule.search(mobile_number)

        if validate_phone == None:
            return JsonResponse({'result': 'شماره موبایل را با فرمت (09121111111) وارد کنید.'})
        User = get_user_model()

        if not User.objects.filter(username=nationalcode, phone=mobile_number).exists():
            return JsonResponse({'result': 'با این کد ملی و شماره موبایل ثبت نام نکرده اید.'})
        try:
            # reponse_sms = send_sms(mobile_number)
            sms_code = 333
            print(sms_code)
        except:

            return JsonResponse({'result': 'دوباره تلاش کنید.'})

        request.session['code'] = sms_code
        request.session['user'] = nationalcode
        return JsonResponse({'code': 1, 'result': ('برای شماره موبایل %(mobile_number)s کد تاسید ارسال شده است.') % {'mobile_number': mobile_number}
                                , 'url': '/user/confirm'})

    return render(request, 'account/forget_password.html')


def confirm(request):
    if request.method == 'POST':
        code = request.session['code']
        verification_code_input = request.POST['code']
        if verification_code_input != '':
            if int(code) == int(verification_code_input):
                return JsonResponse({'code': 1, 'result': '/user/reset_password'})
            else:
                return JsonResponse({'result': 'کد وارد شده اشتباه است.'})
        else:
            return JsonResponse({'result': 'لطفا کد ارسال شده را وارد نمائید.'})

    return render(request, 'account/verification.html')


@csrf_exempt
def resend_sms_code(request):
    try:
        # reponse_sms = send_sms(mobile_number)
        sms_code = 222
        print(sms_code)
    except:
        return JsonResponse({'result': 'دوباره تلاش کنید.'})
    request.session['code'] = sms_code
    return JsonResponse({'result': 'کد جدید ارسال شد.'})


def reset_password(request):
    if request.user.is_authenticated:
        return redirect('pages:index')
    if request.method == 'POST':
        password = request.POST['password']
        if password == '':
            return JsonResponse({'result': 'فیلد مورد نظر را پر کنید.'})

        nationalcode = request.session['user']

        pass_validate = CustomPasswordValidator().validate(password)
        if 'error' in pass_validate:
            return JsonResponse({'result': pass_validate['error']})
        User = get_user_model()

        if User.objects.filter(username=nationalcode).exists():
            User.objects.filter(username=nationalcode).update(password=make_password(password))

            user = authenticate(username=nationalcode, password=password)
            auth.login(request, user)
            if request.user.is_staff == False:

                return JsonResponse({'code': 1, 'url': '/user/dashboard', 'result': 'شما باموفقیت وارد شدید.'})
            else:
                return JsonResponse({'code': 1, 'url': '/panel/panel_profile', 'result': 'شما باموفقیت وارد شدید.'})
    return render(request, 'account/reset_password.html')


def login(request):
    if request.user.is_authenticated:  # redirect to profile
        if request.user.is_staff == False:
            return redirect('account:dashboard')
        else:
            return redirect('/panel/panel_profile')

    if request.method == 'POST':
        username = request.POST['nationalcode']
        password = request.POST['password']
        if username == '' or password == '':
            return JsonResponse({'result': 'فیلد های مورد نظر را پر کنید.'})

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if request.user.is_staff == False:

                return JsonResponse({'code': 1, 'url': '/user/dashboard', 'result': 'شما باموفقیت وارد شدید.'})
            else:
                return JsonResponse({'code': 1, 'url': '/panel/panel_profile', 'result': 'شما باموفقیت وارد شدید.'})


        else:
            return JsonResponse({'result': 'کد ملی یاپسورد اشتباه وارد شده است.'})

    else:
        return render(request, 'account/register&login.html')


def logout(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            auth.logout(request)
            return redirect('pages:index')
    else:
        return redirect('account:login')


@login_required(login_url='/user/login')
def dashboard(request):
    User = get_user_model()
    profile = User.objects.get(pk=request.user.id)
    profile_judo = Profile_Judo.objects.get(user_id=request.user.id)
    profile_jujitso = Profile_Jujitso.objects.get(user_id=request.user.id)
    if request.user.is_authenticated:  # redirect to profile
        if request.user.is_staff == True:
            return redirect('panel:panel_profile')
    if request.method == 'POST':
        try:

            if request.POST['tab_id'] == '2':
                password_old = request.POST['old_pass']
                password = request.POST['new_pass']
                passwordrepeat = request.POST['rep_pass']
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
                return JsonResponse({'code': 1, 'url': '/'})
            elif request.POST['tab_id'] == '1':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                birth_date = request.POST['birth_date']
                gender = request.POST['gender']
                address = request.POST['address']
                phone = request.POST['mobile']
                field = request.POST['field']
                if field not in ['0','1','2']:
                    field = 0

                if first_name == '':
                    return JsonResponse({'error': 'فیلد نام را تکمیل نمائید'})
                if last_name == '':
                    return JsonResponse({'error': 'فیلد نام خانوادگی را تکمیل نمائید'})
                if birth_date == '':
                    return JsonResponse({'error': 'فیلد تاریخ تولد را تکمیل نمائید'})
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



                if profile.national_document_image == '' and national_imgage == '':
                    return JsonResponse({'error': 'افزودن عکس مربوط ب کارت ملی الزامی می باشد.'})

                profile.gender = gender
                profile.phone = phone
                profile.first_name = first_name
                profile.last_name = last_name
                profile.birth_date = birth_date
                profile.interest = int(field)
                if national_imgage != '':
                    profile.national_document_image.delete()
                    profile.national_document_image = national_imgage



                profile.address = address
                profile.save()
                if request.is_ajax():
                    profile = User.objects.get(pk=request.user.id)
                    context = {'profile_info': profile, 'positions': Positions, 'genders': Genders}
                    html = render_to_string('site_pages/dashboard/load_pages/personal_information.html', context)
                    return HttpResponse(html)
            elif request.POST['tab_id'] == '3':
                coach_name = request.POST['coach_name']
                club_name = request.POST['club_name']
                position = request.POST['position']
                if position not in ['0', '1']:
                    position = 0

                qform = ''
                try:
                    qform = request.FILES['qform_document']
                    if str(qform.content_type).startswith('image'):
                        if qform.size < 5000000:
                            pass
                        else:

                            return JsonResponse({'error': 'سایز فایل نمی تواند بیش تر از ۵ مگابایت باشد.'})

                    else:
                        return JsonResponse({'error': 'فایل پشتیبانی نمی شود.'})

                except:
                    pass

                if profile_judo.qform_document == '' and qform == '':
                    return JsonResponse({'error': 'افزودن عکس مربوط به فرمq7 الزامی می باشد.'})

                profile_judo.coach_name = coach_name
                profile_judo.club_name = club_name
                if qform != '':
                    profile_judo.qform_document.delete()
                    profile_judo.qform_document = qform
                profile_judo.position = position
                profile_judo.save()

                if request.is_ajax():
                    profile_judo = Profile_Judo.objects.get(user_id=request.user.id)
                    context = {'profile_judo': profile_judo, 'positions': Positions}
                    html = render_to_string('site_pages/dashboard/load_pages/judo_profile.html', context)
                    return HttpResponse(html)

                return JsonResponse({'code': 1, 'result': 'اطلاعات با موفقیت ثبت شدند.', 'url': '/user/dashboard'})
            elif request.POST['tab_id'] == '4':
                coach_name = request.POST['coach_name']
                club_name = request.POST['club_name']
                position = request.POST['position']
                if position not in ['0', '1']:
                    position = 0

                profile_jujitso.coach_name = coach_name
                profile_jujitso.club_name = club_name

                profile_jujitso.position = position
                profile_jujitso.save()

                if request.is_ajax():
                    profile_jujitso = Profile_Jujitso.objects.get(user_id=request.user.id)
                    context = {'profile_jujitso': profile_jujitso, 'positions': Positions}
                    html = render_to_string('site_pages/dashboard/load_pages/jujitso_profile.html', context)
                    return HttpResponse(html)

            elif request.POST['tab_id'] == '0':
                personal_image = ''
                try:
                    personal_image = request.FILES['person_img']
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
                    profile.personal_image.delete()
                    profile.personal_image = personal_image
                profile.save()
                if request.is_ajax():
                    profile = User.objects.get(pk=request.user.id)
                    context = {'profile_info': profile}
                    html = render_to_string('site_pages/dashboard/load_pages/person_img.html', context)
                    return HttpResponse(html)


        except:
            return JsonResponse({'error': 'با خطا مواجه شدید.'})
    weights = Weight_Classification.objects.all()
    cpms = User_In_Competition.objects.filter(uid_id=request.user.id)
    context = {'profile_info': profile, 'profile_judo': profile_judo, 'profile_jujitso': profile_jujitso, 'genders': Genders, 'ages_period': Age_Period, 'positions': Positions, 'cmps': cpms, 'weights': weights}
    return render(request, 'site_pages/dashboard/index.html', context)
