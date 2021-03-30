from django.core.paginator import Paginator


class PaginationUtilities:

    @staticmethod
    def paginate_results(queryset, page_number, page_size=10):
        """function to create pagination and return a query set for page number"""
        paginator = Paginator(queryset, page_size)
        max_page = len(paginator.page_range)

        return [] if (max_page < int(page_number)) else paginator.get_page(page_number)
