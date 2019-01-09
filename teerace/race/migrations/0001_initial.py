import django.db.models.deletion
import picklefield.fields
from django.conf import settings
from django.db import migrations, models

import lib.file_storage
import race.models
import race.validators


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="BestRun",
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
                ("time", models.DecimalField(max_digits=12, decimal_places=3)),
                ("points", models.IntegerField(default=0)),
                (
                    "demo_file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=race.models.demo_filename,
                        validators=[race.validators.is_demo_file],
                    ),
                ),
                (
                    "ghost_file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=race.models.ghost_filename,
                        validators=[race.validators.is_ghost_file],
                    ),
                ),
            ],
            options={"ordering": ["time", "run__created_at"]},
        ),
        migrations.CreateModel(
            name="Map",
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
                ("name", models.CharField(unique=True, max_length=50)),
                ("author", models.CharField(max_length=100, blank=True)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                (
                    "map_file",
                    models.FileField(
                        upload_to=race.models.map_filename,
                        validators=[race.validators.is_map_file],
                    ),
                ),
                ("crc", models.CharField(max_length=8, null=True, blank=True)),
                ("has_unhookables", models.NullBooleanField(default=False)),
                ("has_deathtiles", models.NullBooleanField(default=False)),
                ("has_teleporters", models.NullBooleanField(default=False)),
                ("has_speedups", models.NullBooleanField(default=False)),
                ("shield_count", models.IntegerField(default=0, null=True)),
                ("heart_count", models.IntegerField(default=0, null=True)),
                ("grenade_count", models.IntegerField(default=0, null=True)),
                ("has_image", models.BooleanField(default=False)),
                ("download_count", models.IntegerField(default=0)),
                (
                    "added_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MapType",
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
                ("slug", models.SlugField(max_length=20)),
                ("displayed_name", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Run",
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
                ("nickname", models.CharField(max_length=15)),
                ("clan", models.CharField(max_length=11, null=True, blank=True)),
                ("checkpoints", models.CharField(max_length=349, blank=True)),
                ("time", models.DecimalField(max_digits=12, decimal_places=3)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("map", models.ForeignKey(to="race.Map", on_delete=models.CASCADE)),
            ],
            options={"ordering": ["time", "created_at"], "get_latest_by": "created_at"},
        ),
        migrations.CreateModel(
            name="Server",
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
                ("name", models.CharField(max_length=100, verbose_name=b"server name")),
                (
                    "description",
                    models.TextField(
                        help_text=b"You may use Markdown syntax", blank=True
                    ),
                ),
                ("description_html", models.TextField(null=True, blank=True)),
                ("address", models.CharField(max_length=50, blank=True)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text=b"Designates whether this server should be treated as active. Unselect this instead of deleting servers.",
                        verbose_name=b"active",
                    ),
                ),
                ("last_connection_at", models.DateTimeField(auto_now=True)),
                (
                    "anonymous_players",
                    picklefield.fields.PickledObjectField(editable=False),
                ),
                ("api_key", models.CharField(unique=True, max_length=32)),
                (
                    "maintained_by",
                    models.ForeignKey(
                        related_name="maintained_servers",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name=b"maintainer",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "played_map",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="race.Map",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="run",
            name="server",
            field=models.ForeignKey(
                related_name="runs",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="race.Server",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="run",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="map",
            name="map_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_DEFAULT,
                default=1,
                to="race.MapType",
            ),
        ),
        migrations.AddField(
            model_name="bestrun",
            name="map",
            field=models.ForeignKey(to="race.Map", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="bestrun",
            name="run",
            field=models.ForeignKey(to="race.Run", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="bestrun",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
        ),
        migrations.AlterUniqueTogether(
            name="bestrun", unique_together=set([("user", "map")])
        ),
    ]
