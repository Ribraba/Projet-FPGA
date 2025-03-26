#READ ME

Ce dossier contient tous les éléments du développement permettant de réaliser une analyse d’électrocardiogrammes (ECG) 
en communiquant de manière sécurisée par une liaison UART grâce au chiffrage et déchiffrage par la méthode de chiffrement ASCON-128.
Il contient notamment, la fonction de chaque élément est défini dans le quickstart :

-Quickstart guide
-inter_spartan: le bitstream généré du chiffrement 
-PROJET_FPGA_ASCON_SV: le dossier contenant les sources et l'environnement ayant généré le bitstream précédent 
-Une présentation Power Point contenant les schémas de l'architecture du hardware
-Un environnment Python 

NB: Il faut noter que nous proposons deux version de codes Python pour analyser les PQRST des ECG :
-ecg_plotter.py : utilisant Neurokit2 permet uniquement le calcul des pics R avec une grande précision
-ecg_plotter_err.py : utilisant signal de la bibliothèque scipy calcul des pics PQRST avec beaucoup d'imprécision
Pour changer d'analyse il suffit de renommer le fichier appelé