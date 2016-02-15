import redis

from django.db import models
from django.http import HttpResponse, HttpResponseServerError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    receiver = models.ForeignKey(User, related_name='receiver')
    time = models.IntegerField()
    short_text = models.TextField()
    long_text = models.TextField()
    is_readed = models.BooleanField(default=False)
    class Meta:
        ordering = ['-time']

    def sender_link(self):
        url = None
        if self.sender.related_with == 'profiles':
            url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.sender.profile.id, )), self.sender.first_name)
        elif self.sender.related_with == 'artists':
            url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.sender.artist.id, )), self.sender.first_name)
        return url

    def receiver_link(self):
        url = None
        if self.receiver.related_with == 'profiles':
            url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.receiver.profile.id, )), self.receiver.first_name)
        elif self.receiver.related_with == 'artists':
            url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.receiver.artist.id, )), self.receiver.first_name)
        return url


    sender_link.allow_tags = True
    sender_link.short_description = "Sender"

    receiver_link.allow_tags = True
    receiver_link.short_description = "Receiver"


@receiver(post_save, sender=Notification)
def send_notifications(sender, instance,**kwargs):
    try:
        receiver_id = instance.receiver_id
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.publish('notification_count', receiver_id, instance.long_text)
        return HttpResponse("Everything worked :)")
    except Exception as e:
        return HttpResponseServerError(str(e))