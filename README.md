# 🪐 Martes Mini - Mascota de Escritorio Inteligente (Desktop Pet AI)

¡Compañero de escritorio en Pixel Art 100% local, ligero (<25 MB RAM), interactivo y sin necesidad de instalación!

![Icono de Martes](assets/app_icon.png)

---

## ✨ Características Principales

- **🎮 100% Plug-and-Play**: Descarga `Martes.exe` y ábrelo directamente. No requiere instalar Python, librerías ni configuraciones complicadas.
- **🔄 Auto-Actualizaciones Integradas**: Martes verifica automáticamente si hay nuevas versiones publicadas en este repositorio de GitHub y se actualiza con un solo clic.
- **🤸 Acrobacias & Salto Mortal**: ¡Martes sabe hacer un **Backflip (Mortal 360°)** con físicas parabólicas fluidas! Haz doble clic en él o pídeselo en el chat.
- **🎨 3 Paletas de Color Clásicas**:
  - 🪐 **Marte Ámbar (Terracota)**
  - 🟩 **Verde Clásico (Retro Game Boy)**
  - ✨ **Cyberpunk (Oro & Oliva)**
- **👀 Estados de Vida Autónomos**:
  - **Seguimiento del cursor**: Martes orienta su mirada (arriba, abajo, izquierda, derecha, centro) hacia donde mueves el ratón.
  - **Parpadeo natural**: Frecuencia y duración orgánica.
  - **Modo Siesta**: Si estás inactivo, cerrará sus ojos (`v v`) y comenzará a flotar con letreros `Zzz`.
  - **Alerta / Sorpresa (`!`)**: Con el atajo global `Ctrl + Alt + M` se teletransporta directo a donde tengas el ratón.
  - **Paseo libre**: Camina aleatoriamente explorando tu pantalla.
- **🧠 Inteligencia Artificial**:
  - **Modo Autónomo Offline**: Cuenta con su propio motor de personalidad para chistes, conversación y control de estados sin conexión.
  - **Conexión Opcional con Ollama**: Si ejecutas Ollama en tu PC con el modelo `mart-es`, Martes responderá cualquier pregunta técnica o de programación con IA generativa.

---

## 🚀 Cómo Empezar

### Opción 1: Ejecutable Portable (Recomendado)
1. Ve a la sección de **[Releases](https://github.com/kenzeta-cyber/mart-es-portable/releases)**.
2. Descarga `Martes.exe` o `Martes-Mini-Portable.zip`.
3. Haz doble clic en `Martes.exe`... ¡y listo!

### Opción 2: Desde el Código Fuente (Python)
Requisitos: Python 3.10 o superior (solo requiere Tkinter, incluido por defecto en Python en Windows).
```bash
python mini_martes.py
```

---

## 🎮 Controles

| Acción | Control |
|---|---|
| **Mover a Martes** | Clic izquierdo y arrastrar |
| **Hablar con él** | Clic izquierdo |
| **Salto Mortal 360° (Backflip)** | Doble clic izquierdo |
| **Menú contextual** | Clic derecho sobre Martes |
| **Teletransportar al ratón** | `Ctrl` + `Alt` + `M` |

---

## 📦 Estructura del Proyecto

```text
├── assets/                  # Sprites pixel art de todas las paletas e icono oficial
│   ├── app_icon.png
│   ├── martes.ico
│   ├── verde_*.png
│   ├── marte_*.png
│   └── cyber_*.png
├── mini_martes.py           # Código fuente de Martes Mini con motor de estados
├── version.json             # Manifiesto de versiones para el auto-updater
├── Iniciar_Martes.bat       # Lanzador alternativo por consola/script
├── LEEME.txt                # Instrucciones para el usuario final
└── README.md                # Esta guía del repositorio
```

---

## 📄 Licencia
Proyecto desarrollado con ❤️ para la comunidad de desarrolladores y amantes del Pixel Art.
