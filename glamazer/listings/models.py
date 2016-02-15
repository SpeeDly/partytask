import os

from pyelasticsearch import ElasticSearch

from haystack.utils.geo import Point
from sorl.thumbnail import get_thumbnail

from django.db import models

from glamazer.settings import MEDIA_ROOT, ELASTIC_SEARCH_URL, NOTIFICATIONS_SHORT, NOTIFICATIONS_LONG, LISTING_STATUS
from glamazer.core.helpers import current_time, get_rate
from glamazer.followers.models import Followers
from glamazer.notifications.models import Notification
from glamazer.artists.models import Artist


class Listing(models.Model):
    
    artist = models.ForeignKey(Artist)
    picture = models.CharField(max_length=128, help_text='The path to the images. Never change it.')
    picture_cover = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    description = models.TextField()
    price = models.FloatField()
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    metadata = models.CharField(max_length=16)
    duration = models.IntegerField(default=0, help_text="1800=00:30 | 3600=1:00 | 5400=1:30 | 7200=2:00 | 9000=2:30 | 10800=3:00 | 12600=3:30 | 14400=4:00")
    status = models.IntegerField(default=0, choices=LISTING_STATUS)
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_style(self):
        return self.artist.get_style()

    def get_picture(self):
        return self.picture_cover

    def get_all_pictures(self):
        pictures = []
        cover = self.picture_cover.split("/")[-1]
        full_path = MEDIA_ROOT + self.picture[7:]
        for p in os.listdir(full_path):
            if not p == cover:
                pictures.append(full_path + p)
        return pictures

    def get_location(self):
        return Point(self.artist.lng, self.artist.lat)

    def get_artist_avatar(self):
        return self.artist.get_avatar()

    def get_artist_id(self):
        return self.artist.id

    def get_artist_avatar(self):
        return self.artist.get_avatar()

    def get_tags(self):
        listings = ListingTags.objects.filter(listing=self).select_related("tags")
        return [x.tags.tag for x in listings]

    def get_rating(self):
        from glamazer.reviews.models import Review
        reviews = Review.objects.select_related().filter(listing=self)
        rate = get_rate(reviews)
        return rate

    def view_all_pictures(self):
        all_pictures = self.get_all_pictures()
        all_pictures.append(self.get_picture())
        thumbs = '<ul>'
        for pic in all_pictures:
            print(get_thumbnail(pic, '240x143', crop='center', quality=99))
            thumbs += '<li><img src="'
            thumbs +=  get_thumbnail(pic, '240x143', crop='center', quality=99).url
            thumbs +=  '"/></li>'
        return thumbs

    view_all_pictures.allow_tags = True
    view_all_pictures.short_description = "Pictures"
    

    def save(self, force_insert=False, force_update=False, **kwargs):
        es = ElasticSearch(ELASTIC_SEARCH_URL)
        if self.id:
            location = self.get_location()
            location_es = "{0},{1}".format(location.y, location.x)
            es.update('glamazer', 'modelresult', 'listings.listing.{0}'.format(self.id),
                script="ctx._source.listing_id = listing;" +
                "ctx._source.artist_id = artist;" +
                "ctx._source.artist_avatar = artist_avatar;" +
                "ctx._source.title = title;" +
                "ctx._source.location = location;" +
                "ctx._source.description = description;" +
                "ctx._source.get_picture = get_picture;" +
                "ctx._source.metadata = metadata;" +
                "ctx._source.price = price;" +
                "ctx._source.likes = likes;" +
                "ctx._source.comments = comments;" +
                "ctx._source.tags = tags;" +
                "ctx._source.status = status;" +
                "ctx._source.style = style;" +
                "ctx._source.rating = rating",
                params={
                    'listing':self.id, 
                    'artist':self.get_artist_id(),
                    'artist_avatar':self.get_artist_avatar(),
                    'title':self.title,
                    'location':location_es,
                    'description':self.description, 
                    'get_picture':self.get_picture(),
                    'metadata':self.metadata,
                    'price':self.price,
                    'likes':self.likes,
                    'comments':self.comments,
                    'tags':self.get_tags(),
                    'status':self.status,
                    'style':self.get_style(),
                    'rating':self.get_rating()
                    })
            super(Listing, self).save(force_insert, force_update)
        else:
            super(Listing, self).save(force_insert, force_update)

            artist_user = self.artist.user
            artist_name = artist_user.first_name
            followers = Followers.objects.select_related().filter(artist=self.artist)
            for follower in followers:
                Notification.objects.create(
                    sender = artist_user,
                    receiver = follower.user,
                    time = current_time(),
                    short_text = NOTIFICATIONS_SHORT[10].format(artist=artist_name),
                    long_text = NOTIFICATIONS_LONG[10].format(artist=artist_name, listing=self.title, user_id=self.artist_id, metadata=self.id),
                )

            location = self.get_location()
            location_es = "{0},{1}".format(location.y, location.x)
            es.index('glamazer', 'modelresult', 
                {
                    'listing_id': self.id,
                    'artist_id': self.artist_id,
                    'artist_avatar':self.get_artist_avatar(),
                    'title': self.title,
                    'location': location_es,
                    'description': self.description,
                    'get_picture': self.get_picture(),
                    'metadata': self.metadata,
                    'price': self.price,
                    'likes': self.likes,
                    'comments':self.comments,
                    'tags': self.get_tags(),
                    'status':self.status,
                    'style':self.get_style(),
                    'rating':self.get_rating()
                }, id='listings.listing.{0}'.format(self.id))
            es.refresh('glamazer')


class Tags(models.Model):
    tag = models.TextField()


class ListingTags(models.Model):
    listing = models.ForeignKey(Listing)
    tags = models.ForeignKey(Tags)


class ListingView(models.Model):
    listing = models.ForeignKey(Listing)
    date = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)