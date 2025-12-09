# Utilisation des services 2N Intercom

## Services disponibles

L'intégration 2N Intercom fournit 3 services personnalisés :

### 1. `twon_intercom.dial` - Composer un numéro

Permet d'initier un appel depuis le parlophone vers un numéro.

**Paramètres :**
- `number` (requis) : Le numéro à composer

**Exemple dans une automatisation :**
```yaml
action:
  - service: twon_intercom.dial
    data:
      number: "101"
```

**Exemple dans Outils de développement → Services :**
```yaml
service: twon_intercom.dial
data:
  number: "101"
```

### 2. `twon_intercom.display_text` - Afficher du texte

Affiche du texte sur l'écran du parlophone (pour les modèles avec écran).

**Paramètres :**
- `text` (requis) : Le texte à afficher
- `x` (optionnel) : Position horizontale (en pixels)
- `y` (optionnel) : Position verticale (en pixels)
- `size` (optionnel) : Taille de la police (8-72)
- `color` (optionnel) : Couleur en hexadécimal (ex: "#FFFFFF")

**Exemple simple :**
```yaml
action:
  - service: twon_intercom.display_text
    data:
      text: "Bienvenue !"
```

**Exemple avec personnalisation :**
```yaml
action:
  - service: twon_intercom.display_text
    data:
      text: "LIVRAISON\nDéposer le colis"
      x: 50
      y: 100
      size: 25
      color: "#FF8800"
```

**Exemple multi-lignes :**
```yaml
action:
  - service: twon_intercom.display_text
    data:
      text: |
        Bienvenue
        Veuillez patienter
        Quelqu'un arrive
```

### 3. `twon_intercom.trigger_switch` - Déclencher un switch

Active temporairement un switch (pulse/impulsion). Utile pour ouvrir une porte sans maintenir le switch activé.

**Paramètres :**
- `switch_num` (requis) : Le numéro du switch (1, 2, etc.)

**Exemple :**
```yaml
action:
  - service: twon_intercom.trigger_switch
    data:
      switch_num: 1
```

## Exemples d'automatisations complètes

### Message de bienvenue personnalisé

```yaml
automation:
  - alias: "Message personnalisé selon l'heure"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: 'on'
    action:
      - choose:
          # Matin
          - conditions:
              - condition: time
                after: '06:00:00'
                before: '12:00:00'
            sequence:
              - service: twon_intercom.display_text
                data:
                  text: "Bonjour !"
                  size: 30
                  color: "#FFD700"
          
          # Après-midi
          - conditions:
              - condition: time
                after: '12:00:00'
                before: '18:00:00'
            sequence:
              - service: twon_intercom.display_text
                data:
                  text: "Bon après-midi"
                  size: 30
                  color: "#00BFFF"
          
          # Soir
          - conditions:
              - condition: time
                after: '18:00:00'
                before: '23:59:59'
            sequence:
              - service: twon_intercom.display_text
                data:
                  text: "Bonsoir"
                  size: 30
                  color: "#9370DB"
```

### Appel automatique à un numéro en cas d'urgence

```yaml
automation:
  - alias: "Appel d'urgence"
    trigger:
      - platform: state
        entity_id: binary_sensor.alarme_incendie
        to: 'on'
    action:
      - service: twon_intercom.dial
        data:
          number: "112"  # Numéro d'urgence
      - service: twon_intercom.display_text
        data:
          text: "ALERTE INCENDIE\nAppel en cours..."
          size: 25
          color: "#FF0000"
```

### Ouverture rapide avec impulsion

```yaml
automation:
  - alias: "Ouverture porte avec impulsion"
    trigger:
      - platform: state
        entity_id: input_boolean.ouvrir_porte
        to: 'on'
    action:
      - service: twon_intercom.trigger_switch
        data:
          switch_num: 1
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.ouvrir_porte
```

### Script de livraison

```yaml
script:
  mode_livraison:
    alias: "Mode livraison"
    sequence:
      # Afficher le message
      - service: twon_intercom.display_text
        data:
          text: "LIVRAISON\nDéposer le colis\nMerci !"
          size: 22
          color: "#FF8800"
      
      # Ouvrir la porte
      - service: twon_intercom.trigger_switch
        data:
          switch_num: 1
      
      # Attendre
      - delay:
          seconds: 30
      
      # Message de remerciement
      - service: twon_intercom.display_text
        data:
          text: "Merci !\nBonne journée"
          size: 25
          color: "#00FF00"
      
      # Effacer après 5 secondes
      - delay:
          seconds: 5
      - service: twon_intercom.display_text
        data:
          text: ""
```

### Notification visuelle pour les visiteurs

```yaml
automation:
  - alias: "Informer visiteur - personne absente"
    trigger:
      - platform: state
        entity_id: binary_sensor.2n_call_active
        to: 'on'
    condition:
      - condition: state
        entity_id: person.proprietaire
        state: 'not_home'
    action:
      - service: twon_intercom.display_text
        data:
          text: |
            Personne absente
            Merci de laisser
            un message
          size: 20
          color: "#FFA500"
```

## Utilisation dans des scripts Lovelace

### Bouton pour ouvrir la porte

```yaml
type: button
name: Ouvrir la porte
icon: mdi:door-open
tap_action:
  action: call-service
  service: twon_intercom.trigger_switch
  service_data:
    switch_num: 1
```

### Bouton pour appeler l'appartement

```yaml
type: button
name: Appeler Apt 101
icon: mdi:phone
tap_action:
  action: call-service
  service: twon_intercom.dial
  service_data:
    number: "101"
```

### Input text pour message personnalisé

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: input_text.message_parlophone
  - type: button
    name: Afficher le message
    icon: mdi:message-text
    tap_action:
      action: call-service
      service: twon_intercom.display_text
      service_data:
        text: "{{ states('input_text.message_parlophone') }}"
        size: 25
```

## Conseils d'utilisation

1. **Effacer l'écran** : Pour effacer le texte affiché, envoyez un texte vide :
   ```yaml
   service: twon_intercom.display_text
   data:
     text: ""
   ```

2. **Sauts de ligne** : Utilisez `\n` ou le format multi-lignes YAML avec `|`

3. **Couleurs** : Utilisez le format hexadécimal avec # (ex: #FF0000 pour rouge)

4. **Test rapide** : Utilisez Outils de développement → Services pour tester

5. **Trigger vs Switch** : Utilisez `trigger_switch` pour une impulsion, `switch.turn_on` pour maintenir activé
