# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## [{version_tag}](https://github.com/geotribu/qtribu/releases/tag/{version_tag}) - YYYY-DD-mm

-->

## 1.1.0 - 2024-11-19

### Features and enhancements 🎉

* feature(qchat): auto-reconnect to last room when QGIS starts by @gounux in https://github.com/geotribu/qtribu/pull/209
* feature(qchat): handle users registration by @gounux in https://github.com/geotribu/qtribu/pull/200
* feature(qchat): like message by @gounux in https://github.com/geotribu/qtribu/pull/210
* feature(qchat): re-arrange websocket message to allow image communications by @gounux in https://github.com/geotribu/qtribu/pull/211
* refactor(qchat): use custom tree widget items by @gounux in https://github.com/geotribu/qtribu/pull/212
* feature(qchat): send a geojson layer through websocket by @gounux in https://github.com/geotribu/qtribu/pull/213
* refactor(qchat): use self.settings instead of PlgOptionsManager by @gounux in https://github.com/geotribu/qtribu/pull/217
* ui(qchat): vertically optimize the QChat widget by @gounux in https://github.com/geotribu/qtribu/pull/216
* feature(qchat): send and receive a crs message by @gounux in https://github.com/geotribu/qtribu/pull/219
* feature(qchat): send and receive a bbox message by @gounux in https://github.com/geotribu/qtribu/pull/220
* trad(qchat): add QChat fr translations by @gounux in https://github.com/geotribu/qtribu/pull/222
* ui(qchat): set fixed height for an image chat item by @gounux in https://github.com/geotribu/qtribu/pull/221

### Bugs fixes 🐛

* fix(qchat): add type key check when receiving a message by @gounux in https://github.com/geotribu/qtribu/pull/218

## 1.0.0 - 2024-10-11

### Bugs fixes 🐛

* fix(qchat): use mp3 instead of ogg by @gounux in <https://github.com/geotribu/qtribu/pull/198>

### Features and enhancements 🎉

* improve(qchat): play sound only on mention by @gounux in <https://github.com/geotribu/qtribu/pull/199>
* update(ui): move misc groupbox to bottom in settings dialog by @Guts in <https://github.com/geotribu/qtribu/pull/205>
* UI: display avatars right into combobox by @Guts in <https://github.com/geotribu/qtribu/pull/206>
* update(i18n): refine translation to prepare next stable release by @Guts in <https://github.com/geotribu/qtribu/pull/207>

### Tooling 🔧

* update(ci): rm deprecated `set-output` command by @Guts in <https://github.com/geotribu/qtribu/pull/203>

## 1.0.0-beta3 - 2024-09-27

### Bugs fixes 🐛

* fix(init): remove QChat import outside try/except by @Guts in <https://github.com/geotribu/qtribu/pull/196>
* fix(qchat): no notification on self message mention by @gounux in <https://github.com/geotribu/qtribu/pull/197>

## 1.0.0-beta2 - 2024-09-07

### Tooling 🔧

* update(ci): switch to geotribu user as releases publisher to plugins.qgis.org and use a toiken instead of raw OSGeo password

## Other changes

* update(packaging): add French description by @Guts in <https://github.com/geotribu/qtribu/pull/194>
* update(packaging): add Guilhem as plugin contributor @gounux in <https://github.com/geotribu/qtribu/pull/193>

## 1.0.0-beta1 - 2024-09-07

### Features and enhancements 🎉

* feature: qchat by @gounux in <https://github.com/geotribu/qtribu/pull/182>
* feature: put settings in QScrollArea by @gounux in <https://github.com/geotribu/qtribu/pull/190>

## 0.18.0 - 2024-08-25

### Bugs fixes 🐛

* fix(web_viewer): switch from QtWebKit to QtWebEngine by @lbartoletti in <https://github.com/geotribu/qtribu/pull/186>

### Features and enhancements 🎉

* refacto(rss): remove unused rss reader subclasses by @Guts in <https://github.com/geotribu/qtribu/pull/184>
* Feature: add application folder by @Guts in <https://github.com/geotribu/qtribu/pull/187>
* refactor(rss): move RSS reader to its own folder by @Guts in <https://github.com/geotribu/qtribu/pull/188>

## New Contributors

* @lbartoletti made their first contribution in <https://github.com/geotribu/qtribu/pull/186>

## 0.17.3 - 2024-06-28

### Tooling 🔧

* fix(ci): copy LICENSE file since it's mandatory on official repository by @Guts in <https://github.com/geotribu/qtribu/pull/180>

## 0.17.2 - 2024-06-28

### Features and enhancements 🎉

* Retirer tri des colonnes by @gounux in <https://github.com/geotribu/qtribu/pull/177>

### Documentation 📖

* Doc: packaging by @gounux in <https://github.com/geotribu/qtribu/pull/178>

## 0.17.1 - 2024-05-01

### Bugs fixes 🐛

* fix(form-rdp): LOCAL_CDN_PATH was unreachable by @Guts in <https://github.com/geotribu/qtribu/pull/172>
* UI : corrige les étiquettes copiées/collées du formulaire RDP dans le formulaire article by @Guts in <https://github.com/geotribu/qtribu/pull/174>
* UI : corrige l'autopreview by @Guts in <https://github.com/geotribu/qtribu/pull/176>

### Features and enhancements 🎉

* ui(authoring): supprime la taille minimum pour améliorer l'intégration du widget authoring by @Guts in <https://github.com/geotribu/qtribu/pull/173>
* UI : améliore le redimensionnement automatique des formulaires de soumission by @Guts in <https://github.com/geotribu/qtribu/pull/175>

## 0.17.0 - 2024-05-01

### Features and enhancements 🎉

* Fenêtre contenus Geotribu by @gounux in <https://github.com/geotribu/qtribu/pull/157>
* feature(logs): permet de personnaliser la fenêtre dans laquelle afficher le message de log by @Guts in <https://github.com/geotribu/qtribu/pull/161>
* ui(forms): add message bars to forms by @Guts in <https://github.com/geotribu/qtribu/pull/162>
* feature(authoring): ajoute le compte Mastodon by @Guts in <https://github.com/geotribu/qtribu/pull/164>
* Refactorisation : utilise le Network Requests Manager de QGIS à la place de requests by @Guts in <https://github.com/geotribu/qtribu/pull/165>
* feature(forms): connecte le formulaires de soumission de news by @Guts in <https://github.com/geotribu/qtribu/pull/163>
* UI: amélioration générale du navigateur de contenus by @Guts in <https://github.com/geotribu/qtribu/pull/167>
* UI : MAJ des traductions by @Guts in <https://github.com/geotribu/qtribu/pull/168>
* UI : ajoute une toolbar dédiée au plugin by @Guts in <https://github.com/geotribu/qtribu/pull/169>
* feature(forms): connecte le formulaire d'article au formulaire GitHub by @Guts in <https://github.com/geotribu/qtribu/pull/170>
* UI: changer couleur des logos article et geordp by @gounux in <https://github.com/geotribu/qtribu/pull/171>

### Other Changes

* fix(webviewer): setWindowsTitle was failing when default browser is s… by @Guts in <https://github.com/geotribu/qtribu/pull/166>

### New Contributors

* @gounux made their first contribution in <https://github.com/geotribu/qtribu/pull/157>

----

## 0.16.0 - 2024-03-13

### Bugs fixes 🐛

* ci: fix i18n compilation by @Guts in <https://github.com/geotribu/qtribu/pull/156>

### Features and enhancements 🎉

* QtWebKitWidgets is no longer available by @kikislater in <https://github.com/geotribu/qtribu/pull/99>
* ui: regroupe les liens vers les sites FR de référence dans le menu Aide de QGIS by @Guts in <https://github.com/geotribu/qtribu/pull/153>
* Fonctionnalité : intègre le dernier contenu publié dans le fil d'actualité de QGIS by @Guts in <https://github.com/geotribu/qtribu/pull/154>
* ui: MAJ les traductions by @Guts in <https://github.com/geotribu/qtribu/pull/155>

### Tooling 🔧

* docs: use modern GitHub Actions based workflow by @Guts in <https://github.com/geotribu/qtribu/pull/146>
* ci: upgrade autolabeler to v5 by @Guts in <https://github.com/geotribu/qtribu/pull/149>
* ci: fix qgis tests by @Guts in <https://github.com/geotribu/qtribu/pull/150>

### Documentation 📖

* docs: add sitemap by @Guts in <https://github.com/geotribu/qtribu/pull/147>

### Other Changes

* Outillage: MAJ les dépendances de dév, la config VS Code et les git hooks by @Guts in <https://github.com/geotribu/qtribu/pull/144>
* packaging: pin minimal version of qgis-plugin-ci by @Guts in <https://github.com/geotribu/qtribu/pull/145>
* tooling: add SonarCloud config and badge by @Guts in <https://github.com/geotribu/qtribu/pull/148>
* test: replace semver by packaging by @Guts in <https://github.com/geotribu/qtribu/pull/151>

### New Contributors

* @kikislater made their first contribution in <https://github.com/geotribu/qtribu/pull/99>

----

## 0.15.0 - 2023-08-08

### Features and enhancements 🎉

* Formulaire de soumission de news pour les GeoRDP by @Guts in <https://github.com/geotribu/qtribu/pull/84>
* Simplifie le chargement des QgsSettings du plugin dans l'objet des préférences by @Guts in <https://github.com/geotribu/qtribu/pull/91>
* Ajoute un bouton pour réinitialiser les paramètres à leurs valeurs par défaut by @Guts in <https://github.com/geotribu/qtribu/pull/93>
* Change l'URL du site Geotribu by @Guts in <https://github.com/geotribu/qtribu/pull/127>

### Tooling 🔧

* Change to a maintained job to create release by @Guts in <https://github.com/geotribu/qtribu/pull/92>
* CI: use ubuntu-latest (22.04) and fix qt5 install by @Guts in <https://github.com/geotribu/qtribu/pull/111>
* Add ruff and pyupgrade as git hooks by @Guts in <https://github.com/geotribu/qtribu/pull/112>
* Set 3.28 as minimal version by @Guts in <https://github.com/geotribu/qtribu/pull/113>

## 0.15.0-beta2 - 2022-09-06

* CI/CD: fix release workflow
* add reset button to settings

## 0.15.0-beta1 - 2022-08-22

* Add form to create a news for GeoRDP #84

## 0.14.2 - 2022-08-05

* Hotfix renomme l'ancien nom d'un paramètre

## 0.14.1 - 2022-08-05

* Hotfix enlève un bout d'ancienne syntaxe de traduction

## 0.14.0 - 2022-08-05

* corrige le chargement de la traduction après que le module dédié ne fonctionne plus sur QGIS 3.22+
* améliore le module de log pour permettre de mieux personnaliser le `QgsMessageOutput`

## 0.13.0 - 2022-07-18

* corrige le lien vers l'aide dans le menu #78
* modernise la gestion des préférences en utilisant une dataclass
* actualise l'outillage (GitHub Actions, étiquetage automatique, etc.)

## 0.12.0 - 2022-07-12

* mise à jour des dépendances
* test sur la version 3.22
* publication sur le dépôt officiel des extensions

## 0.11.0 - 2022-03-17

* les traductions compilées (fichiers `*.qm`) sont désormais générées et automatiquement intégrées dans la CI - #34
* ajoute un lien vers le forum QGIS de GeoRezo

## 0.10.0 - 2022-01-02

* la requête vers le flux RSS attend désormais que l'application QGIS soit complètement chargée pour ne pas ralentir le lancement, en particulier quand la connexion réseau n'est pas idéale. Jusque-là elle était envoyée à la fin du chargement du plugin.
* la gestion de l'affichage du dernier contenu a été déportée dans un module dédié (WebViewer).

## 0.9.0 - 2021-08-12

* augmente la durée par défaut de la notification de 3 à 10 secondes
* permet à l'utilisateur de définir la durée de la notification

## 0.8.0 - 2021-08-11

* ajout d'un bouton pour effacer l'historique de consultation
* correction d'un bug dans la condition permettant d'afficher un bouton dans les notifications push
* améliorations mineures

## 0.7.0 - 2021-08-10

* ajout d'un bouton dans la notification pour ouvrir directement le dernier contenu
* simplification de la maintenance du formulaire des préférences

## 0.6.3 - 2021-06-14

* utilise les QgsSettings plutôt que l'édition du fichier ini pour activer la personnalisation de l'interface, pour cause d'inconsistance entre les systèmes d'exploitation, en particulier MacOS

## 0.6.2 - 2021-06-14

* améliore le mécanisme de changement du splash screen pour gérer les chemins Windows (ou plutôt leur stockage dans un .ini et interprétation par QGIS)

## 0.6.1 - 2021-06-11

* change le splash screen
* ajoute le lien vers l'article sur le splash screen dans la doc

## 0.6.0 - 2021-06-04

* prise en compte du mode debug
* activation du module permettant de changer/restaurer le splash screen ([voir l'article dédié](https://geotribu.fr/articles/2021/2021-06-17_qgis_personnaliser_splash_screen/))
* traduction en français et réduction du warning de non traduction. A noter que, contrairement aux bonnes pratiques de git, les fichiers `.qm` (binaires) sont stockés dans le dépôt, jusqu'à ce que [le ticket upstream](https://github.com/opengisch/qgis-plugin-ci/issues/47) soit résolu.
* documentation : ajout des balises OpenGraph, de pages manquantes et améliorations diverses
* CI : améliorations diverses (emojis...)

## 0.5.0 - 2021-05-30

* ajout du mécanisme permettant de notifier l'utilisateur si un nouveau contenu a été publié
* amélioration des paramètres

## 0.4.1 - 2021-04-09

* améliorations diverses :
  * meilleure gestion des paramètres du plugin
  * personnalisation des en-têtes pour les appels réseau

## 0.4.0 - 2021-04-01

* fin de la période de tests : publication dans le canal stable

## 0.3.1 - 2021-03-08

* corrige un problème de type lors de la récupération des options enregistrées

## 0.3.0 - 2021-03-06

* préférences : menu réglages, intégration des options à l'interface de QGIS
* ajout d'une option pour choisir dans quel navigateur internet ouvrir les pages : celui intégré à QGIS ou le navigateur par défaut de l'utilisateur/ice

## [0.2.1] - 2021-03-04

* correction d'un import d'un futur module pas encore inclus

## [0.2.0] - 2021-03-04

* ajout du raccourci vers l'aide en ligne
* déplacement du menu du plugin dans la catégorie "Web"

## [0.1.1] - 2021-03-03

* correction d'un bug avec les versions de Python inférieures à 3.8

## [0.1.0] - 2021-02-28

* première version !
* structure du dépôt et outillage de base (modularité, traduction, linter, documentation, packaging...)
* fonctionnellement, le plugin consiste en un bouton qui télécharge le flux RSS et affiche le dernier contenu publié dans le navigateur intégré à QGIS
