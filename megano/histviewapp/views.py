from django.shortcuts import render, redirect
from django.views import View
from histviewapp.services.history import HistoryService


class HistProductsView(View):
    TEMPLATE_NAME = 'hist_views_products.jinja2'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        viewed_products = HistoryService.get_history(request.user)
        return render(request, self.TEMPLATE_NAME, {'dealers': viewed_products})