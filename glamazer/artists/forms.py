import string
import random
import os
import shutil
import base64
import re

from io import BytesIO
from PIL import Image

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from glamazer.core.helpers import get_object_or_None
from glamazer.artists.models import Artist
from glamazer.listings.models import Listing, Tags, ListingTags
from glamazer.settings import STYLE_INDEXES, MEDIA_URL, MEDIA_ROOT, DURATION



class ArtistForm(ModelForm):
    
    name = forms.CharField(required=True, widget=forms.TextInput())
    email = forms.EmailField(required=True, widget=forms.TextInput())
    password = forms.CharField(widget=(forms.PasswordInput()))
    confirm_password = forms.CharField(widget=(forms.PasswordInput()))

    class Meta:
        model = Artist
        fields = ['confirm_password', ]

    def clean_email(self):

        email = self.cleaned_data['email']
        check_email = User.objects.filter(email=email)

        if check_email:
            raise forms.ValidationError(
                "A user associated with this email address already exists")

        return email

    def clean_password(self):

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if not password == confirm_password:
            raise forms.ValidationError("Password mismatch")

        elif len(password) < 6:
            raise forms.ValidationError("Password is too short (6 symbols)")

        elif password.isalpha() or password.isdigit():
            raise forms.ValidationError("Password should contain at least one alphabetic and one non-alphabetic character")

        return password

    def save(self):

        data = self.cleaned_data
        username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))

        new_user = User.objects.create_user(
            username = username,
            first_name = data['name'],
            email = data['email'],
            password = data['password'],
            related_with = 'artists',
            )

        return new_user


class ArtistDetails(forms.Form):
    
    style = forms.ChoiceField(widget=forms.Select(), choices=STYLE_INDEXES)
    specific_style = forms.CharField()
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'value': 'Click here to upload picture', 'class': 'custom_button' }))
    cropped_image = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.artist = kwargs.pop('artist', None)
        super(ArtistDetails, self).__init__(*args, **kwargs)

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        print(avatar)
        if not self.artist.avatar and not avatar:
            raise forms.ValidationError("This field is required.")

        return avatar

    def handle_uploaded_file(self, my_file, user):
        
        #format the data
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        my_file = dataUrlPattern.match(my_file).group(2)
        artist_id = str(user.artist.id)
        path = '{0}artists/{1}/avatar/{1}.jpeg'.format(MEDIA_URL, artist_id) 
        full_path = '{0}artists/{1}/avatar/{1}.jpeg'.format(MEDIA_ROOT, artist_id)
        # check if the directory existings
        d = os.path.dirname(full_path)
        if not os.path.exists(d):
            os.makedirs(d)

        im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
        im.save(full_path, 'JPEG')

        return path


class LocationArtistDetails(forms.Form):
    
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter street address'}))
    lat = forms.CharField(required=True, widget=forms.HiddenInput())
    lng = forms.CharField(required=False, widget=forms.HiddenInput())
    mobile_number = forms.CharField(required=True, widget=forms.TextInput())


class EditArtist(ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput())
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    description = forms.CharField(widget=forms.Textarea())
    address = forms.CharField(max_length=128, widget=forms.TextInput())
    style = forms.ChoiceField(widget=forms.Select(), choices=STYLE_INDEXES)
    lat = forms.CharField(required=False, widget=forms.HiddenInput())
    lng = forms.CharField(required=False, widget=forms.HiddenInput())
    mobile_number = forms.CharField(required=True)
    cropped_image = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Artist
        exclude = ('money', 'rating', 'avatar', 'user', 'salon', 'step', 'currency')

    def save(self):

        artist = self.instance
        user = artist.user
        data = self.cleaned_data

        user.first_name = data['name']
        user.save()

        my_file = data['cropped_image']

        if my_file:

            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(my_file).group(2)

            hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
            path = MEDIA_URL + 'artists/' + str(user.artist.id) + '/avatar/' + hash_name + '.jpeg'
            full_path = MEDIA_ROOT + 'artists/' + str(user.artist.id) + '/avatar/' + hash_name + '.jpeg'

            artist.avatar = path
            artist.save()

            #if the folder doesn't exist, create one
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)
            else:
                shutil.rmtree(d)
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
            im.save(full_path, 'JPEG')

        else:
            artist.description = data['description']
            artist.address = data['address']
            artist.style = int(data['style'])
            artist.lat = data['lat']
            artist.lng = data['lng']
            artist.mobile_number = data['mobile_number']
            artist.save()
        return artist


class UploadListing(forms.Form):
    
    title = forms.CharField(required=True, widget=forms.TextInput())
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'Enter description here.'}))
    price = forms.CharField(required=True, widget=forms.NumberInput())
    tags = forms.CharField(required=True, widget=forms.TextInput())
    duration = forms.ChoiceField(widget=forms.Select(), choices=DURATION)
    cover = forms.CharField(required=False, widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Listing

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadListing, self).__init__(*args, **kwargs)

    def clean_price(self):
        data = self.cleaned_data
        price = data['price']
        if not (len(price) in range(5) and price.isdigit()):
            raise forms.ValidationError('Please enter a valid price.')

        return price

    def clean_cover(self):
        data = self.cleaned_data
        cover = data['cover']
        pictures = self.request.POST.getlist('files')
        if not pictures:
            raise forms.ValidationError('Please upload a valid images.')

        return cover


    def save(self, artist, FILES):
        data = self.cleaned_data
        artist_id = str(artist.id)
        pictures = FILES.getlist('files')
        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(6))

        for index, picture in enumerate(pictures):

            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(picture).group(2)

            path = MEDIA_URL + 'artists/' + artist_id + '/listings/' + hash_name + '/'
            if index == int(data["cover"]):    
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + hash_name + '/' + str(index) +'.jpeg'
                cover = full_path
            else:
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + hash_name + '/' + str(index) +'.jpeg'

            #if the folder doesn't exist, create one
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
            im.save(full_path, 'JPEG')
        
        listing = Listing.objects.create(
            artist = artist,
            picture = path,
            title = data['title'],
            description = data['description'],
            picture_cover = cover,
            price = data['price'],
            metadata = hash_name,
            duration = int(data['duration']),
        )
        
        tags = data['tags'].split(',')
        tags.append(artist.get_style())
        for tag in tags:
            tag = tag.lower()
            current_tag = get_object_or_None(Tags, tag=tag)
            if not current_tag:
                current_tag = Tags.objects.create(tag=tag)

            ListingTags.objects.create(listing=listing, tags=current_tag)
        listing.save()
        return listing