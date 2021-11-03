# Projet Data RTE

## Données
Les données viennent de l'API "Actual Generation" de RTE qui sont accessibles via le protocol Oauth2, et mise à jour toutes les heures 
https://data.rte-france.com/catalog/-/api/generation/Actual-Generation/v1.1?fbclid=IwAR04Vwn0ixY3z9eauJufcl-CYQpLW6MMyk3wmXboTpyPXmGpEkXFjOW5bTM

## Architecture 
Comme nous souhaitons réaliser un projet type dashbord, j'ai choisit le framework python [Streamlit](https://streamlit.io/) (Flask) permettant de développer un serveur rapidement sans se soucier de la structure html/css. Le code va donc requêter toutes le 5 minutes le site de RTE pour actualiser les courbes.

## Captures d'écran

