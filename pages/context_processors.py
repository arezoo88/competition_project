from .models import Company_Info
from news.models import Category_News
def footer_info(request):
    cat_news = Category_News.objects.all()[0:15]
    company_Info = Company_Info.objects.all()
    if company_Info.count() == 0:
        obj = {'phone': '', 'fax': '', 'address': ''}
    else:
        obj = company_Info[0]

    return {'info':obj,'cat_news':cat_news}

