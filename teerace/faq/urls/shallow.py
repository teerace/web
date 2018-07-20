from django.conf.urls import url

from ..views.shallow import question_detail, topic_detail, topic_list


# Include these patterns if you want URLs like:
#
#   /faq/
#   /faq/#topic
#   /faq/#question
#

urlpatterns = (
    url(r"^$", topic_list, name="faq-topic-list"),
    url(r"^(?P<slug>[-\w]+)/$", topic_detail, name="faq-topic-detail"),
    url(
        r"^(?P<topic_slug>[-\w]+)/(?P<slug>[-\w]+)/$",
        question_detail,
        name="faq-question-detail",
    ),
)
