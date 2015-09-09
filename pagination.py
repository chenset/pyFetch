from math import ceil


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
        self.query = query
        #: current page number
        self.page = page
        #: number of items to be displayed per page
        self.per_page = per_page
        #: total number of items matching the query
        self.total = None
        #: list of items for the current page
        self.items = items

    def pages(self):
        """The total number of pages"""
        if self.total is None:
            self.total = self.query.count()

        return int(ceil(self.total / float(self.per_page)))

    def current_page(self):
        return self.items

    def next_page(self):
        """The next page number."""
        return self.page + 1

    def has_next(self):
        """Returns ``True`` if a next page exists."""
        return self.page < self.pages

    def next(self, error_out=False):
        """Return a :class:`Pagination` object for the next page."""
        return paginate(self.query, self.page + 1, self.per_page, error_out)

    def prev_page(self):
        """The previous page number."""
        return self.page - 1

    def has_prev(self):
        """Returns ``True`` if a previous page exists."""
        return self.page > 1

    def prev(self, error_out=False):
        """Return a :class:`Pagination` object for the previous page."""
        return self.query.paginate(self.query, self.page - 1, self.per_page, error_out)