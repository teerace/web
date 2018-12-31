import django.db.models.deletion
import django_countries.fields
import picklefield.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("race", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("api_token", models.CharField(unique=True, max_length=24)),
                ("registration_ip", models.IPAddressField(null=True, blank=True)),
                ("last_connection_at", models.DateTimeField(auto_now_add=True)),
                (
                    "country",
                    django_countries.fields.CountryField(blank=True, max_length=2),
                ),
                ("points", models.IntegerField(default=0)),
                (
                    "points_history",
                    picklefield.fields.PickledObjectField(null=True, editable=False),
                ),
                ("yesterday_points", models.IntegerField(default=0)),
                ("playtime", models.IntegerField(default=0)),
                (
                    "gender",
                    models.IntegerField(
                        default=1, choices=[(1, "Unknown"), (2, "Male"), (3, "Female")]
                    ),
                ),
                ("has_skin", models.BooleanField(default=False)),
                ("skin_name", models.CharField(max_length=40, blank=True)),
                ("skin_body_color", models.CharField(max_length=7, blank=True)),
                ("skin_feet_color", models.CharField(max_length=7, blank=True)),
                ("skin_body_color_raw", models.IntegerField(null=True, blank=True)),
                ("skin_feet_color_raw", models.IntegerField(null=True, blank=True)),
                (
                    "last_played_server",
                    models.ForeignKey(
                        related_name="players",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="race.Server",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["id"], "get_latest_by": "user__created_at"},
        )
    ]
