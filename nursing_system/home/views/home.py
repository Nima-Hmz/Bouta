from django.views import View
from django.shortcuts import render, redirect
from articles.models import IndexTemplateModel, Article, ServiceTemplateModel, FrequentQuestionsTemplateModel, \
    ContactUsTemplateModel, TermsTemplateModel, HistoryTemplateModel
from nurse_users.models import NurseUserAdditionalInfo

class IndexView(View):
    def get(self, request):
        index_info = IndexTemplateModel.objects.first()
        star_articles = Article.objects.filter(status=True, star=True)[:5]
        star_nurses = NurseUserAdditionalInfo.objects.filter(star=True).order_by('-id')[:3]

        for rr in star_nurses:
            if rr.average_rating:
                rr.full_stars = int(rr.average_rating)
                rr.has_half_star = (rr.average_rating - rr.full_stars) >= 0.5
            else:
                rr.full_star = None
                rr.has_half_star = False
    
        context = {
            'index_info':index_info,
            'star_articles':star_articles,
            'star_nurses':star_nurses,
        }
        return render(request, 'home/index.html', context)

class AboutUsView(View):
    def get(self, request):
        index_info = IndexTemplateModel.objects.first()
        star_articles = Article.objects.filter(status=True, star=True)[:5]
        questions = FrequentQuestionsTemplateModel.objects.filter(display_about=True)
        context = {
            'index_info':index_info,
            'star_articles':star_articles,
            'questions':questions,
        }
        return render(request, 'home/about_us.html', context)
    
class ContactView(View):
    def get(self, request):
        contact_us = ContactUsTemplateModel.objects.first()
        context = {
            'contact_us':contact_us,
        }
        return render(request, 'home/contact.html', context)
    
class FAQView(View):
    def get(self, request):
        questions = FrequentQuestionsTemplateModel.objects.all()
        star_articles = Article.objects.filter(status=True, star=True)[:5]
        context = {
            'questions':questions,
            'star_articles':star_articles,
        }
        return render(request, 'home/faq.html', context)
    
class HistoryView(View):
    def get(self, request):
        history = HistoryTemplateModel.objects.first()
        star_articles = Article.objects.filter(status=True, star=True)[:5]
        context = {
            'history':history,
            'star_articles':star_articles,
        }
        return render(request, 'home/history.html', context)
    
class ServiceView(View):
    def get(self, request):
        service_info = ServiceTemplateModel.objects.first()
        star_articles = Article.objects.filter(status=True, star=True)[:5]
        context = {
            'service_info':service_info,
            'star_articles':star_articles,
            }
        return render(request, 'home/service.html', context)
    
class TermsView(View):
    def get(self, request):
        terms = TermsTemplateModel.objects.first()
        context = {
            'terms':terms,
        }
        return render(request, 'home/terms.html', context)
    