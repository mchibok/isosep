
# exécuter avec
#exec(open("D:/outils_py/isosep/script.py".encode("UTF-8")).read())
#exec(open("/home/mik/repos/isosep/script.py").read())

# nom de la couche à séparer
#nom_couche = "isochrone_2019-08-19T16_00_du_TLO_intervalles_5_max_60_marche_800"

# importation des éléments de pyqgis
from qgis.core import *

# nécessité de réparer les géométries du geojson
param_rep = {
	"INPUT" : nom_couche,
	"OUTPUT" : "TEMPORARY_OUTPUT"
}
algo_rep = processing.run("qgis:fixgeometries", param_rep)["OUTPUT"]
algo_rep.setName("rep")
QgsProject.instance().addMapLayer(algo_rep)

# 1. sélection valeurs de temps uniques (différentes entités)
layer = algo_rep
# 1.1 index de la colonne time dans variable idx
idx = layer.fields().indexOf("time")
# 1.2 ordonner les valeurs du plus grand au plus petit
values = sorted(layer.uniqueValues(idx), reverse = True)
# 1.3 déselectionner tout
layer.removeSelection()
# 1.4 initialiser le vecteur array vide qui sert à mettre chaque valeur de time en texte
array = []

# 2. initialisation de la boucle de la plus grosse valeur à la plus petite
# isochrone = i
for i in range(len(values)):
	# insère la valeur time en texte dans le vecteur array
	array.append(str(values[i]))
	layer.removeSelection()
	print(str(values[i]))
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
			"INPUT": QgsProcessingFeatureSourceDefinition(algo_rep.name(), True),
			"OUTPUT": "TEMPORARY_OUTPUT"
		}
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
			"INPUT": QgsProcessingFeatureSourceDefinition(algo_rep.name(), True),
			"OUTPUT": "TEMPORARY_OUTPUT",
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
# 3.1 répertoire de la couche originale
layer_orig = QgsProject.instance().mapLayersByName(nom_couche)[0]
chemin = os.path.dirname(unicode(layer_orig.dataProvider().dataSourceUri()))+"/"+nom_couche+"_separe.shp"
params_fusion = {
	"LAYERS": array,
	"OUTPUT": chemin
	#"OUTPUT": "TEMPORARY_OUTPUT"
}
algo_fusion = processing.run("qgis:mergevectorlayers", params_fusion)["OUTPUT"]
# 3.2 ajoute la couche au canevas
layer_sep = QgsVectorLayer(chemin, nom_couche+"_séparé") 
QgsProject.instance().addMapLayer(layer_sep)
QgsProject.instance().removeMapLayer(algo_rep)

# 4 ôte les couches temporaires
for i in range(len(values)):
	temp = QgsProject.instance().mapLayersByName(str(values[i]))[0]
	QgsProject.instance().removeMapLayer(temp)

