from django.shortcuts import render, get_object_or_404, redirect
from .models import News, Category_News


def news_list(request):
    cat = request.GET.get('cat', None)
    title = request.GET.get('title', '')
    news_lists = News.objects.order_by('-pk').filter(is_published=True)

    if not (cat == None or cat == ''):
        news_lists = news_lists.filter(category__title__iexact=cat, is_published=True)

    if not (title == None or title == ''):
        news_lists = news_lists.filter(title__icontains=title)

    cats = Category_News.objects.all()
    context = {'news_lists': news_lists, 'cats': cats, 'selected_cat': cat, 'title_search': title}
    return render(request, 'site_pages/news/news_list.html', context)


def news_detail(request, news_id):
    try:
        news_detail = get_object_or_404(News, pk=news_id, is_published=True)
        context = {
            'news_detail': news_detail
        }
        return render(request, 'site_pages/news/news_detail.html', context)
    except:
        return redirect('news:news_list')
