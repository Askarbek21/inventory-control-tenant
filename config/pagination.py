from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages
        page_range = self.get_page_range(current_page, total_pages)

        return Response({
            'links': {
                'first': self.page.paginator.page(1).number if total_pages > 1 else None,
                'last': self.page.paginator.page(total_pages).number if total_pages > 1 else None,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'total_pages': total_pages,
            'current_page': current_page,
            'page_range': page_range,
            'page_size': self.page_size,
            'results': data,
            'count': self.page.paginator.count,

        })

    def get_page_range(self, current_page, total_pages, visible_pages=8):
        if total_pages <= visible_pages:
            return list(range(1, total_pages + 1))
        half_page = visible_pages // 2
        if current_page <= half_page:
            return list(range(1, visible_pages + 1)) + ["...", total_pages]
        if ((total_pages - visible_pages) + 1) < current_page:
            return [1, "..."] + list(range(((total_pages - visible_pages) + 1), total_pages + 1))
        return (
                [1, "..."] + list(range(current_page - 2, current_page + 3)) + ["...", total_pages]
        )
