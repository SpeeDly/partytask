import time
import requests
import paypalrestsdk

from django import template
from django.db import connection
from django.conf import settings
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger

from glamazer.settings import PAYPAL_MODE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET


def login_user(request, user):
    """
    Log in a user without requiring credentials (using ``login`` from
    ``django.contrib.auth``, first finding a matching backend).

    """
    from django.contrib.auth import load_backend, login
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login(request, user)


def get_object_or_None(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def get_geolocation_from_address(address):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false'.format(address)
    request = requests.get(url)
    json_results = request.json()

    return {'lon': json_results['results'][0]['geometry']['location']['lng'],
                    'lat': json_results['results'][0]['geometry']['location']['lat']}


def paginator(request, item, limit=10):
    page_it = Paginator(item, limit)
    page = request.GET.get('page')
    try:
        data = page_it.page(page)
    except PageNotAnInteger:
        data = page_it.page(1)
    except EmptyPage:
        data = page_it.page(page_it.num_pages)
    return data

def current_time():
    return round(time.time())


def create_payment(request, payment, booking_id):
    from glamazer.payments.models import Payment
    data = payment['transactions'][0]['related_resources'][0]['authorization']
    state = data['state']
    create_time = data['create_time']
    valid_until = data['valid_until']
    price = data["amount"]["total"]
    currency = data["amount"]["currency"]
    payer_id = payment["payer"]["payer_info"]["payer_id"]
    payment_id = payment["id"]
    authorization_id = data["id"]

    new_payment = Payment.objects.create(
        booking_id = booking_id,
        state = state,
        create_time = create_time, 
        valid_until = valid_until, 
        price = price, 
        currency = currency, 
        payer_id = payer_id, 
        payment_id = payment_id, 
        authorization_id = authorization_id,
        )

    return new_payment

def void_authorization(booking_id):
    from glamazer.payments.models import Payment
    payment = Payment.objects.filter(booking_id=booking_id).order_by("last_updated")[0]
    auth_id = payment.authorization_id
    
    paypalrestsdk.configure({
        'mode': PAYPAL_MODE,
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_CLIENT_SECRET
    })
    
    authorization = paypalrestsdk.Authorization.find(auth_id)
    
    if authorization.void():
        payment.current_status = "voided"
        payment.save()
        return True
    else:
        payment.current_status = "failed"
        payment.save()
        return False


def full_capture(booking_id):
    ''' Full capture the money. Example for listing 100$. 90 for artist, 10 for us. '''
    from glamazer.payments.models import Payment, Fee
    from glamazer.booking.models import Booking

    booking = Booking.objects.select_related().get(id=booking_id)
    current_fee = Fee.objects.get(deactivated__isnull=True)
    artist = booking.artist
    
    ''' Check if for the user have some special fee '''
    if artist.custom_fee:
        current_fee = artist.custom_fee
    else:
        current_fee = current_fee.fee

    price = booking.price # booking price
    for_us = price*current_fee/100 # our money

    payment = Payment.objects.filter(booking_id=booking_id).order_by("last_updated")[0]
    auth_id = payment.authorization_id

    paypalrestsdk.configure({
        'mode': PAYPAL_MODE,
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_CLIENT_SECRET
    })


    authorization = paypalrestsdk.Authorization.find(auth_id)
    capture = authorization.capture({
        "amount": {
            "currency": "USD",
            "total": format(price, ',.2f') },
        "is_final_capture": True })

    for_artist = round(price - for_us, 2)

    print(capture)

    if capture.success():
        print("Capture[%s] successfully"%(capture.id))
    else:
        print(capture.error)
        return False


    artist.money = artist.money + for_artist
    artist.save()

    booking.revenue = for_artist
    booking.save()


def partially_capture(booking_id):
    ''' Partially capture the money. Example for listing 100$. 50 for the client, 45 for artist, 5 for us. '''
    from glamazer.payments.models import Payment, Fee
    from glamazer.booking.models import Booking

    booking = Booking.objects.select_related().get(id=booking_id)
    current_fee = Fee.objects.get(deactivated__isnull=True)
    artist = booking.artist
    
    if artist.custom_fee:
        current_fee = artist.custom_fee
    else:
        current_fee = current_fee.fee

    price = booking.price # booking price
    percent = booking.cancellation_policy.percent # the percent from cancellation policy
    for_artist = price*percent/100
    # for_user = price - for_artist
    for_us = for_artist*current_fee/100

    payment = Payment.objects.filter(booking_id=booking_id).order_by("last_updated")[0]
    auth_id = payment.authorization_id

    paypalrestsdk.configure({
        'mode': PAYPAL_MODE,
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_CLIENT_SECRET
    })
    

    print(format(for_artist, ',.2f'))

    authorization = paypalrestsdk.Authorization.find(auth_id)
    capture = authorization.capture({
        "amount": {
            "currency": "USD",
            "total": format(for_artist, ',.2f') },
        "is_final_capture": True })

    for_artist = round(for_artist - for_us, 2)


    if capture.success():
        print("Capture[%s] successfully"%(capture.id))
    else:
        print(capture.error)


    artist.money = artist.money + for_artist
    artist.save()

    booking.revenue = for_artist
    booking.save()


# Iban validator
def IBAN_checker(IBAN):
    ''' Check IBAN country notation, IBAN length and IBAN format '''
    letter_dic = {"A":10, "B":11, "C":12, "D":13, "E":14, "F":15, "G":16, "H":17, "I":18, "J":19, "K":20, "L":21, "M":22,
    "N":23, "O":24, "P":25, "Q":26, "R":27, "S":28, "T":29, "U":30, "V":31, "W":32, "X":33, "Y":34, "Z":35}

    country_dic = {
        "AL":[28,"Albania"],
        "AD":[24,"Andorra"],
        "AT":[20,"Austria"],
        "BE":[16,"Belgium"],
        "BA":[20,"Bosnia"],
        "BG":[22,"Bulgaria"],
        "HR":[21,"Croatia"],
        "CY":[28,"Cyprus"],
        "CZ":[24,"Czech Republic"],
        "DK":[18,"Denmark"],
        "EE":[20,"Estonia"],
        "FO":[18,"Faroe Islands"],
        "FI":[18,"Finland"],
        "FR":[27,"France"],
        "DE":[22,"Germany"],
        "GI":[23,"Gibraltar"],
        "GR":[27,"Greece"],
        "GL":[18,"Greenland"],
        "HU":[28,"Hungary"],
        "IS":[26,"Iceland"],
        "IE":[22,"Ireland"],
        "IL":[23,"Israel"],
        "IT":[27,"Italy"],
        "LV":[21,"Latvia"],
        "LI":[21,"Liechtenstein"],
        "LT":[20,"Lithuania"],
        "LU":[20,"Luxembourg"],
        "MK":[19,"Macedonia"],
        "MT":[31,"Malta"],
        "MU":[30,"Mauritius"],
        "MC":[27,"Monaco"],
        "ME":[22,"Montenegro"],
        "NL":[18,"Netherlands"],
        "NO":[15,"Northern Ireland"],
        "PO":[28,"Poland"],
        "PT":[25,"Portugal"],
        "RO":[24,"Romania"],
        "SM":[27,"San Marino"],
        "SA":[24,"Saudi Arabia"],
        "RS":[22,"Serbia"],
        "SK":[24,"Slovakia"],
        "SI":[19,"Slovenia"],
        "ES":[24,"Spain"],
        "SE":[24,"Sweden"],
        "CH":[21,"Switzerland"],
        "TR":[26,"Turkey"],
        "TN":[24,"Tunisia"],
        "GB":[22,"United Kingdom"]
        }

    def check(n):
        if int(n)%97 !=1:
            result=0 # False
        else:
            result=1 # True
        return result

    while True:
        length = len(IBAN)
        country = IBAN[:2]
        if country in country_dic:
            data = country_dic[country]
            length_c = data[0]
            if length == length_c:
                header = IBAN[:4] # Get the first four characters
                body = IBAN[4:] # And the remaining characters
                IBAN = body+header # Move the first block at the end
                IBAN_ = list(IBAN) # Transform string into a list
                string_=""
                for index in range(len(IBAN_)): # Convert letters to integers
                    if IBAN_[index] in letter_dic:
                        value = letter_dic[IBAN_[index]]
                        IBAN_[index] = value
                for index in range(len(IBAN_)): # Transform list into a string
                    string_ = string_ + str(IBAN_[index])

                if int(string_)%97 !=1:
                    valid=False
                else:
                    valid=True

                if not valid:
                    raise Exception("Not a valid IBAN account No.")
                else:
                    return True
            else:
                raise Exception("Wrong IBAN code length!")
        else:
            raise Exception("Wrong IBAN country code!")


def get_rate(reviews):
    ''' Get the rating for specific unit based on the reviews '''
    rate = 0
    count = len(reviews)
    if not count == 0:
        for review in reviews:
            rate += review.rating
        rate = rate/count
        rate = str(rate)
        front_rate = int(rate.split(".")[0])
        try:
            back_rate = int(rate.split(".")[1])
        except:
            back_rate = 0
    
        if back_rate > 75:
            front_rate += 1
            return front_rate

        elif back_rate < 75 and back_rate > 50:
            back_rate = 5
            return float(str(front_rate) + '.' + str(back_rate))

        elif back_rate < 50 and back_rate > 0:
            back_rate = 5
            return float(str(front_rate) + '.' + str(back_rate))

        elif back_rate == 0:
            return front_rate

    else:
        return 0


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]