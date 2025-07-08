@page modules_schema Modules Schema

@brief JSON schema used to define the editable modules in the 'Modules' tab of ESPHomeGUIeasy.

This file provides a generic schema-based configuration system that dynamically builds
the accordion layout for editable modules (like `wifi`, `logger`, `ota`, etc.)

---

## 📄 JSON Format

```json
{
  "wifi": {
    "title": "Wi-Fi",
    "fields": [
      { "key": "ssid", "type": "text", "label": "Network SSID", "default": "" },
      { "key": "password", "type": "text", "label": "Password", "default": "" }
    ]
  }
}
```

---

## 📌 Field Types

| Field     | Type   | Description                                         |
|-----------|--------|-----------------------------------------------------|
| title     | string | Title shown in the GUI section header               |
| fields    | list   | List of editable fields within the section          |

Each field in `fields` must include:
- `key`: key to use in YAML
- `type`: field type (`text`, `int`, `bool`, `combo`)
- `label`: visible label in GUI
- `default`: default value
- `options`: only for `combo`

---

## ➕ Adding a new module

To define a new module section:
1. Add a new object to the root level using a unique key (e.g., `"mqtt"`).
2. Provide a `title` and `fields` array.
3. Example:

```json
{
  "mqtt": {
    "title": "MQTT",
    "fields": [
      { "key": "broker", "type": "text", "label": "MQTT Broker Address", "default": "192.168.1.10" }
    ]
  }
}
```

---

## 🧠 Notes

- This schema powers the accordion-based form UI in the Modules tab.
- Only modules defined here will be shown/editable in the interface.