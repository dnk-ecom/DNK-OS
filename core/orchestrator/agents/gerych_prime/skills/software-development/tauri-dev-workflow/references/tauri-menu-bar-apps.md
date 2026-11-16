---
name: tauri-menu-bar-apps
description: Special considerations for menu-bar/tray-only Tauri apps
license: Apache-2.0
---

# Tauri Menu-Bar / Tray-Only Apps

## When to Use

- "tauri menu bar", "tauri tray app", "tauri system tray", "tauri no window"

## Key Characteristics

- **No main window** on startup — app lives in system tray / menu bar
- **macOS**: Appears in top-right menu bar (near clock)
- **Windows**: System tray (bottom-right, may need "Show hidden icons")
- **Linux**: System tray / indicator (depends on DE)

## Configuration (tauri.conf.json)

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist"
  },
  "tauri": {
    "allowlist": {
      "tray": {
        "all": true
      }
    },
    "windows": [],
    "systemTray": {
      "iconPath": "icons/tray-icon.png",
      "iconAsTemplate": true,
      "menu": {
        "items": [
          { "id": "show", "text": "Show App" },
          { "id": "quit", "text": "Quit" }
        ]
      }
    }
  }
}
```

## Rust Backend (src-tauri/src/main.rs)

```rust
use tauri::{Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, CustomMenuItem};

fn main() {
    let tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show".to_string(), "Show"))
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit".to_string(), "Quit"));

    let tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "show" => {
                        // Show window or panel
                    }
                    "quit" => {
                        std::process::exit(0);
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error running tauri app");
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Icon not visible | Check `iconAsTemplate: true` for macOS template images |
| Menu doesn't appear | Verify `allowlist.tray.all: true` in tauri.conf.json |
| App quits immediately | Ensure no windows are created; tray keeps app alive |
| Multiple icons | Prevent multiple `SystemTray` instances |
| Icon size | Use 16x16 or 32x32 PNG; macOS prefers template PDF |

## Debugging Menu-Bar Apps

```bash
# Dev mode still works
npm run tauri dev

# Logs appear in terminal
# Right-click tray icon → "Inspect Element" (if enabled)
# Or: Cmd+Option+I when menu is open
```

## References

- https://v2.tauri.app/learn/system-tray/
- https://v2.tauri.app/api/js/tray/