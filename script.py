
# nom de la couche à séparer
nom_couche = "isochrone_2019-08-19T08_00"

# importation des éléments de pyqgis
from qgis.core import *
# 1. sélection valeurs de temps uniques (différentes entités)
# 1.1 insère les entités dans la variable layer
layer = QgsProject.instance().mapLayersByName(nom_couche)[0]
# 1.2 index de la colonne time dans variable idx
idx = layer.fields().indexOf("time")
# 1.3 ordonner les valeurs du plus grand au plus petit
values = sorted(layer.uniqueValues(idx), reverse = True)
# 1.4 déselectionner tout
layer.removeSelection()
# 1.5 initialiser le vecteur array vide qui sert à mettre chaque valeur de time en texte
array = []

# 2. initialisation de la boucle de la plus grosse valeur à la plus petite
# isochrone = i
for i in range(len(values)):
    # insère la valeur time en texte dans le vecteur array
    array.append(str(values[i]))
    # on fait les opérations suivantes seulement si ce n'est pas le plus petit isochrone
    if values[i] != layer.minimumValue(idx):
        # sélection entités inférieures à isochrone i
        selection = "time<"+str(values[i])
        expr = QgsFeatureRequest(QgsExpression(selection)).setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([])
        it = layer.getFeatures(QgsFeatureRequest(expr))
        ids = [id.id() for id in it]
        layer.selectByIds(ids)
        # dissolve/regroupement les entités inférieures à i
        param_diss = {
            "INPUT": QgsProcessingFeatureSourceDefinition(nom_couche, True),
            "OUTPUT": 'TEMPORARY_OUTPUT'}
        algo_diss = processing.run("qgis:dissolve", param_diss)["OUTPUT"]
        # ajout de la couche fusionnée algo_diss des entités inférieures à i
        QgsProject.instance().addMapLayer(algo_diss)
        # sélection de l'isochrone i
        selection = "time="+str(values[i])
        expr = QgsFeatureRequest(QgsExpression(selection)).setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([])
        it = layer.getFeatures(QgsFeatureRequest(expr))
        ids = [id.id() for id in it]
        layer.selectByIds(ids)
        # différence de l'entité i et des entités inférieures à i (algo_diss)
        params_diff = {
            "INPUT": QgsProcessingFeatureSourceDefinition(nom_couche, True),
            #"INPUT": "inf_i",
            "OUTPUT": 'TEMPORARY_OUTPUT',
            "OVERLAY": algo_diss.name()
        }
        algo_diff = processing.run("qgis:difference", params_diff)["OUTPUT"]
        # enlever les entités fusionnées inférieures à i (algo_diss)
        QgsProject.instance().removeMapLayer(algo_diss)
        # nomme la couche différence avec la valeur time de l'isochrone i
        algo_diff.setName(str(values[i]))
        # ajoute cette couche au canevas
        QgsProject.instance().addMapLayer(algo_diff)
        # enlever toute sélection
        layer.removeSelection()
    # si l'isochrone i est le plus petit
    elif values[i] == layer.minimumValue(idx):
        # on le sélectionne
        selection = "time="+str(values[i])
        expr = QgsFeatureRequest(QgsExpression(selection)).setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes([])
        it = layer.getFeatures(QgsFeatureRequest(expr))
        ids = [id.id() for id in it]
        layer.selectByIds(ids)
        # on en créée une couche en mémoire
        min_iso = layer.materialize(QgsFeatureRequest().setFilterFids(layer.selectedFeatureIds()))
        # nomme la couche avec la valeur time de l'isochrone i
        min_iso.setName(str(values[i]))
        # ajoute cette couche au canevas
        QgsProject.instance().addMapLayer(min_iso)
        # enlever toute sélection
        layer.removeSelection()

# 3. fusion (merge) de toutes les couches distinctes des différents temps
params_fusion = {
    "LAYERS": array,
    "OUTPUT": "TEMPORARY_OUTPUT"
    }
algo_fusion = processing.run("qgis:mergevectorlayers", params_fusion)["OUTPUT"]
# 3.1 nomme la couche comme l'entrante en ajoutant '_séparé'
algo_fusion.setName(nom_couche+"_séparé")
# 3.2 ajoute la couche au canevas
QgsProject.instance().addMapLayer(algo_fusion)

# 4 ôte les couches temporaires
for i in range(len(values)):
    temp = QgsProject.instance().mapLayersByName(str(values[i]))[0]
    QgsProject.instance().removeMapLayer(temp)

