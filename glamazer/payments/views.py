import paypalrestsdk

from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render

from glamazer.booking.models import Booking, DummyBooking
from glamazer.core.helpers import get_object_or_None, create_payment
from glamazer.settings import PAYPAL_MODE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET


def start_payment(request):
    sn = request.session.get('dummy_booking_id', None)
    dummy_booking = get_object_or_None(DummyBooking, id=int(sn))
    
    paypalrestsdk.configure({
      'mode': PAYPAL_MODE,
      'client_id': PAYPAL_CLIENT_ID,
      'client_secret': PAYPAL_CLIENT_SECRET
    })
    payment = paypalrestsdk.Payment({
            "intent": "authorize",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://partytask.com/success",
                "cancel_url": "http://partytask.com/error"
            },
            "transactions": [ {
                "item_list": {
                    "items": [{
                        "name": dummy_booking.title,
                        "price": int(dummy_booking.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": int(dummy_booking.price),
                    "currency": "USD" 
                },
                "description": dummy_booking.title
            }]
        })

    if not payment.create():
        print(payment.error)
        raise Http404

    request.session['Payment_id'] = payment['id']
    redirect = payment['links'][1]['href'] + "&no_shipping=1"

    return HttpResponseRedirect(redirect)


def success_payment(request):

    paypalrestsdk.configure({
      'mode': PAYPAL_MODE,
      'client_id': PAYPAL_CLIENT_ID,
      'client_secret': PAYPAL_CLIENT_SECRET
    })
    payer_id = request.GET.get('PayerID', None)
    payment_id = request.session['Payment_id']
    
    payment = paypalrestsdk.Payment.find(payment_id)
    payment.execute({"payer_id": payer_id})

    sn = request.session.get('dummy_booking_id', None)
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
        booking = Booking.objects.create(
                                artist = dummy_booking.artist,
                                listing = dummy_booking.listing,
                                client = dummy_booking.client,
                                cancellation_policy = dummy_booking.cancellation_policy,
                                price = dummy_booking.price,
                                title = dummy_booking.title,
                                start_time = dummy_booking.start_time,
                                end_time = dummy_booking.end_time,
                                status = 0,
                            )
        create_payment(request, payment, booking.id)
        dummy_booking.delete()
        request.session['dummy_booking_id'] = ''
        request.session['Payment_id'] = ''
    else:
        return HttpResponseRedirect(reverse("error"))

    
    return render(request, 'payments/success.html', {})

def error_payment(request):
    ''' Delete everything what we can find about this booking '''
    sn = request.session.get('dummy_booking_id', None)
    listing_id = 0
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
        listing_id = dummy_booking.listing_id
        dummy_booking.delete()
    request.session['dummy_booking_id'] = ''
    request.session['Payment_id'] = ''
    
    return HttpResponseRedirect("/listings/{0}".format(listing_id))


def cancel_payment(request):
    ''' Delete everything what we can find about this booking '''
    sn = request.session.get('dummy_booking_id', None)
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
        listing_id = dummy_booking.listing_id
        dummy_booking.delete()
    request.session['dummy_booking_id'] = ''
    request.session['Payment_id'] = ''

    return HttpResponseRedirect("/listings/{0}".format(listing_id))