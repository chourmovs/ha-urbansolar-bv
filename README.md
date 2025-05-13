# 🔋 UrbanSolar Battery – Intégration HACS pour Home Assistant

![HACS Integration](https://img.shields.io/badge/HACS-Integration-blue?logo=home-assistant)
![Home Assistant](https://img.shields.io/badge/Compatible-Home%20Assistant-41BDF5?logo=home-assistant)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

## 📚 Sommaire

1. [Ajouter le dépôt HACS](#1-ajouter-le-dépôt-hacs)  
2. [Installer l'intégration](#2-installer-lintégration)  
3. [Configuration](#3-configuration)  
4. [Entités & Automatisations](#4-entités--automatisations)  
5. [Dashboard Lovelace](#5-dashboard-lovelace)  
6. [Dépannage](#6-dépannage)  
7. [Auteur & Support](#7-auteur--support)

---

## 1. Ajouter le dépôt HACS

1. Ouvrez **HACS** dans Home Assistant.  
2. Allez dans l’onglet **Intégrations**.  
3. Cliquez sur **➕ Ajouter un dépôt personnalisé** et entrez l’URL :  
   `https://github.com/chourmovs/ha-urbansolar-bv`  
4. Sélectionnez **Catégorie : Intégration**.  
5. Cliquez sur **Enregistrer**

---

## 2. Installer l'intégration

1. Dans **HACS → Intégrations**, recherchez **UrbanSolar Battery**.  
2. Cliquez sur **Télécharger**.  
3. **Redémarrez Home Assistant**.

### 📦 Dépendances Lovelace requises

L’intégration utilise plusieurs cartes Lovelace que vous devez installer via HACS :

| Carte Lovelace              | Dépôt GitHub                                                   |
|----------------------------|----------------------------------------------------------------|
| ApexCharts Card            | [apexcharts-card](https://github.com/RomRider/apexcharts-card) |
| Vertical Stack In Card     | [vertical-stack-in-card](https://github.com/custom-cards/vertical-stack-in-card) |
| Number Box Card            | [number-box-card](https://github.com/custom-cards/number-box-card) |
| Energy Flow Card Plus      | [energy-flow-card-plus](https://github.com/flixlix/energy-flow-card-plus) |
| Power Flow Card Plus       | [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus) |

> **N'oubliez pas de redémarrer Home Assistant** après installation.

---

## 3. 🔧 Configuration

Lors de l’ajout de l’intégration, une boîte de dialogue vous demandera de sélectionner :

1. **Capteur de puissance totale consommée** (ex : `sensor.puissance_totale_consommee`)  
2. **Capteur de puissance solaire produite** (ex : `sensor.pv_energie_solaire`)

> ⚠️ Assurez-vous que ces capteurs renvoient une puissance en **kW**.

Si la boîte de dialogue ne s’affiche pas :  
→ **Paramètres → Intégrations → ➕ Ajouter** → **Urban Solar Battery**.

Ensuite, ajoutez dans votre `configuration.yaml` :

```yaml
#Urban solar
input_number: !include urban_input_numbers.yaml
sensor: !include urban_integrations.yaml
template: !include urban_sensors.yaml
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
<pre lang="yaml"><code>
   configuration.yaml, cas de la double source d'entité (ici exemple classique des automations, à adapter aux autres entités)

   ```yaml
   # Automatisations globales 
   automation: !include automations.yaml 
   # Automatisations spécifiques à UrbanSolar 
   automation urban: !include urban_automations.yaml</code></pre>```
---
→**Redémarrez Home Assistant après avoir enregistré configuration.yaml**


## 4. 🌐 Entités & Automatisations

### Capteurs créés automatiquement

| Entité | Description |
|--------|-------------|
| `sensor.urban_energie_restituee_au_reseau` | Énergie solaire excédentaire envoyée au réseau |
| `sensor.urban_puissance_import_enedis` | Puissance importée du réseau en temps réel |
| `sensor.urban_energie_importee_enedis` | Intégration de la puissance importée |
| `sensor.urban_puissance_solaire_instant` | Puissance solaire instantanée |
| `sensor.urban_conso_totale_instant` | Puissance totale consommée |
| `sensor.urban_batterie_virtuelle_stock` | Stock actuel de la batterie virtuelle |
| `sensor.urban_batterie_virtuelle_entree_horaire` | Entrée horaire vers batterie virtuelle |
| `sensor.urban_batterie_virtuelle_sortie_horaire` | Sortie horaire depuis la batterie virtuelle |

### Input Numbers

- `input_number.urban_batterie_virtuelle_stock`
- `input_number.urban_energie_restituee_veille`

### Automatisations incluses

- Mise à jour quotidienne du stock de la batterie
- Calcul différentiel sur l’énergie exportée
- Mise à jour manuelle possible via Number Box

---

## 5. 🎨 Dashboard Lovelace

Un **dashboard complet** est installé automatiquement via `urban_dashboard.yaml` :  
- Visualisation du flux d’énergie  
- Courbes de production et de consommation  
- Suivi du stock de la batterie virtuelle
- 2 capteurs ad'hoc disponibles pour configurer le dashboard **Energy** pour la partie batterie :
    `sensor.urban_batterie_virtuelle_entree_horaire`
    `sensor.urban_batterie_virtuelle_sortie_horaire`, pensez aussi a supprimer l'énergie retournée au réseau car l'énergie retourrne a la batterie ^^

![Capture d'écran de l'application](https://i.imgur.com/vUdDOOh.png)
![Capture d'écran de l'application](https://i.imgur.com/FN5RG13.png)
![Capture d'écran de l'application](https://imgur.com/a/sFu0WaL)
---

## 6. ❗ Dépannage

- **Capteur manquant (`sensor.urban_energie_restituee_au_reseau`) ?**  
  → Vérifiez votre configuration YAML et les logs de Home Assistant.

- **Pas de mise à jour nocturne ?**  
  → Assurez-vous que votre timezone est correcte.  

---

## 7. 📝 Auteur & Support

- **Auteur** : [chourmovs](https://github.com/chourmovs)  
- **Support & bugs** : [Issues GitHub](https://github.com/chourmovs/ha-urbansolar-bv/issues)

---

Merci d’utiliser **UrbanSolar Battery** ⚡️ pour optimiser votre autoconsommation solaire ! 🌞
