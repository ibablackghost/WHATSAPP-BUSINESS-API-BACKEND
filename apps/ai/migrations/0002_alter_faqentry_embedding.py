from django.db import migrations, models


def embedding_to_json(apps, schema_editor):
    """Postgres: vector -> jsonb. SQLite/autres: ALTER standard."""
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("ALTER TABLE ai_faqentry DROP COLUMN embedding")
        schema_editor.execute("ALTER TABLE ai_faqentry ADD COLUMN embedding jsonb NULL")
        return
    FAQEntry = apps.get_model("ai", "FAQEntry")
    old_field = FAQEntry._meta.get_field("embedding")
    new_field = models.JSONField(blank=True, null=True)
    schema_editor.alter_field(FAQEntry, old_field, new_field)


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(embedding_to_json, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="faqentry",
                    name="embedding",
                    field=models.JSONField(blank=True, null=True),
                ),
            ],
        ),
    ]
