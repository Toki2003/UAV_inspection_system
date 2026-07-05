from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0002_alert"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="rtsp_url",
            field=models.CharField(
                max_length=500,
                blank=True,
                verbose_name="RTSP流地址",
                help_text=(
                    "例如："
                    "rtsp://192.168.1.101:554/stream1"
                ),
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="stream_enabled",
            field=models.BooleanField(
                default=False,
                verbose_name="视频流启用",
            ),
        ),
    ]