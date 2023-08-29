from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, RoleType


class MoviesApiMixin:
    http_method_names = ['get']
    model = Filmwork

    def get_queryset(self):
        actors = ArrayAgg(
            'persons__full_name',
            distinct=True,
            filter=Q(personfilmwork__role=RoleType.actor),
        )
        directors = ArrayAgg(
            'persons__full_name',
            distinct=True,
            filter=Q(personfilmwork__role=RoleType.director),
        )
        writers = ArrayAgg(
            'persons__full_name',
            distinct=True,
            filter=Q(personfilmwork__role=RoleType.writer),
        )
        genres = ArrayAgg(
            'genres__name',
            distinct=True,
        )

        return self.model.objects.prefetch_related(
            'genres',
            'persons',
        ) \
            .values().annotate(
                actors=actors,
                directors=directors,
                writers=writers,
                genres=genres,
             )

    @staticmethod
    def render_to_response(context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by
        )

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.object