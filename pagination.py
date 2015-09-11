from math import ceil, floor


def paginate(mongo_cursor, page, per_page=20, error_out=True):
    """Returns ``per_page`` items from page ``page`` By default, it will
    abort with 404 if no items were found and the page was larger than 1.
    This behaviour can be disabled by setting ``error_out`` to ``False``.
    Returns a :class:`Pagination` object."""
    if page < 1 and error_out:
        return None

    items = list(mongo_cursor.skip((page - 1) * per_page).limit(per_page))
    if not items and page != 1 and error_out:
        return None

    return Pagination(mongo_cursor, page, per_page, items)


class Pagination(object):
    """Internal helper class returned by :meth:`~BaseQuery.paginate`."""

    def __init__(self, query, page, per_page, items):
        #: query object used to create this
        #: pagination object.
        self._query = query
        #: current page number
        self._page = page
        #: number of items to be displayed per page
        self.per_page = per_page
        #: total number of items matching the query
        self._total = None
        #: list of items for the current page
        self._items = items

    def render_json(self, page_limit, url_patten='page='):
        page_list = []
        start_page = int(self.current_page() - floor(page_limit / 2))
        end_page = int(self.current_page() + ceil(page_limit / 2))

        if start_page < 1:
            end_page += 1 - start_page

        if end_page > self.count():
            start_page -= self.count() - end_page
            end_page = self.count()

        if start_page < 1:
            start_page = 1

        for i in xrange(start_page, end_page):
            page_list.append(url_patten + str(i))

        return {
            'total': self.total(),
            'count': self.count(),
            'page_list': page_list,
            'current_page': url_patten + str(self._page),
            'prev_page': url_patten + str(self.prev_page()) if self.prev_page() else '',
            'next_page': url_patten + str(self.next_page()) if self.next_page() else '',
            'first_page': url_patten + '1',
            'last_page': url_patten + str(self.count()),
        }

    def render_view(self, url_patten='page='):
        pass

    def total(self):
        """The total number of documents"""
        if self._total is None:
            self._total = self._query.count()

        return self._total

    def count(self):
        """The count number of pages"""
        return int(ceil(self.total() / float(self.per_page)))

    def current_page(self):
        return self._page

    def result(self):
        return self._items

    def next_page(self):
        """The next page number."""
        return self._page + 1 if self.has_next() else None

    def has_next(self):
        """Returns ``True`` if a next page exists."""
        return self._page < self.count()

    def next(self, error_out=False):
        """Return a :class:`Pagination` object for the next page."""
        if not self.has_next():
            return None

        return paginate(self._query, self._page + 1, self.per_page, error_out)

    def prev_page(self):
        """The previous page number."""
        return self._page - 1 if self.has_prev() else None

    def has_prev(self):
        """Returns ``True`` if a previous page exists."""
        return self._page > 1

    def prev(self, error_out=False):
        """Return a :class:`Pagination` object for the previous page."""
        if not self.has_prev():
            return None

        return self._query.paginate(self._query, self._page - 1, self.per_page, error_out)