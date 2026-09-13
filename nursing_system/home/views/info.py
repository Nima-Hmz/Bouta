from django.views import View 
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from nurse_users.models import SubSkill

class ServicePricingView(View):
    def get(self, request):
        subskills_list = SubSkill.objects.all()
        paginator = Paginator(subskills_list, 10)  # Show 10 subskills per page
        
        page = request.GET.get('page')
        try:
            subskills = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            subskills = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            subskills = paginator.page(paginator.num_pages)
        
        context = {
            'subskills': subskills
        }
        return render(request, 'info/service_pricing.html', context)