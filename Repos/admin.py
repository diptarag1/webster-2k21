from django.contrib import admin

from Repos.models import PullRequest, Repo,Issue,IssueComment

# Register your models here.
admin.site.register(Repo)
admin.site.register(Issue)
admin.site.register(IssueComment)
admin.site.register(PullRequest)