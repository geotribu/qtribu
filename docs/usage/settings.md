# Configuration

Les options du plugin sont intégrées dans un onglet des réglages de QGIS, accessibles de deux façons :

- menu `Préférences` -> `Options...`
- menu du plugin : `Internet` -> `QTribu` -> `Réglages`

![Options du plugin QTribu](https://cdn.geotribu.fr/img/projets-geotribu/plugin_qtribu/qtribu_settings.png "Options du plugin QTribu")

## Navigateur

Permet de choisir dans quel navigateur ouvrir les contenus :

- soit dans un navigateur intégré à QGIS (basé sur `QWebView`)
- soit dans le navigateur par défaut du système

## Notification

Activer ou désactiver le message de notification lorsqu'un nouveau contenu a été publié depuis la dernière lecture.

## Variables d’environnement

La plupart des paramètres peuvent être définis via des variables d’environnement. Cela permet de confier la configuration du plugin directement au service informatique. Cette approche offre plusieurs périmètres de portée :

- pour tous les profils QGIS d’un ordinateur (nécessite des droits administrateur)
- pour tous les profils QGIS d’une session utilisateur
- dans un profil QGIS spécifique : voir `Préférences` > `Système` et le panneau `Variables d’environnement` (exemple ici
)
- uniquement pour une session QGIS donnée en les définissant au lancement

Ceci permet également de s'intégrer à des logiques de déploiement de QGIS et des configurations liées au niveau du Système d'Information, comme avec [QGIS Deployment Toolbelt (QDT)](./with_qdt.md) par exemple.

Par exemple, sur un système Linux classique, si vous souhaitez activer les notifications quand il y a un nouveau contenu de publié, qu'elles soient affichées pendant 30 secondes et ouvrir les contenus dans votre navigateur web par défaut, vous pouvez ajouter les lignes suivantes à votre fichier `.bashrc`, `.zshrc` ou `.profile`:

```sh
export QGIS_PLG_QTRIBU_NOTIFY_PUSH_INFO="true"
export QGIS_PLG_QTRIBU_NOTIFY_PUSH_DURATION="30"
export QGIS_PLG_QTRIBU_BROWSER="2"
```

Sous Windows, c’est encore plus simple : une interface graphique permet de définir les variables d’environnement aussi bien au niveau du système (administrateur) que de l’utilisateur. Vous pouvez y accéder via le menu Démarrer.

Le tableau suivant liste les paramètres disponibles, ainsi que la variable d’environnement associée et sa valeur par défaut :

| Paramètre | Variable d'environnement | Valeur par défaut |
| :-------- | :----------------------: | :---------------: |
| Activer le mode debug | `QGIS_PLG_QTRIBU_DEBUG_MODE` | False |
| Dossier local de l'application | `QGIS_PLG_QTRIBU_LOCAL_APP_FOLDER` | PosixPath('/home/jmo/.geotribu/cache') |
| URL du flux JSON | `QGIS_PLG_QTRIBU_JSON_FEED_SOURCE` | '<https://geotribu.fr/feed_json_created.json>' |
| URL du flux RSS | `QGIS_PLG_QTRIBU_RSS_SOURCE` | '<https://geotribu.fr/feed_rss_created.xml>' |
| Fréquence de consultation du RSS | `QGIS_PLG_QTRIBU_RSS_POLL_FREQUENCY_HOURS` | 24 |
| Navigateur web à utiliser (1 : intégré à QGIS ; 2 : navigateur par défaut du système) | `QGIS_PLG_QTRIBU_BROWSER` | 1 |
| Activer les notifications | `QGIS_PLG_QTRIBU_NOTIFY_PUSH_INFO` | True |
| Durée de la notification | `QGIS_PLG_QTRIBU_NOTIFY_PUSH_DURATION` | 10 |
| Afficher le splash screen de Geotribu | `QGIS_PLG_QTRIBU_SPLASH_SCREEN_ENABLED` | False |
| Acceptation de la licence globale | `QGIS_PLG_QTRIBU_LICENSE_GLOBAL_ACCEPT` | False |
| Licence préférée pour mes articles | `QGIS_PLG_QTRIBU_LICENSE_ARTICLE_PREFERRED` | '' |
| Acceptation de la charte éditoriale | `QGIS_PLG_QTRIBU_EDITORIAL_POLICY_ACCEPT` | False |
| Intégration au fil d'actualité de QGIS | `QGIS_PLG_QTRIBU_INTEGRATION_QGIS_NEWS_FEED` | True |
| Prénom | `QGIS_PLG_QTRIBU_AUTHOR_FIRSTNAME` | '' |
| Nom de famille | `QGIS_PLG_QTRIBU_AUTHOR_LASTNAME` | '' |
| Email | `QGIS_PLG_QTRIBU_AUTHOR_EMAIL` | '' |
| Nom d'utilisateur GitHub | `QGIS_PLG_QTRIBU_AUTHOR_GITHUB` | '' |
| Identifiant LinkedIn | `QGIS_PLG_QTRIBU_AUTHOR_LINKEDIN` | '' |
| Nom d'utilisateur Bluesky | `QGIS_PLG_QTRIBU_AUTHOR_BLUESKY` | '' |
| Nom d'utilisateur Mastodon | `QGIS_PLG_QTRIBU_AUTHOR_MASTODON` | '' |
