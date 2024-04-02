from qgis.core import QgsSettings

qsettings = QgsSettings()

print(f"QGIS3.ini located at: {qsettings.fileName()}")
print(f"qgis_global_settings.ini located at: {qsettings.globalSettingsPath()}")

qsettings.beginGroup(
    prefix="news-feed/items/httpsfeedqgisorg/entries/items/", section=QgsSettings.App
)
all_news_keys = qsettings.allKeys()

print(all_news_keys)

latest_qgis_news_feed_id = max(
    [
        key.split("/")[0]
        for key in all_news_keys
        if "title" in key and not qsettings.value(key=key).startswith("[Geotribu]")
    ]
)
print(latest_qgis_news_feed_id, type(latest_qgis_news_feed_id))
