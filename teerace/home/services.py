from actstream.models import Action


def get_noun_info(action, label, use_url=True, fallback_url=None):
    data = dict.fromkeys(f"{label}_{key}" for key in ("id", "repr", "url"))
    noun = getattr(action, label)
    if noun is None:
        return data
    data.update({f"{label}_id": noun.id, f"{label}_repr": str(noun)})
    if use_url:
        url = noun.get_absolute_url()
        if not url:
            url = fallback_url
        data[f"{label}_url"] = url
    return data


def actions_to_json(actions):
    return [
        {
            **get_noun_info(action, "actor", fallback_url=action.actor_url),
            **get_noun_info(action, "target"),
            **get_noun_info(action, "action_object", use_url=False),
            "verb": action.verb,
            "timesince": action.timesince(),
            "timestamp": action.timestamp,
        }
        for action in actions
    ]


def get_new_actions(since):
    return Action.objects.filter(timestamp__gt=since).order_by("-timestamp")[:10]
