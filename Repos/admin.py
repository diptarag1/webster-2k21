from django.contrib import admin

from Repos.models import Repo,Issue,IssueComment

# Register your models here.
admin.site.register(Repo)
admin.site.register(Issue)
admin.site.register(IssueComment)