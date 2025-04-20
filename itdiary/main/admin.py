from django.contrib import admin
from .models import User, Project, Offer, Message, Review

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Offer)
admin.site.register(Message)
admin.site.register(Review)

