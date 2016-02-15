from django.db import models
from django.contrib.auth.models import User

from glamazer.settings import NOTIFICATIONS_SHORT, NOTIFICATIONS_LONG
from glamazer.notifications.models import Notification
from glamazer.artists.models import Artist
from glamazer.core.helpers import current_time
from glamazer.core.emails import send_email


class Followers(models.Model):
    user = models.ForeignKey(User)
    artist = models.ForeignKey(Artist)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, **kwargs):
        if self.id:
            super(Followers, self).save(force_insert, force_update)
        else:
            super(Followers, self).save(force_insert, force_update)
            if self.user.related_with == 'profiles':
                link_1 = '/users/profile/' + str(self.user.profile.id)
            elif self.user.related_with == 'artists':
                link_1 = '/artists/profile/' + str(self.user.artist.id)
            else:
                link_1 = '/salons/profile/' + str(self.user.salon.id)

            Notification.objects.create(
                            sender = self.user,
                            receiver = self.artist.user,
                            time = current_time(),
                            short_text = NOTIFICATIONS_SHORT[6].format(user=self.user.first_name),
                            long_text = NOTIFICATIONS_LONG[6].format(user=self.user.first_name, link_1=link_1),
                        )
            kwargs = {}
            kwargs['username'] = self.user.first_name
            kwargs['count'] = Followers.objects.filter(artist=self.artist).count()
            kwargs['id'] = self.artist.id
            send_email(case=8, receiver=self.artist.user, **kwargs)