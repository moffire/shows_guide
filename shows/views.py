from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.postgres.search import SearchVector

from .models import Movie


class BaseListView(ListView):
	model = Movie
	ordering = ('-imdb',)
	paginate_by = 9
	template_name = 'shows/main_content.html'
	context_object_name = 'movies_list'


class MainPageView(BaseListView):
	allow_empty = False

	def get_context_data(self, **kwargs):
		# add to context 10 random top rated movies for carousel

		context = super().get_context_data(**kwargs)
		context['random_top_movies'] = Movie.objects.filter(imdb__gte=9).order_by('-kp')[:10]
		return context


class RatingView(BaseListView):

	def get_queryset(self):
		rating = self.kwargs.get('rating', None)
		allowed_kwargs = ('top_250', 'top_imdb', 'top_kp')

		if not rating:
			return super().get_queryset()

		if rating not in allowed_kwargs:
			return None
		else:
			if rating == 'top_250':
				# get objects with the biggest average rating score
				unsorted_results = Movie.objects.filter(Q(imdb__gte=7) & Q(kp__gte=7))
				return sorted(unsorted_results, key=lambda avg: avg.get_average(), reverse=True)[:250]
			elif rating == 'top_imdb':
				return Movie.objects.order_by('-imdb')[:100]
			elif rating == 'top_kp':
				return Movie.objects.order_by('-kp')[:100]


class SearchView(BaseListView):
	allow_empty = True

	def get_queryset(self):
		vector = SearchVector('first_title', 'second_title')
		return Movie.objects.annotate(search=vector).filter(search=self.request.GET.get('q'))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		search_params = self.request.GET.get('q', None)
		if search_params:
			context['q'] = f"q={self.request.GET.get('q', None)}&"

		return context


class MovieDetail(DetailView):
	model = Movie
	template_name = 'shows/item_content.html'
	context_object_name = 'movie'
	pk_url_kwarg = 'external_id'

	def get_object(self, queryset=None):
		movie = get_object_or_404(Movie.objects.select_related(), external_id=self.kwargs['external_id'])
		return movie
