# 🚀 UrbanSolar Battery — Instructions

![HACS Integration](https://img.shields.io/badge/HACS-Integration-blue?logo=home-assistant)
![Home Assistant](https://img.shields.io/badge/Compatible-Home%20Assistant-41BDF5?logo=home-assistant)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

## 📚 Sommaire
- [1. Ajouter le dépôt HACS](#1-ajouter-le-dépôt-hacs)
- [2. Installer l'intégration](#2-installer-lintégration)
- [3. Configuration](#3-configuration)
- [4. Entités et Automatisations](#4-entités-et-automatisations)
- [5. Interface Lovelace](#5-interface-lovelace)
- [6. Troubleshooting](#6-troubleshooting)
- [7. Auteur & Support](#7-auteur--support)

---

## 1. Ajouter le dépôt HACS
1. Ouvrez **HACS** dans Home Assistant.
2. Allez dans **Intégrations**.
3. Cliquez sur **➕ Ajouter un dépôt personnalisé** et entrez :
[https://github.com/chourmovs/ha-urbansolar-bv]

4. Sélectionnez **Catégorie : Intégration**.
5. Cliquez sur **Save and Refresh**.

---


## 2. Installer l'intégration

1. Dans **HACS → Intégrations**, recherchez **UrbanSolar Battery**.
2. Cliquez sur **Télécharger**.
3. **Redémarrez Home Assistant**.

### 🔗 Dépendances HACS à ajouter

UrbanSolar Battery s’appuie sur plusieurs cartes Lovelace : vous devez donc installer ces 3 plugins via HACS  :

| Carte                         | Dépôt GitHub                                                     |
|:------------------------------|:-----------------------------------------------------------------|
| ApexCharts Card               | https://github.com/RomRider/apexcharts-card                     |
| Vertical Stack In Card        | https://github.com/custom-cards/vertical-stack-in-card          |
| Number Box Card               | https://github.com/custom-cards/number-box-card                 |
| Energy Flow Card Plus         | https://github.com/flixlix/energy-flow-card-plus                |
| Power Flow Card Plus          | https://github.com/flixlix/power-flow-card-plus                 |



**Redémarrer Home Assistant** (nécessaire pour charger les nouvelles ressources).

---



## 3. 🔧 Configuration

Lors de l’ajout de l’intégration **Urban Solar Battery**, une boîte de dialogue vous invite à sélectionner **deux capteurs** :

1. **Énergie totale consommée**  
   (ex : `sensor.puissance_totale_consommee`)
2. **Énergie totale solaire produite**  
   (ex : `sensor.pv_energie_solaire`)

> ⚠️ Assurez-vous que les deux capteurs utilisent l’unité **kWh** !

Si la boîte de dialogue n’apparaît pas automatiquement :  
**Paramètres → Intégrations → ➕ Ajouter** → **Urban Solar Battery**.


Après redémarrage, ajoutez dans votre `configuration.yaml` :

```yaml
#Urban solar 
input_number: !include urban_input_numbers.yaml
sensor: !include urban_sensors.yaml
utility_meter: !include urban_utility_meters.yaml
automation: !include urban_automations.yaml


lovelace:
  mode: yaml
  resources:
    - url: /hacsfiles/apexcharts-card/apexcharts-card.js
      type: module
    - url: /hacsfiles/vertical-stack-in-card/vertical-stack-in-card.js
      type: module
    - url: /hacsfiles/numberbox-card/numberbox-card.js
      type: module
    - url: /hacsfiles/power-flow-card-plus/power-flow-card-plus.js
      type: module
    - url: /hacsfiles/energy-flow-card-plus/energy-flow-card-plus.js
      type: module

  dashboards:
    urban-dashboard:
      title: Urban Solar Dashboard
      mode: yaml
      filename: urban_dashboard.yaml
```
---

## 4. 🌐 Entités et Automatisations

### Capteurs créés
| Entité | Description |
|:---|:---|
| `sensor.energie_restituee_au_reseau` | Basé sur votre capteur source |
| `sensor.diff_energie_restituee_veille_avant_veille` | Calcul de la différence journalière |

### Input Numbers
- `input_number.energie_restituee_veille`
- `input_number.batterie_virtuelle_stock`

### Automatisations
- Mise à jour nocturne
- Gestion des plages horaires

---

## 5. 🎨 Interface Lovelace
Un dashboard est préconfiguré 

---

## 6. ❗ Troubleshooting

- **Pas de `sensor.energie_restituee_au_reseau` ?**
- Vérifiez la configuration et consultez les logs HACS.

- **Valeurs non mises à jour la nuit ?**
- Vérifiez votre timezone dans Home Assistant.
- Vérifiez que le capteur source est accessible.

---

## 7. 📝 Auteur & Support

- **Auteur** : chourmovs
- **Bugs / Support** : [GitHub Issues](https://github.com/chourmovs/ha-urbansolar-bv/issues)

Merci d'utiliser UrbanSolar Battery 🌞 !
