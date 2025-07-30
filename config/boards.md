@page boards Supported Boards

@brief JSON configuration file containing the list of supported development boards.

This file is used by the ESPHomeGUIeasy project to populate the **board selector**
during the creation of a new project.

Each entry in the file provides a human-readable label (shown in the GUI) and
the internal identifier (`board:`) used by ESPHome in the YAML configuration.

---

## 📄 JSON Format

```json
{
  "boards": [
    {
      "label": "Seeed Studio XIAO ESP32-C3",
      "value": "seeed_xiao_esp32c3"
    },
    {
      "label": "ESP32 DevKit v1",
      "value": "esp32dev"
    },
    {
      "label": "NodeMCU v3 (ESP8266)",
      "value": "nodemcuv2"
    }
  ]
}
```

---

## 📌 Required Fields

| Field   | Type   | Description                                                      |
|---------|--------|------------------------------------------------------------------|
| label   | string | Name shown in the dropdown inside the GUI                       |
| value   | string | Internal name passed to the `board:` field in ESPHome YAML file |

---

## ➕ Adding New Boards

To add a new board to the selection list:

1. Open the `boards.json` file in a text editor.
2. Add a new object to the `"boards"` array following the format above.
3. Example:

```json
{
  "label": "Wemos D1 Mini",
  "value": "d1_mini"
}
```

4. Save the file and restart ESPHomeGUIeasy. The new board will appear in the dropdown.

---

## 🧠 Notes

- The values must match those officially supported by ESPHome (https://esphome.io/devices/)
- Boards can be grouped or filtered in future releases using optional fields such as `architecture`, `manufacturer`, or `featured`.