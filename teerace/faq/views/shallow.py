from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from ..models import Question, Topic


def _fragmentify(model, slug, url=None):
    get_object_or_404(model.objects.published().filter(slug=slug))
    url = url or reverse("faq-topic-list")
    fragment = "#%s" % slug

    return redirect(url + fragment, permanent=True)


def topic_list(request):
    """
    A list view of all published Topics

    Templates:
        :template:`faq/topic_list.html`
    Context:
        topic_list
            A list of all published :model:`faq.Topic` objects that
            relate to the current :model:`sites.Site`.

    """
    list_view = ListView.as_view(
        queryset=Topic.objects.published(), context_object_name="topic_list"
    )
    return list_view(request)


def topic_detail(request, slug):
    """
    A detail view of a Topic

    Simply redirects to :view:`faq.views.topic_list` with the addition of
    a fragment identifier that links to the given :model:`faq.Topic`.
    E.g., ``/faq/#topic-slug``.

    """
    return _fragmentify(Topic, slug)


def question_detail(request, topic_slug, slug):
    """
    A detail view of a Question.

    Simply redirects to :view:`faq.views.topic_list` with the addition of
    a fragment identifier that links to the given :model:`faq.Question`.
    E.g. ``/faq/#question-slug``.

    """
    return _fragmentify(Question, slug)
