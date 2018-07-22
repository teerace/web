from actstream import action
from annoying.functions import get_object_or_None
from django.contrib.auth import authenticate, get_user_model
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from pinax.badges.models import BadgeAward
from pinax.badges.registry import badges
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from lib.rgb import rgblong_to_hex
from race import tasks
from race.models import BestRun, Map, Run, Server

from . import serializers
from .helpers import get_filtered_checkpoints


User = get_user_model()


class ActivityCreateView(APIView):
    def post(self, request, format=None):
        event_type = request.data.get("event_type")
        verb_dict = {"join": "joined", "leave": "left"}
        if event_type not in ["join", "leave"]:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=int(request.data["user_id"]))
        except (User.DoesNotExist, KeyError):
            return Response(
                "User with specified user_id doesn't exist",
                status=status.HTTP_400_BAD_REQUEST,
            )

        action.send(user, verb=verb_dict[event_type], target=request.auth)
        return Response()


class RecordingUploadView(APIView):
    recording_field_name = None

    def post(self, request, user_id, map_id, format=None):
        try:

            best_run = BestRun.objects.get(map_id=map_id, user_id=user_id)
        except BestRun.DoesNotExist:
            return Response(
                "There's no BestRun matching this user/map pair.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        setattr(
            best_run,
            self.recording_field_name,
            request.data.get(self.recording_field_name),
        )
        best_run.save()

        return Response()


def recording_upload_view_factory(class_name, field_name):
    return type(
        class_name, (RecordingUploadView,), {"recording_field_name": field_name}
    )


DemoUploadView = recording_upload_view_factory("DemoUploadView", "demo_file")
GhostUploadView = recording_upload_view_factory("GhostUploadView", "ghost_file")


class PingView(APIView):
    def post(self, request, format=None):
        server = request.auth
        users_dict = request.data.get("users", {})

        badges_list = []

        if users_dict:
            user_ids = list(users_dict.keys())

            # get a list of newly awarded badges
            badges_awarded = BadgeAward.objects.filter(
                user__id__in=user_ids,
                awarded_at__gt=F("user__profile__last_connection_at"),
            )

            badges_list = [
                {
                    "name": badges._registry[badge.slug].levels[badge.level].name,
                    "user_id": badge.user.id,
                }
                for badge in badges_awarded
            ]

            # removing the relationship for users not present on the server
            server.players.exclude(id__in=user_ids).update(last_played_server=None)
            # updating users' last connection time
            UserProfile.objects.filter(id__in=user_ids).update(
                last_played_server=request.auth, last_connection_at=timezone.now()
            )
            # TODO save nicknames of logged users
        server.anonymous_players = request.data.get("anonymous", ())
        server.played_map = get_object_or_None(Map, name=request.data.get("map"))
        server.save()

        return Response({"awards": badges_list})


class UserDetailView(RetrieveAPIView):
    lookup_url_kwarg = "user_id"
    queryset = get_user_model().objects.select_related("profile")
    serializer_class = serializers.UserSerializer


class UserProfileDetailView(RetrieveAPIView):
    lookup_url_kwarg = "user_id"
    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer


class UserRankView(APIView):
    def get(self, request, user_id, format=None):
        profile = get_object_or_404(UserProfile, pk=user_id)
        return Response(profile.position)


class UserMapRankView(APIView):
    def get(self, request, user_id, map_id, format=None):
        profile = get_object_or_404(UserProfile, pk=user_id)
        return Response(
            {
                "position": profile.map_position(int(map_id)),
                "bestrun": profile.best_score(int(map_id)),
            }
        )


class UserAuthTokenView(APIView):
    def post(self, request, format=None):
        try:
            user = User.objects.exclude(is_active=False).get(
                profile__api_token=request.data.get("api_token")
            )
        except User.DoesNotExist:
            return Response(False)
        return Response(serializers.UserSerializer(user).data)


class UserGetByNameView(APIView):
    def post(self, request, format=None):
        form_username = request.data.get("username")
        try:
            user = User.objects.get(username=form_username)
        except User.DoesNotExist:
            users = User.objects.filter(username__icontains=form_username)
            if users.count():
                return Response({"id": users[0].id, "username": users[0].username})
            else:
                return Response(None)
        return Response({"id": user.id, "username": user.username})


class UserSkinView(APIView):
    def put(self, request, user_id, format=None):
        profile = get_object_or_404(UserProfile, pk=user_id)
        profile.has_skin = True
        try:
            profile.skin_name = request.data["skin_name"]
            body_color = request.data.get("body_color")
            feet_color = request.data.get("feet_color")
            if body_color and feet_color:
                profile.skin_body_color_raw = body_color
                profile.skin_body_color = rgblong_to_hex(body_color)
                profile.skin_feet_color_raw = feet_color
                profile.skin_feet_color = rgblong_to_hex(feet_color)
            else:
                profile.skin_body_color_raw = None
                profile.skin_body_color = ""
                profile.skin_feet_color_raw = None
                profile.skin_feet_color = ""
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        profile.save()
        return Response(serializers.UserProfileSerializer(profile).data)


class UserPlaytimeView(APIView):
    def put(self, request, user_id, format=None):
        profile = get_object_or_404(UserProfile, pk=user_id)
        profile.update_playtime(int(request.data.get("seconds")))
        return Response()


class RunDetailView(RetrieveAPIView):
    lookup_url_kwarg = "run_id"
    queryset = Run.objects.all()
    serializer_class = serializers.RunSerializer


class RunCreateView(APIView):
    def post(self, request, format=None):
        filtered_checkpoints = get_filtered_checkpoints(request.data["checkpoints"])
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, pk=user_id) if user_id else None
        run = Run(
            map_id=int(request.data["map_id"]),
            server=request.auth,
            user_id=user_id,
            nickname=request.data["nickname"],
            clan=request.data["clan"],
            time=request.data["time"],
            checkpoints=filtered_checkpoints,
        )
        run.save()
        tasks.redo_ranks.apply(args=[run.id])
        if user is not None:
            user.profile.update_connection(request.auth)
            badges.possibly_award_badge("run_finished", user=user, run=run)
        return Response(serializers.RunSerializer(run).data)


class MapDetailView(RetrieveAPIView):
    lookup_url_kwarg = "map_id"
    queryset = Map.objects.all()
    serializer_class = serializers.MapSerializer


class MapListView(ListAPIView):
    queryset = Map.objects.all()
    serializer_class = serializers.MapSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        types = self.kwargs.get("type")
        if types:
            types = types.split(" ")
            q = Q()
            for type_ in types:
                q &= Q(map_types__slug=type_)
            queryset = queryset.filter(q)
        return queryset


class MapRankView(ListAPIView):
    queryset = BestRun.objects.all()
    serializer_class = serializers.BestRunSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(map_id=int(self.kwargs["map_id"]))

        offset = int(self.kwargs.get("offset", 1)) - 1
        return queryset.select_related()[offset : offset + 5]


class HelloView(APIView):
    def get(self, request, format=None):
        return Response("PONG")


class ServerListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        servers = (
            Server.objects.exclude(is_active=False)
            .exclude(address="")
            .values_list("address", flat=True)
        )
        return Response(servers)


class UserTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        user = authenticate(
            username=request.data.get("username"), password=request.data.get("password")
        )
        if not user or not user.is_active:
            return False
        return user.profile.api_token
