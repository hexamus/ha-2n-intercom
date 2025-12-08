# Exemples d'utilisation avancée

## Configuration complète d'un système d'interphone

### 1. Dashboard Lovelace pour contrôle du parlophone

```yaml
type: vertical-stack
cards:
  # Caméra en direct
  - type: picture-entity
    entity: camera.2n_camera
    camera_view: live
    name: Entrée principale
    
  # Statuts
  - type: horizontal-stack
    cards:
      - type: entity
        entity: binary_sensor.2n_call_active
        name: Appel en cours
      - type: entity
        entity: sensor.2n_phone_state
        name: État SIP
      - type: entity
        entity: sensor.2n_temperature
        name: Température
        
  # Contrôles principaux
  - type: entities
    title: Contrôles
    entities:
      - entity: switch.2n_switch_1
        name: Ouvrir la porte
        icon: mdi:door-open
      - entity: switch.2n_switch_2
        name: Gâche électrique
        icon: mdi:gate
      - entity: button.2n_answer
        name: Répondre
      - entity: button.2n_hangup
        name: Raccrocher
        
  # Entrées
  - type: entities
    title: Détecteurs
    entities:
      - entity: binary_sensor.2n_input_1
        name: Bouton d'appel
      - entity: binary_sensor.2n_input_2
        name: Porte ouverte
```

### 2. Automatisation complète avec notifications enrichies

```yaml
automation:
  # Notification lors d'un appel avec snapshot
  - id: '2n_call_notification'
    alias: "Notification appel parlophone avec photo"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: 'on'
    action:
      # Prendre un snapshot
      - service: camera.snapshot
        target:
          entity_id: camera.2n_camera
        data:
          filename: '/config/www/snapshots/visitor_{{ now().timestamp() | int }}.jpg'
      
      # Envoyer une notification avec l'image
      - service: notify.mobile_app_iphone
        data:
          title: "🔔 Quelqu'un sonne"
          message: "Un visiteur à la porte d'entrée"
          data:
            image: '/local/snapshots/visitor_{{ now().timestamp() | int }}.jpg'
            actions:
              - action: "OPEN_DOOR"
                title: "Ouvrir"
                icon: "sfsymbols:door.left.hand.open"
              - action: "ANSWER_CALL"
                title: "Répondre"
                icon: "sfsymbols:phone.fill"
              - action: "IGNORE"
                title: "Ignorer"
                icon: "sfsymbols:hand.raised.fill"
                destructive: true
      
      # Allumer les lumières de l'entrée
      - service: light.turn_on
        target:
          entity_id: light.entree
        data:
          brightness: 255
      
      # Enregistrer dans l'historique
      - service: logbook.log
        data:
          name: "Parlophone"
          message: "Appel reçu à la porte d'entrée"
          entity_id: binary_sensor.2n_call_active

  # Gestion des actions de la notification
  - id: '2n_notification_actions'
    alias: "Actions notification parlophone"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: 'OPEN_DOOR'
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: 'ANSWER_CALL'
    action:
      - choose:
          # Ouvrir la porte
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'OPEN_DOOR' }}"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.2n_switch_1
              - service: notify.mobile_app_iphone
                data:
                  message: "Porte ouverte ✅"
          
          # Répondre à l'appel
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'ANSWER_CALL' }}"
            sequence:
              - service: button.press
                target:
                  entity_id: button.2n_answer
              - service: notify.mobile_app_iphone
                data:
                  message: "Communication établie 📞"
```

### 3. Contrôle d'accès intelligent

```yaml
automation:
  # Ouverture automatique pour famille (détection présence)
  - id: '2n_auto_open_family'
    alias: "Ouverture auto pour la famille"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: 'on'
    condition:
      # Vérifier qu'un membre de la famille est proche
      - condition: or
        conditions:
          - condition: state
            entity_id: person.papa
            state: 'home'
          - condition: state
            entity_id: person.maman
            state: 'home'
      # Vérifier l'heure (pas la nuit)
      - condition: time
        after: '07:00:00'
        before: '23:00:00'
    action:
      # Attendre 2 secondes
      - delay: 00:00:02
      # Ouvrir si l'appel est toujours actif
      - condition: state
        entity_id: binary_sensor.2n_call_active
        state: 'on'
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
      - service: 2n_intercom.display_text
        data:
          text: "Bienvenue !"
          size: 30
          color: "#00FF00"
      - service: notify.family
        data:
          message: "Porte ouverte automatiquement"

  # Mode invité avec code PIN
  - id: '2n_guest_access'
    alias: "Accès invité avec code"
    trigger:
      - platform: state
        entity_id: input_text.guest_code
        to: '1234'  # Code PIN invité
    condition:
      - condition: state
        entity_id: input_boolean.guest_mode
        state: 'on'
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
      - service: input_text.set_value
        target:
          entity_id: input_text.guest_code
        data:
          value: ''
      - service: notify.admin
        data:
          message: "Accès invité utilisé"
```

### 4. Surveillance et sécurité

```yaml
automation:
  # Détection d'intrusion (porte forcée)
  - id: '2n_door_forced'
    alias: "Alerte porte forcée"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_input_2  # Capteur de porte
        to: 'on'
    condition:
      # Porte ouverte sans activation du switch
      - condition: state
        entity_id: switch.2n_switch_1
        state: 'off'
        for:
          seconds: 5
    action:
      # Alerte immédiate
      - service: notify.critical
        data:
          title: "⚠️ ALERTE SÉCURITÉ"
          message: "Porte forcée détectée !"
          data:
            push:
              sound:
                name: "default"
                critical: 1
                volume: 1.0
      # Prendre plusieurs photos
      - repeat:
          count: 5
          sequence:
            - service: camera.snapshot
              target:
                entity_id: camera.2n_camera
              data:
                filename: '/config/www/security/intrusion_{{ now().timestamp() | int }}_{{ repeat.index }}.jpg'
            - delay: 00:00:01
      # Activer l'alarme si disponible
      - service: alarm_control_panel.alarm_trigger
        target:
          entity_id: alarm_control_panel.maison

  # Enregistrement des événements
  - id: '2n_log_events'
    alias: "Journalisation événements parlophone"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.2n_call_active
          - switch.2n_switch_1
          - binary_sensor.2n_input_1
          - binary_sensor.2n_input_2
    action:
      - service: script.log_to_file
        data:
          message: "{{ trigger.to_state.entity_id }} changé de {{ trigger.from_state.state }} à {{ trigger.to_state.state }}"
```

### 5. Interface tactile avec contrôle vocal

```yaml
# Script pour contrôle vocal
script:
  parlophone_ouvrir:
    alias: "Ouvrir la porte"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
      - service: tts.google_translate_say
        data:
          entity_id: media_player.google_home
          message: "J'ouvre la porte"

  parlophone_repondre:
    alias: "Répondre au parlophone"
    sequence:
      - service: button.press
        target:
          entity_id: button.2n_answer
      - service: tts.google_translate_say
        data:
          entity_id: media_player.google_home
          message: "Communication établie avec le visiteur"

# Configuration Google Assistant / Alexa
intent_script:
  OuvrirPorte:
    speech:
      text: "J'ouvre la porte d'entrée"
    action:
      - service: script.parlophone_ouvrir

  RepondrePorte:
    speech:
      text: "Je réponds au parlophone"
    action:
      - service: script.parlophone_repondre
```

### 6. Services personnalisés avancés

```yaml
# Script pour afficher des messages personnalisés
script:
  2n_welcome_message:
    alias: "Message de bienvenue"
    fields:
      name:
        description: "Nom du visiteur"
        example: "Jean"
    sequence:
      - service: 2n_intercom.display_text
        data:
          text: "Bienvenue {{ name }} !"
          size: 25
          color: "#0088FF"
          x: 50
          y: 100
      - delay:
          seconds: 5
      - service: 2n_intercom.display_text
        data:
          text: ""  # Effacer l'écran

  2n_delivery_mode:
    alias: "Mode livraison"
    sequence:
      - service: 2n_intercom.display_text
        data:
          text: "LIVRAISON\nDéposer le colis"
          size: 20
          color: "#FF8800"
      - service: switch.turn_on
        target:
          entity_id: switch.2n_switch_1
      - delay:
          seconds: 10
      - service: 2n_intercom.display_text
        data:
          text: "Merci !"
          size: 30
          color: "#00FF00"
```

### 7. Node-RED Flow (si vous utilisez Node-RED)

```json
[
    {
        "id": "call_detect",
        "type": "server-state-changed",
        "name": "Appel détecté",
        "server": "home_assistant",
        "version": 4,
        "entityidfilter": "binary_sensor.2n_call_active",
        "entityidfiltertype": "exact",
        "outputinitially": false,
        "state_type": "str",
        "to": "on"
    },
    {
        "id": "take_snapshot",
        "type": "api-call-service",
        "name": "Prendre photo",
        "server": "home_assistant",
        "version": 5,
        "service_domain": "camera",
        "service": "snapshot",
        "data": "{\"entity_id\":\"camera.2n_camera\",\"filename\":\"/config/www/visitor.jpg\"}"
    },
    {
        "id": "send_notification",
        "type": "api-call-service",
        "name": "Notifier",
        "server": "home_assistant",
        "service_domain": "notify",
        "service": "mobile_app",
        "data": "{\"message\":\"Visiteur à la porte\",\"data\":{\"image\":\"/local/visitor.jpg\"}}"
    }
]
```

## Conseils de sécurité

1. **Utilisez HTTPS** pour la communication avec le parlophone si possible
2. **Créez un utilisateur dédié** avec droits limités pour Home Assistant
3. **Activez l'authentification à deux facteurs** sur Home Assistant
4. **Gardez le firmware du parlophone à jour**
5. **Utilisez un VPN** si vous accédez à Home Assistant à distance
6. **Sauvegardez régulièrement** vos snapshots et configurations

## Troubleshooting avancé

### Redémarrage automatique en cas de problème

```yaml
automation:
  - id: '2n_watchdog'
    alias: "Surveillance parlophone"
    trigger:
      - platform: state
        entity_id: sensor.2n_uptime
        to: 'unavailable'
        for:
          minutes: 5
    action:
      - service: notify.admin
        data:
          message: "Parlophone non disponible, tentative de redémarrage"
      - service: button.press
        target:
          entity_id: button.2n_restart
```

### Debug logging

Ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.2n_intercom: debug
```
