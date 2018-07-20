import picklefield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chart",
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
                ("displayed_name", models.CharField(max_length=30)),
                ("description", models.TextField()),
                ("slug", models.SlugField(unique=True, max_length=30)),
                (
                    "data",
                    picklefield.fields.PickledObjectField(null=True, editable=False),
                ),
            ],
        )
    ]
