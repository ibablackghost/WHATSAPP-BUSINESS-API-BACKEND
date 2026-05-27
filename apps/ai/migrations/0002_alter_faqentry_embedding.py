from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="faqentry",
            name="embedding",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
