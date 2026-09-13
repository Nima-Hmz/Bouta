from articles.models import BaseTemplateModel

def base_template_processor(request):
    base_template_model = BaseTemplateModel.objects.first()
    output = {
        'base_info':base_template_model,
    }
    return output
