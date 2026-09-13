from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from articles.models import Article, Category

class ArticleListView(View):
    def get(self, request):
        articles = Article.objects.filter(status=True)
        categories = Category.objects.filter(star=True)[:6]
        star_article = Article.objects.filter(status=True, star=True)[:4]

        paginator = Paginator(articles, 6)

        page = request.GET.get('page')
        try:
            article_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            article_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            article_list = paginator.page(paginator.num_pages)

        context = {
            'article_list':article_list,
            'categories':categories,
            'star_article':star_article,
        }
        return render(request, 'articles/article_list.html', context)
    

class ArticleDetailView(View):
    def get(self, request, article_slug):
        the_article = get_object_or_404(Article, slug=article_slug)
        categories = Category.objects.filter(star=True)[:6]
        star_article = Article.objects.filter(status=True, star=True)[:4]

        if the_article.status == False:
            messages.error(request, "مقاله مورد نظر از دسترس خارج میباشد", 'danger')
            return redirect('articles:article_list')

        context = {
            'the_article':the_article,
            'categories':categories,
            'star_article':star_article,
        }
        return render(request, 'articles/article_detail.html', context)
    

class ArticleSearchResultView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        # Start with articles that are published.
        articles = Article.objects.filter(status=True)
        categories = Category.objects.filter(star=True)[:6]
        star_article = Article.objects.filter(status=True, star=True)[:4]

        if query:
            vector = SearchVector('title', weight='A')
            search_query = SearchQuery(query)
            
            # Annotate articles with a rank based on the search match.
            articles = articles.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1)  # Adjust threshold as needed.

            # Order results by the search rank in descending order.
            articles = articles.order_by('-rank')

        paginator = Paginator(articles, 6)
        page_number = request.GET.get('page')
        try:
            articles_page = paginator.page(page_number)
        except PageNotAnInteger:
            articles_page = paginator.page(1)
        except EmptyPage:
            articles_page = paginator.page(paginator.num_pages)
        
        context = {
            'query': query,
            'article_list': articles_page,
            'categories':categories,
            'star_article':star_article,
        }
        return render(request, 'articles/article_search_result.html', context)
    

class ArticleCategoryView(View):
    def get(self, request, category_slug):
        the_category = get_object_or_404(Category, slug=category_slug)
        related_articles = the_category.blog.filter(status=True)
        categories = Category.objects.filter(star=True)[:6]
        star_article = Article.objects.filter(status=True, star=True)[:4]

        paginator = Paginator(related_articles, 6)

        page = request.GET.get('page')
        try:
            article_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            article_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            article_list = paginator.page(paginator.num_pages)

        context = {
            'article_list':article_list,
            'categories':categories,
            'star_article':star_article,
            'cat_title':the_category.title,
        }
        return render(request, 'articles/article_category.html', context)