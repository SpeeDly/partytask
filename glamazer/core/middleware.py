from django.conf import settings 

class MobileMiddleware(object):
    def process_request(self, request):
        subdomain = request.META.get('HTTP_X_FORWARDED_HOST', '').split('.')
        if 'm' in subdomain or settings.MOBILE_ONLY:
            settings.TEMPLATE_DIRS = settings.MOBILE_TEMPLATE_DIRS
        else:
            settings.TEMPLATE_DIRS = settings.DESKTOP_TEMPLATE_DIRS