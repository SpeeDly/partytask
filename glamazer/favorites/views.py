from time import time

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from glamazer.core.helpers import get_object_or_None, current_time
from glamazer.listings.models import Listing
from glamazer.favorites.models import Favorite
from glamazer.notifications.models import Notification
from glamazer.settings import NOTIFICATIONS_SHORT, NOTIFICATIONS_LONG


def add(request, listing_id):
    listing_id = int(listing_id)
    user = request.user
    listing = Listing.objects.select_related("artist").get(id=listing_id)

    flag = get_object_or_None(Favorite, user=user, listing=listing)

    if not flag:
        listing.likes = listing.likes + 1
        listing.save()
        Favorite.objects.create(user=user, listing=listing)
        Notification.objects.create(
                        sender = user, 
                        receiver = listing.artist.user,
                        time = current_time(),
                        short_text = NOTIFICATIONS_SHORT[7].format(user=user.first_name),
                        long_text = NOTIFICATIONS_LONG[7].format(user=user.first_name, listing=listing.title, user_id=user.id, metadata=listing_id),
                    )
    else:
        listing.likes = listing.likes - 1
        listing.save()
        flag.delete()

    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id}))