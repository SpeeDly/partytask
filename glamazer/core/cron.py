import string
import random

from django_cron import CronJobBase, Schedule

from glamazer.core.helpers import current_time, full_capture
from glamazer.core.emails import send_email
from glamazer.booking.models import Booking
from glamazer.reviews.models import WaitingForFeedback


class SendFeedbackForm(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours
    ALLOW_PARALLEL_RUNS = True
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'glamazer.core.cron.send_review_email'    # a unique code

    def do(self):
        now = current_time()
        passed_bookings = Booking.objects.select_related().filter(end_time__lt=now, is_mailed=False, status=1)

        for b in passed_bookings:

            token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))

            WaitingForFeedback.objects.create(
                client=b.client,
                artist=b.artist,
                listing=b.listing,
                booking=b,
                token=token
                )

            full_capture(b.id)

            kwargs = {}
            kwargs['artistname'] = b.artist.user.first_name
            kwargs['token'] = token
            send_email(case=17, receiver=b.client.user, **kwargs)

        Booking.objects.select_related().filter(end_time__lt=now, is_mailed=False, status=1).update(is_mailed=True)


def send_review_email():
    print("something cool")
    now = current_time()
    # passed_bookings = Booking.objects.select_related("client__user, artist__user").filter(end_time__lt=now, is_mailed=False, status=1).update(is_mailed=True)
    passed_bookings = Booking.objects.all()
    print(passed_bookings)
    for b in passed_bookings:

        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))
        
        # b.is_mailed = True
        # b.save()
        w = WaitingForFeedback.objects.all()
        for x in w:
            x.delete()

        WaitingForFeedback.objects.create(
            client=b.client,
            artist=b.artist,
            listing=b.listing,
            booking=b,
            token=token
            )

        kwargs = {}
        kwargs['artistname'] = b.artist.user.first_name
        kwargs['token'] = token
        send_email(case=17, receiver=b.client.user, **kwargs)