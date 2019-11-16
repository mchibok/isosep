# isosep
> script python pour créer des entités distinctes dans QGIS à partir d'isochrones provenant d'OTP

## exécution dans QGIS
1. afficher couche/geojson à séparer
2. ouvrir console python dans QGIS
    - extension >> console python
3. inscrire nom de la couche à séparer dans console
    - exemple: `nom_couche = "isochrone_2019-08-19T08_00_de_-73.49258559937294,45.51919069508378"`
4. exécuter le script dans la console en substituant le nom du répertoire où il est situé
    - `exec(open("D:/DOSSIER/script.py".encode("UTF-8")).read())`