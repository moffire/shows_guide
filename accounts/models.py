from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from shows.models import Movie, Episode

User = get_user_model()

class UserProfile(User):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	avatar = models.ImageField(upload_to='users_logo/', blank=True)

class Sub(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subs')
	movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name='subs')

	def __str__(self):
		return "{} :: {}".format(self.movie.first_title, self.movie.second_title)

class SubEpisode(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_episodes')
	sub = models.ForeignKey(Sub, on_delete=models.CASCADE, related_name='viewed_episodes')
	episode = models.OneToOneField(Episode, on_delete=models.CASCADE)
	is_viewed = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()