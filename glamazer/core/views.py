import datetime


from haystack.query import SQ, SearchQuerySet
from haystack.utils.geo import Point, D

from django.http import HttpResponse, Http404
from django.db import connection
from django.db.models import Q
from django.utils import simplejson
from django.shortcuts import render

from glamazer.listings.models import Listing, Tags
from glamazer.core.helpers import dictfetchall
from glamazer.settings import STYLE_INDEXES, MEDIA_ROOT


def home(request):
    listings = Listing.objects.select_related("artist").filter(status=1).order_by('?')[:20]
    return render(request, 'core/home.html', {"listings": listings})


def base(request):
    path = request.path.strip('/')
    # path_list = {'venues': 'Venues',
    #              'catering': 'Catering',
    #              'drinks': 'Drinks',
    #              'music': 'Music',
    #              'entertainment': 'Entertainment',
    #              'equipment': 'Equipment',
    #              'decoration': 'Decoration',
    #              'party': 'Party'
    #              }
    path_list = {'venues': 'Venues',
                 'catering': 'Catering',
                 'drinks': 'Drinks',
                 'music': 'Music',
                 'entertainment': 'Entertainment',
                 'equipment': 'Equipment',
                 'decoration': 'Decoration',
                 'party': 'Party',
                 'more': 'Music, Entertainment, Equipment, Decoration, Party',
                 }
    print(path)
    try:
        path_name = path_list[path]
    except:
        raise Http404

    _listings = SearchQuerySet().models(Listing).filter(style=path_name, status=1)


    price_list = [l.price for l in _listings]
    try:
        price_list = [min(price_list), max(price_list)]
    except:
        price_list = [0, 500]
    price_list = [min(price_list), max(price_list)]

    listings = []
    listing = {}
    for l in _listings:
        listing = {}
        listing["lat"] = l.location.x
        listing["lng"] = l.location.y
        listing["id"] = l.listing_id
        listing["picture"] = l.get_picture
        listing["style"] = l.style
        listing["title"] = l.title
        listing["likes"] = l.likes
        listing["price"] = int(l.price)
        listing["comments"] = l.comments
        listing["artist_id"] = l.artist_id
        listing["avatar"] = l.artist_avatar
        listings.append(listing)

    return render(request, 'service/service.html', { 'listings': listings, "price_list": price_list})


def autocomplete_tags(request):
    result = Tags.objects.filter(tag__contains=request.GET["q"])
    if result:
        data = [r.tag for r in result]
    else:
        data = {}
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def search(request):
    query = request.GET.get("q", None)
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    budget = request.GET.get("budget", None)
    gender = request.GET.get("gender", None)
    rating = request.GET.get("rating", None)
    date = request.GET.get("date", None)
    hour = request.GET.get("hour", None)
    tags = request.GET.get("tags", None)
    sorted_by = request.GET.get("sorted_by", None)
    start_price = 0
    end_price = 15000
    point = Point(23.31326937672202, 42.68336526966131)
    type_of_order = ['listing_id', '-listing_id', '-likes', '-comments']
    if query:
        query = query.split(" ")
        if tags:
            tags = tags.split(',')
            query = query + tags
        sq = SQ()
        for q in query:
            sq.add(SQ(tags__contains=q), SQ.OR)
            sq.add(SQ(title__contains=q), SQ.OR)
            sq.add(SQ(description__contains=q), SQ.OR)
    else:
        sq = SQ()

    if budget:
        start_price = int(budget.split('-')[0])
        end_price = int(budget.split('-')[1])

    if gender:
        gender = int(gender)
        if gender == 0:
            gender = [0]
        elif gender == 2:
            gender = [1]
        else:
            gender = [0,1,2]
    else:
        gender = [0,1,2]


    # if lat and lng:
    #     lat = float(lat)
    #     lng = float(lng)
        # point = Point(lat, lng)
        
    if date and date.isdigit():
        date = int(date)
    else:
        date = None

    if not (hour is  None or hour == "-1"):
        hour = int(hour)
    else:
        hour = -1

    if rating:
        rating = int(rating)
    else:
        rating = 0

    if sorted_by:
        sorted_by = type_of_order[int(sorted_by)]
    else:
        sorted_by = 'listing_id'


    partial_query = SearchQuerySet().models(Listing).filter(sq)
    partial_query = [l.price for l in partial_query]

    if len(partial_query) >= 2:
        price_list = [min(partial_query), max(partial_query)]
    else:
        price_list = [0, 500]
    print(price_list)

    price_list = [min(price_list), max(price_list)]
    _listings = SearchQuerySet().models(Listing).filter(sq).filter(
                                                    gender__in=gender, 
                                                    price__gte=start_price, 
                                                    price__lte=end_price, 
                                                    status=1, 
                                                    rating__gte=rating)
    print("numbers", len(_listings))
    # .dwithin('location', point, D(km=1500000))

    if date and not (hour is not None and hour == -1):
        ''' hour in seconds is the time in utc seconds from the date to the required time '''
        work_days = [("mon_start", "mon_end"), ("tues_start", "tues_end"), ("wed_start", "wed_end"), ("thurs_start", "thurs_end"), ("fri_start", "fri_end"), ("sat_start", "sat_end"), ("sun_start", "sun_end")]
        
        # get listings IDs which was already filtered and make in format (1,1,3,3,5)
        listings_ids = [l.listing_id for l in _listings]
        listings_ids = str(listings_ids)[1:-1]

        # get the index of the day from the week
        week_days = datetime.datetime.fromtimestamp(date).strftime('%w')
        week_days = work_days[int(week_days)]

        # hour in seconds
        hour_in_seconds = 28800 + hour*1800

        # start range is a variable which will be used for the following things: time in seconds from booking start 
        start_range = date + hour_in_seconds

        query = "SELECT DISTINCT listing.id, listing.title, listing.likes, listing.price, listing.artist_id, listing.comments, listing.picture_cover, artist.lat, artist.lng, artist.style, artist.avatar"
        query += " FROM listings_listing AS listing"
        query += " JOIN artists_artist AS artist ON artist.id = listing.artist_id"
        query += " JOIN artists_worktime AS worktime ON worktime.artist_id = artist.id"
        query += " LEFT JOIN booking_booking AS booking ON booking.artist_id = artist.id"
        query += " LEFT JOIN artists_busy AS busy ON busy.artist_id = artist.id"
        query += " WHERE listing.id IN ({0})".format(listings_ids)
        query += " AND worktime.{0} <= {1} AND worktime.{2} >= ({1} + listing.duration/1800)".format(week_days[0], hour, week_days[1])
        query += " AND (booking.start_time >= listing.duration + {0}".format(start_range)
        query += " OR booking.end_time <= {0} OR booking.start_time IS NULL)".format(start_range)
        query += " AND (busy.start_time >= listing.duration + {0}".format(start_range)
        query += " OR busy.end_time <= {0} OR busy.start_time IS NULL)".format(start_range)


        cursor = connection.cursor()
        cursor.execute(query)
        _listings = dictfetchall(cursor)

        listings = []
        listing = {}
        for l in _listings:
            listing = {}
            listing["lat"] = l["lat"]
            listing["lng"] = l["lng"]
            listing["id"] = l["id"]
            listing["picture"] = l["picture_cover"]
            listing["style"] = STYLE_INDEXES[int(l["style"])-1][1]
            listing["title"] = l["title"]
            listing["likes"] = l["likes"]
            listing["price"] = int(l["price"])
            listing["comments"] = l["comments"]
            listing["artist_id"] = l["artist_id"]
            listing["avatar"] = MEDIA_ROOT + l["avatar"][7:]
            listings.append(listing)
        print("1")
    elif date:
        work_days = [("mon_start", "mon_end"), ("tues_start", "tues_end"), ("wed_start", "wed_end"), ("thurs_start", "thurs_end"), ("fri_start", "fri_end"), ("sat_start", "sat_end"), ("sun_start", "sun_end")]
        
        listings_ids = [l.listing_id for l in _listings]
        listings_ids = str(listings_ids)[1:-1]

        week_days = datetime.datetime.fromtimestamp(date).strftime('%w')
        week_days = work_days[int(week_days)]

        query = "SELECT DISTINCT listing.id, listing.title, listing.likes, listing.price, listing.artist_id, listing.comments, listing.picture_cover, artist.lat, artist.lng, artist.style, artist.avatar"
        query += " FROM listings_listing AS listing"
        query += " JOIN artists_artist AS artist ON artist.id = listing.artist_id"
        query += " JOIN artists_worktime AS worktime ON worktime.artist_id = artist.id"
        query += " LEFT JOIN booking_booking AS booking ON booking.artist_id = artist.id"
        query += " LEFT JOIN artists_busy AS busy ON busy.artist_id = artist.id"
        query += " WHERE listing.id IN ({0})".format(listings_ids)
        query += " AND NOT worktime.{0} = -1".format(week_days[0])

        cursor = connection.cursor()
        cursor.execute(query)
        _listings = dictfetchall(cursor)

        listings = []
        listing = {}
        for l in _listings:
            listing = {}
            listing["lat"] = l["lat"]
            listing["lng"] = l["lng"]
            listing["id"] = l["id"]
            listing["picture"] = l["picture_cover"]
            listing["style"] = STYLE_INDEXES[int(l["style"])-1][1]
            listing["title"] = l["title"]
            listing["likes"] = l["likes"]
            listing["price"] = int(l["price"])
            listing["comments"] = l["comments"]
            listing["artist_id"] = l["artist_id"]
            listing["avatar"] = MEDIA_ROOT + l["avatar"][7:]
            listings.append(listing)
        print("2")

    else:
        listings = []
        listing = {}
        for l in _listings:
            listing = {}
            listing["lat"] = l.location.x
            listing["lng"] = l.location.y
            listing["id"] = l.listing_id
            listing["picture"] = l.get_picture
            listing["style"] = l.style
            listing["title"] = l.title
            listing["likes"] = l.likes
            listing["price"] = int(l.price)
            listing["comments"] = l.comments
            listing["artist_id"] = l.artist_id
            listing["avatar"] = l.artist_avatar
            listings.append(listing)
        print('3')
    return render(request, 'service/service.html', {"listings": listings, "price_list": price_list})