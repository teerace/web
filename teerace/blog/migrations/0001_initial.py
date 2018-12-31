import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Entry",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("published_at", models.DateTimeField(auto_now=True)),
                ("enable_comments", models.BooleanField(default=True)),
                (
                    "is_micro",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether this entry should be displayed as micropost. It will not be included in Teeplanet feed.",
                        verbose_name="micro",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("slug", models.CharField(max_length=100, blank=True)),
                (
                    "excerpt",
                    models.TextField(
                        help_text="You may use Markdown syntax", blank=True
                    ),
                ),
                ("excerpt_html", models.TextField(blank=True)),
                ("content", models.TextField(help_text="You may use Markdown syntax")),
                ("content_html", models.TextField()),
                (
                    "status",
                    models.IntegerField(
                        default=2,
                        choices=[(1, "Published"), (2, "Draft"), (3, "Hidden")],
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
            ],
            options={"get_latest_by": "created_at", "verbose_name_plural": "Entries"},
        )
    ]
