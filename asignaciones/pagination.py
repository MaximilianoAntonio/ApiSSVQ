"""
Paginador personalizado que fuerza HTTPS en las URLs de paginación
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class HTTPSPageNumberPagination(PageNumberPagination):
    """
    Paginador personalizado que fuerza HTTPS en las URLs de paginación
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Sobrescribir para forzar HTTPS en las URLs de navegación
        """
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        
        # Forzar HTTPS en las URLs si existen
        if next_url and next_url.startswith('http://'):
            next_url = next_url.replace('http://', 'https://')
        
        if previous_url and previous_url.startswith('http://'):
            previous_url = previous_url.replace('http://', 'https://')
        
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', next_url),
            ('previous', previous_url),
            ('results', data)
        ]))

    def get_next_link(self):
        """
        Obtener siguiente enlace con HTTPS forzado
        """
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        
        # Forzar HTTPS
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        
        page_number = self.page.next_page_number()
        return self.replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        """
        Obtener enlace anterior con HTTPS forzado
        """
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        
        # Forzar HTTPS
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return self.remove_query_param(url, self.page_query_param)
        return self.replace_query_param(url, self.page_query_param, page_number)
