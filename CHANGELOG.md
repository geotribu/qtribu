# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## [{version_tag}](https://github.com/geotribu/qtribu/releases/tag/{version_tag}) - YYYY-DD-mm

### Added

- la requête vers le flux RSS attend désormais que l'application QGIS soit complètement chargée pour ne pas ralentir le lancement, en particulier quand la connexion réseau n'est pas idéale. Jusque-là elle était envoyée à la fin du chargement du plugin.
- la gestion de l'affichage du dernier contenu a été déportée dans un module dédié (WebViewer).

### Changed

### Removed

-->

## 0.9.0 - 2021-08-12

- augmente la durée par défaut de la notification de 3 à 10 secondes
- permet à l'utilisateur de définir la durée de la notification

## 0.8.0 - 2021-08-11

- ajout d'un bouton pour effacer l'historique de consultation
- correction d'un bug dans la condition permettant d'afficher un bouton dans les notifications push
- améliorations mineures

## 0.7.0 - 2021-08-10

- ajout d'un bouton dans la notification pour ouvrir directement le dernier contenu
- simplification de la maintenance du formulaire des préférences

## 0.6.3 - 2021-06-14

- utilise les QgsSettings plutôt que l'édition du fichier ini pour activer la personnalisation de l'interface, pour cause d'inconsistance entre les systèmes d'exploitation, en particulier MacOS

## 0.6.2 - 2021-06-14

- améliore le mécanisme de changement du splash screen pour gérer les chemins Windows (ou plutôt leur stockage dans un .ini et interprétation par QGIS)

## 0.6.1 - 2021-06-11

- change le splash screen
- ajoute le lien vers l'article sur le splash screen dans la doc

## 0.6.0 - 2021-06-04

- prise en compte du mode debug
- activation du module permettant de changer/restaurer le splash screen ([voir l'article dédié](https://static.geotribu.fr/articles/2021/2021-06-17_qgis_personnaliser_splash_screen/))
- traduction en français et réduction du warning de non traduction. A noter que, contrairement aux bonnes pratiques de git, les fichiers `.qm` (binaires) sont stockés dans le dépôt, jusqu'à ce que [le ticket upstream](https://github.com/opengisch/qgis-plugin-ci/issues/47) soit résolu.
- documentation : ajout des balises OpenGraph, de pages manquantes et améliorations diverses
- CI : améliorations diverses (emojis...)

## 0.5.0 - 2021-05-30

- ajout du mécanisme permettant de notifier l'utilisateur si un nouveau contenu a été publié
- amélioration des paramètres

## 0.4.1 - 2021-04-09

- améliorations diverses :
    - meilleure gestion des paramètres du plugin
    - personnalisation des en-têtes pour les appels réseau

## 0.4.0 - 2021-04-01

- fin de la période de tests : publication dans le canal stable

## 0.3.1 - 2021-03-08

- corrige un problème de type lors de la récupération des options enregistrées

## 0.3.0 - 2021-03-06

- préférences : menu réglages, intégration des options à l'interface de QGIS
- ajout d'une option pour choisir dans quel navigateur internet ouvrir les pages : celui intégré à QGIS ou le navigateur par défaut de l'utilisateur/ice

## [0.2.1] - 2021-03-04

- correction d'un import d'un futur module pas encore inclus

## [0.2.0] - 2021-03-04

- ajout du raccourci vers l'aide en ligne
- déplacement du menu du plugin dans la catégorie "Web"

## [0.1.1] - 2021-03-03

- correction d'un bug avec les versions de Python inférieures à 3.8

## [0.1.0] - 2021-02-28

- première version !
- structure du dépôt et outillage de base (modularité, traduction, linter, documentation, packaging...)
- fonctionnellement, le plugin consiste en un bouton qui télécharge le flux RSS et affiche le dernier contenu publié dans le navigateur intégré à QGIS
