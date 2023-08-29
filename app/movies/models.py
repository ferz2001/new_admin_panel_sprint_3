import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class FilmWorkType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("tv_show")


class RoleType(models.TextChoices):
    actor = 'actor', _('Actor')
    writer = 'writer', _('Writer')
    director = 'director', _('Director')


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True, null=True)
    modified = models.DateTimeField(_('modified'), auto_now=True, null=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(_('title'))
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateTimeField(_('creation_date'),
                                         auto_now_add=True,
                                         null=True)
    type = models.CharField(
        'Тип',
        max_length=12,
        choices=FilmWorkType.choices,
    )
    rating = models.FloatField(_("rating"), blank=True, null=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)],)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork', verbose_name=_('genres'))
    persons = models.ManyToManyField(Person, through='PersonFilmwork', verbose_name=_('persons'))

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _("film_work")
        verbose_name_plural = _("film_works")
        indexes = [
            models.Index(
                fields=['creation_date', 'rating'],
                name='fw_creation_date_rating_idx'
            ),
            models.Index(fields=['rating'], name='fw_rating_idx'),
            models.Index(fields=['title'], name='fw_title_idx'),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('genre_film_work')
        constraints = [
            models.UniqueConstraint(
                fields=['film_work_id', 'genre_id'],
                name='film_work_id_genre_id_uniq_idx'
            )
        ]


class PersonFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('Role'),
                            max_length=15,
                            blank=True,
                            choices=RoleType.choices)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('person_film_work')
        constraints = [
            models.UniqueConstraint(fields=[_('role'),
                                            _('person'),
                                            _('film_work')],
                                    name='film_work_person_idx')
        ]
