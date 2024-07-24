# Installation

## Dépendances

Certaines fonctionnalités du plugin reposent sur des dépendances logicielles tierces non incluses dans le packaging de QGIS sur certaines plateformes :

- QGISChat: QtWebSockets

### Linux

> Par exemple sur Ubuntu 22.04. Adapter à votre distribution.

Ouvrir un terminal et exécuter la commande suivante :

```sh
sudo apt install python3-pyqt5.qtwebsockets
```

----

## Version stable (recommandée)

Le plugin est publié sur le dépôt officiel des extensions de QGIS : <https://plugins.qgis.org/plugins/qtribu/>.

## Version stable depuis le projet Github (alternative)

En plus d'être publié dans le dépôt officiel de plugins de QGIS, QTribu est également disponible via son propre dépôt personnalisé. Dans QGIS :

1. Menu `Extensions` > `Installer/Gérer des extensions`
2. Onglet `Paramètres`
3. Sous la liste des dépôts, cliquer sur `Ajouter...` et renseigner :
    - Nom :

        ```txt
        Dépôt personnalisé du plugin QTribu
        ```

    - URL :  

    ```html
    https://github.com/geotribu/qtribu/releases/latest/download/plugins.xml
    ```

    ![QTribu - Dépôt](https://cdn.geotribu.fr/img/tuto/qgis_plugins_repository/qgis_plugins_repository_qtribu.png "QTribu - Dépôt")

4. Une fois le dépôt ajouté, l'extension devrait apparaître dans l'onglet `Non installées`. Cliquer sur `Installer` :

    ![QTribu - Non installée](https://cdn.geotribu.fr/img/tuto/qgis_plugins_repository/qgis_plugins_available_qtribu.png "QTribu - Non installée")

:::{warning}
Selon votre configuration, redémarrer QGIS peut être nécessaire, le gestionnaire d'extensions ayant des comportements parfois capricieux par rapport aux dépôts tiers.
:::

----

## Intégration dans QGIS

Une fois installé, le plugin s'intègre :

- dans le menu `Internet` :

![Menu QTribu](https://cdn.geotribu.fr/img/projets-geotribu/plugin_qtribu/qtribu_menu_plugin.png "Menu QTribu")

- dans la barre d'outils :

![Toolbar QTribu](https://cdn.geotribu.fr/img/projets-geotribu/plugin_qtribu/qtribu_toolbar.png "Toolbar QTribu")
