import datetime

from django.db import models
from django.core.urlresolvers import reverse

from glamazer.notifications.models import Notification
from glamazer.listings.models import Listing
from glamazer.artists.models import Artist, CancellationPolicy, CancellationRate
from glamazer.users.models import Profile
from glamazer.core.helpers import current_time
from glamazer.core.emails import send_email
from glamazer.settings import STATUS, NOTIFICATIONS_LONG, NOTIFICATIONS_SHORT


class Booking(models.Model):
    artist = models.ForeignKey(Artist, null=True)
    client = models.ForeignKey(Profile)
    listing = models.ForeignKey(Listing)
    cancellation_policy = models.ForeignKey(CancellationPolicy)
    price = models.FloatField(default=0)
    revenue = models.FloatField(default=0)
    title = models.TextField(blank=True, null=True)
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=0)
    cancelled_by = models.IntegerField(default=0)
    is_mailed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')

    def get_status(self):
        return STATUS[self.status]

    def artist_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.artist_id, )), self.artist.user.first_name)
        return url

    def client_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.client_id, )), self.client.user.first_name)
        return url

    def listing_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:listings_listing_change"), args=(self.listing_id, )), self.listing.title)
        return url


    artist_link.allow_tags = True
    artist_link.short_description = "Artist"
    
    client_link.short_description = 'Client'
    client_link.allow_tags = True

    listing_link.allow_tags = True
    listing_link.short_description = "Listing"

    def save(self, force_insert=False, force_update=False, old_status=None, **kwargs):
        if self.id:
            cancelled_by = self.cancelled_by
            super(Booking, self).save(force_insert, force_update)
            print("start_function", cancelled_by, old_status, self.status)
            if cancelled_by == 1 and not old_status == self.status:
                '''The real tricky moment here is the notation for nb 1 - the booking is approved, 2 - rejected, 3 declined'''
                notificated_user = self.client.user
                artist_user = self.artist.user
                if self.status == 1:
                    nb = 1
                    cr = CancellationRate.objects.get(artist=self.artist)
                    cr.approved += 1
                    cr.save()
                elif self.status == 2:
                    if old_status == 0:
                        nb = 2
                    else:
                        nb = 3
                        cr = CancellationRate.objects.get(artist=self.artist)
                        cr.cancelled += 1
                        cr.save()

                Notification.objects.create(
                    sender = artist_user,
                    receiver = notificated_user,
                    time = current_time(),
                    short_text = NOTIFICATIONS_SHORT[nb].format(artist=artist_user.first_name),
                    long_text = NOTIFICATIONS_LONG[nb].format(artist=artist_user.first_name, listing=self.listing.title, user_id=self.artist_id, metadata=self.listing_id),
                )

                kwargs = {}

                if nb == 1:
                    kwargs['listing'] = self.listing
                    kwargs['artistname'] = self.artist.user.first_name
                    kwargs['when'] = self.start_time
                    send_email(case=12, receiver=notificated_user, **kwargs)
                elif nb == 2:
                    kwargs['artistname'] = self.artist.user.first_name
                    send_email(case=13, receiver=notificated_user, **kwargs)
                elif nb == 3:
                    kwargs['artistname'] = self.artist.user.first_name
                    kwargs['when'] = self.start_time
                    kwargs['listing_id'] = self.listing_id
                    send_email(case=13, receiver=notificated_user, **kwargs)

            elif cancelled_by == 2 and not old_status == self.status:

                profile_user = self.client.user
                artist_user = self.artist.user
                Notification.objects.create(
                    sender = profile_user,
                    receiver = artist_user,
                    time = current_time(),
                    short_text = NOTIFICATIONS_SHORT[4].format(user=profile_user.first_name),
                    long_text = NOTIFICATIONS_LONG[4].format(user=profile_user.first_name, listing=self.listing.title, user_id=self.client_id, metadata=self.listing_id),
                )

                kwargs = {}
                # when user cancel an apoinment
                if old_status == 2:
                    delta_time = self.start_time - current_time()
                    kwargs['username'] = profile_user.first_name
                    kwargs['when'] = self.start_time 
                    kwargs['day_before'] = round(delta_time/86400)
                    if delta_time > 150000:
                        send_email(case=14, receiver=artist_user, **kwargs)
                    else:
                        send_email(case=15, receiver=artist_user, **kwargs)
        else:
            super(Booking, self).save(force_insert, force_update)
            user = self.client.user
            Notification.objects.create(
                        sender = user, 
                        receiver = self.artist.user,
                        time = current_time(),
                        short_text = NOTIFICATIONS_SHORT[0].format(user=user.first_name),
                        long_text = NOTIFICATIONS_LONG[0].format(user=user.first_name, listing=self.title, user_id=self.client_id, metadata=self.listing_id),
                    )
            kwargs = {}
            kwargs['listing'] = self.listing
            kwargs['username'] = user.first_name
            send_email(case=10, receiver=self.artist.user, **kwargs)


class DummyBooking(models.Model):
    artist = models.ForeignKey(Artist)
    client = models.ForeignKey(Profile)
    listing = models.ForeignKey(Listing)
    cancellation_policy = models.ForeignKey(CancellationPolicy)
    price = models.FloatField(default=0)
    title = models.TextField(blank=True, null=True)
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
