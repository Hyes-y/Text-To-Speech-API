from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """ 한 페이지에 10개 항목을 보여주는 Custom Pagination """
    page_size = 10
