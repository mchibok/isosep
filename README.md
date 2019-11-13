# isosep
> Script PYTHON pour créer des entités distinctes dans QGIS à partir d'isochrones provenant d'OTP

## utilisation
- Afficher couche à séparer dans QGIS (geojson ou shapefile)
- Ouvrir *script.py*
    - Mettre le nom de couche à séparer
    - exemple: `nom_couche = "isochrone_2019-08-19T08_00"`
    - Copier l'ensemble du script (`ctrl`+`a`, `ctrl`+`c`)
- Ouvrir console python dans QGIS
    - Extension >> console python
- Coller le script copié dans la console python (`ctrl`+`v`)
    - Appuyer `enter` deux fois
- Couche générée est en mémoire >> **ne pas oublier de sauvegarder**
