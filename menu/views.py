from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'menu/main.html'
