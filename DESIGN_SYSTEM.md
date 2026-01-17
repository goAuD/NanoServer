# Nano Design System

A reusable design system for lightweight "Nano" desktop applications using CustomTkinter.

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Success Green | `#4caf50` | Start buttons, positive status |
| Danger Red | `red` / `darkred` | Stop buttons, errors |
| Warning Orange | `#e67e22` / `#d35400` | Restart, caution actions |
| Neutral Gray | `#34495e` | Secondary buttons |
| Laravel Red | `#ff2d20` | Laravel detection |
| Error Red | `#e74c3c` | Error messages |

### Text Colors
| Name | Hex | Usage |
|------|-----|-------|
| Muted | `gray` | Subtitles, descriptions |
| Light Gray | `#aaaaaa` | Secondary text, paths |

## Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Title | Roboto | 24 | Bold |
| Section Header | Roboto | 16 | Bold |
| Subsection | Roboto | 14 | Bold |
| Log Text | Consolas | 11 | Normal |

## Layout Guidelines

### Window
```python
geometry = "700x780"
minsize = (600, 700)
resizable = True
```

### Spacing
- Section padding: `pady=10, padx=20`
- Element padding: `pady=5`
- Button padding: `padx=10`

### Button Sizes
- Primary actions: `width=140`
- Full-width buttons: use default (fills container)

## Components

### Section Frame
```python
frame = ctk.CTkFrame(parent)
frame.pack(pady=10, padx=20, fill="x")

label = ctk.CTkLabel(
    frame, 
    text="Section Title",
    font=("Roboto", 16, "bold")
)
label.pack(pady=8)
```

### Primary Button (Start/Positive)
```python
btn = ctk.CTkButton(
    parent,
    text="Start",
    fg_color="green",
    hover_color="darkgreen",
    width=140
)
```

### Danger Button (Stop/Negative)
```python
btn = ctk.CTkButton(
    parent,
    text="Stop",
    fg_color="red",
    hover_color="darkred",
    width=140
)
```

### Warning Button (Restart/Caution)
```python
btn = ctk.CTkButton(
    parent,
    text="Restart",
    fg_color="#e67e22",
    hover_color="#d35400",
    width=140
)
```

### Log Display
```python
textbox = ctk.CTkTextbox(
    parent,
    height=120,
    font=("Consolas", 11),
    state="disabled"
)
```

### Input Field with Enter Support
```python
entry = ctk.CTkEntry(
    parent,
    placeholder_text="Enter value...",
    width=500
)
entry.bind("<Return>", lambda e: on_submit())
```

## Appearance Mode

```python
import customtkinter as ctk
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
```

---

## Future Nano Products Ideas

- **NanoNotes** - Lightweight Markdown note-taking
- **NanoAPI** - Simple REST API testing tool
- **NanoSSH** - Basic SSH client
- **NanoGit** - Simple Git GUI
- **NanoTimer** - Pomodoro/productivity timer
