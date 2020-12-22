from django.db import models
from django.urls import reverse

class Movie(models.Model):
    external_id = models.IntegerField(db_index=False, unique=True)
    first_title = models.CharField(max_length=200, blank=True, db_index=True)
    second_title = models.CharField(max_length=200, blank=True, db_index=True)
    description = models.TextField(max_length=1000, blank=True)
    start_date = models.DateField(null=True, blank=True, editable=False)
    end_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100)
    imdb = models.DecimalField(max_digits=5, decimal_places=3)
    kp = models.DecimalField(max_digits=5, decimal_places=3)
    poster = models.ImageField(upload_to='images/', blank=True)

    def get_absolute_url(self):
        return reverse('shows:detail', args=[int(self.external_id)])

    """average rating score"""
    def get_average(self):
        return (self.imdb + self.kp) / 2

    def __str__(self):
        return "{} :: {}".format(self.first_title, self.second_title)


class Season(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='seasons', to_field='external_id')
    number = models.IntegerField()

    def __str__(self):
        return "Season №{} / {}".format(self.number, self.movie.first_title)


class Episode(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='episodes', to_field='external_id')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    number = models.IntegerField()
    name = models.CharField(max_length=200, blank=True)
    date = models.DateField(editable=False, null=True, blank=True)

    def __str__(self):
        return "Episode №{} / Season №{} / {}".format(self.number, self.season.number, self.movie.first_title)