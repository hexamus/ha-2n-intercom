# Intégration Home Assistant 2N Intercom

Intégration personnalisée pour Home Assistant permettant de contrôler les parlophones et écrans 2N IP Intercom via leur API HTTP.

## 🎯 Fonctionnalités

### Switches
- **Switches matériels** : Contrôle des relais de porte (ouverture de porte, activation de la gâche, etc.)
- **Sorties IO** : Contrôle des sorties configurables

### Binary Sensors
- **Entrées IO** : Surveillance des entrées (détection de porte ouverte, bouton d'appel, etc.)
- **État d'appel** : Détection d'un appel en cours

### Camera
- **Snapshot caméra** : Visualisation en temps réel de la caméra du parlophone

### Sensors
- **Uptime** : Temps de fonctionnement de l'appareil
- **Température** : Température interne de l'appareil
- **État téléphone** : État de l'enregistrement SIP

### Buttons
- **Répondre** : Répondre à un appel entrant
- **Raccrocher** : Terminer un appel en cours
- **Redémarrer** : Redémarrer l'appareil

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur les trois points en haut à droite
3. Sélectionnez "Dépôts personnalisés"
4. Ajoutez l'URL de ce dépôt : `https://github.com/hexamus/ha-2n-intercom`
5. Sélectionnez la catégorie "Integration"
6. Cliquez sur "2N IP Intercom" dans la liste des intégrations
7. Cliquez sur "Télécharger"
8. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez les fichiers de ce dépôt
2. Copiez le dossier `custom_components/2n_intercom` dans votre dossier `custom_components` de Home Assistant
3. Redémarrez Home Assistant

## ⚙️ Configuration

### Via l'interface utilisateur (recommandé)

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur le bouton **"+ Ajouter une intégration"**
3. Recherchez **"2N IP Intercom"**
4. Entrez les informations suivantes :
   - **Hôte** : Adresse IP de votre parlophone 2N
   - **Nom d'utilisateur** : Nom d'utilisateur de l'API (compte admin ou utilisateur avec droits API)
   - **Mot de passe** : Mot de passe du compte
   - **Port** : Port HTTP (par défaut : 80)

### Via configuration.yaml (legacy)

```yaml
2n_intercom:
  host: 192.168.1.100
  username: admin
  password: votre_mot_de_passe
  port: 80  # optionnel, défaut: 80
  scan_interval: 30  # optionnel, défaut: 30 secondes
```

## 🔧 Prérequis sur l'appareil 2N

1. **Activer l'API HTTP** :
   - Connectez-vous à l'interface web de votre parlophone 2N
   - Allez dans **Services** → **HTTP API**
   - Activez l'API HTTP
   - Assurez-vous que l'authentification est activée

2. **Créer un compte utilisateur** (recommandé) :
   - Allez dans **System** → **Users**
   - Créez un compte dédié pour Home Assistant
   - Attribuez les droits nécessaires (au minimum : API access)

## 📱 Appareils compatibles

Cette intégration est compatible avec les parlophones 2N suivants :
- 2N IP Verso
- 2N IP Style
- 2N IP Force
- 2N IP Solo
- 2N IP Base
- 2N IP Uni
- 2N LTE Verso
- 2N Indoor Touch/View/Compact
- Et autres modèles supportant l'API HTTP

## 🎬 Exemples d'automatisations

### Ouvrir la porte quand quelqu'un sonne

```yaml
automation:
  - alias: "Ouvrir porte automatiquement"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
```

### Prendre un snapshot quand quelqu'un appuie sur le bouton

```yaml
automation:
  - alias: "Snapshot sur appel"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_input_1
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.2n_camera
        data:
          filename: "/config/www/snapshots/2n_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

### Notification sur appel entrant

```yaml
automation:
  - alias: "Notification appel parlophone"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Appel parlophone"
          message: "Quelqu'un sonne à la porte"
          data:
            image: "/api/camera_proxy/camera.2n_camera"
            actions:
              - action: "OPEN_DOOR"
                title: "Ouvrir"
              - action: "ANSWER_CALL"
                title: "Répondre"
```

### Script pour ouvrir la porte avec notification

```yaml
script:
  open_front_door:
    alias: "Ouvrir la porte d'entrée"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
      - service: notify.persistent_notification
        data:
          message: "Porte ouverte"
```

## 🐛 Dépannage

### L'intégration ne se connecte pas

1. Vérifiez que l'API HTTP est activée sur votre parlophone 2N
2. Vérifiez l'adresse IP et les identifiants
3. Assurez-vous que Home Assistant peut accéder au réseau du parlophone
4. Vérifiez les logs Home Assistant : **Configuration** → **Logs**

### Les entités ne s'affichent pas

1. Certaines entités nécessitent des fonctionnalités spécifiques (switches, IO, caméra)
2. Vérifiez que votre modèle supporte ces fonctionnalités
3. Consultez les logs pour voir les erreurs éventuelles

### La caméra ne fonctionne pas

1. Vérifiez que la caméra est activée sur votre parlophone
2. Certains modèles peuvent nécessiter une configuration spécifique
3. Essayez d'accéder manuellement à : `http://IP_PARLOPHONE/api/camera/snapshot`

## 📚 Documentation

- [Documentation officielle API 2N](https://wiki.2n.com/hip/hapi/latest/en)
- [Forum Home Assistant](https://community.home-assistant.io/)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des pull requests

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- 2N pour leur API HTTP bien documentée
- La communauté Home Assistant pour leur support

## ⚠️ Avertissement

Cette intégration n'est pas officiellement supportée par 2N. Utilisez-la à vos propres risques.
