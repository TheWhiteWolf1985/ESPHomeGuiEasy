@page sensors Sensors Configuration

@brief JSON configuration file defining all available sensors for the visual editor.

This file defines the sensors that can be added via the block canvas in ESPHomeGUIeasy.
Each sensor entry describes the type, parameters, and required fields needed to
generate valid YAML blocks from the GUI.

---

## 📄 JSON Format

```json
{
  "sensors": [
    {
      "name": "DHT22 Temperature & Humidity",
      "platform": "dht",
      "parameters": [
        { "key": "pin", "type": "text", "label": "GPIO Pin", "default": "D1" },
        { "key": "model", "type": "combo", "label": "Sensor Model", "options": ["DHT11", "DHT22", "AM2302"], "default": "DHT22" }
      ]
    }
  ]
}
```

---

## 📌 Required Fields

| Field       | Type    | Description                                            |
|-------------|---------|--------------------------------------------------------|
| name        | string  | Sensor name shown in the UI                           |
| platform    | string  | ESPHome platform name used in YAML                    |
| parameters  | list    | Array of editable fields shown in the block UI        |

---

## 🔧 Parameter Format

Each item in the `parameters` array must contain:

- `key`: name of the YAML field
- `type`: widget type ("text", "combo", "int", "float", "bool")
- `label`: field label in the block UI
- `default`: default value (optional)
- `options`: array (for combo only)

---

## 🧠 Notes

- Each sensor becomes a draggable block on the canvas.
- Blocks are validated before YAML generation.