# 🐦 Flappy Bird - Control Facial

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.13-green)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-red)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-orange)

## 📖 Descripción

**Flappy Bird - Control Facial** es una versión del clásico juego Flappy Bird que utiliza **reconocimiento facial** para controlar a Flappy. Mueve tu nariz hacia arriba o abajo para esquivar los tubos y conseguir la puntuación más alta.

El juego cuenta con:
- 🎮 **Control por movimiento de nariz** (detección facial en tiempo real)
- 📈 **Dificultad progresiva** (aumenta automáticamente con tu puntaje)
- 🏆 **Sistema de récords** (guarda tu mejor puntuación)
- 🎨 **Interfaz clisica 2D** con efectos visuales y animaciones
- 📷 **Modo debug** para probar el reconocimiento facial
- ⚡ **Velocidad extrema** en niveles altos

## ✨ Características

- **Control intuitivo**: Solo mueve tu nariz arriba/abajo
- **Dificultad dinámica y rápida**: 
  - Velocidad inicial: -10 (rápido)
  - Velocidad máxima: -14 (extremadamente rápido)
  - Gap entre tubos: 220 → 180
  - Distancia entre tubos: 400 → 280
- **Sistema de puntuación**: 1 punto por tubo superado
- **Guardado automático**: Tu récord se guarda localmente
- **Modo debug independiente**: Prueba la cámara sin jugar
- **Compatibilidad**: Funciona con Python 3.13

## 🎮 Controles

| Tecla | Acción |
|-------|--------|
| **Movimiento de nariz** | Controla la altura del pájaro |
| **R** | Reiniciar juego (cuando pierdes) |
| **ESC** | Salir del juego |

## 🖥️ Requisitos del Sistema

### Hardware
- Cámara web (integrada o externa)
- Procesador: 1.5 GHz o superior
- RAM: 2 GB mínimo
- Resolución de pantalla recomendada: 1024x600 o superior

### Software
- **Python 3.13** (o superior)
- Bibliotecas requeridas:
  - `pygame` 2.6.1
  - `opencv-python` 4.x
  - `numpy` 1.x

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/flappy-bird-facial.git
cd flappy-bird-facial
```

### 2. Instalar dependencias
```bash
pip install pygame opencv-python numpy
```

### 3. Ejecutar el juego
```bash
python main.py
```

## 🚀 Cómo Jugar
1. Colócate frente a la cámara a unos 50-80 cm de distancia
2. Asegúrate de tener buena iluminación
3. Mueve tu nariz hacia arriba o abajo para controlar la altura del pájaro
4. Esquiva los tubos verdes para sumar puntos
5. Cada tubo superado = 1 punto

-La dificultad aumenta automáticamente con tu puntaje

## 🐛 Modo Debug
Si quieres probar el reconocimiento facial sin jugar:
```bash
python camera_debug.py
```

Esto abrirá una ventana con:
- Detección de rostro (rectángulo verde)
- Seguimiento de nariz (círculo rojo)
- Indicadores de apertura de boca e inclinación de cabeza
- Información en tiempo real

## 🎯 Configuración de Dificultad Actual
Tu juego tiene una dificultad MUY RÁPIDA:

```python
DIFFICULTY_CONFIG = {
    0: {'gap': 220, 'velocity': -10, 'spawn_distance': 400},  # Base muy rápida
    5: {'gap': 210, 'velocity': -11, 'spawn_distance': 350},  # Aumenta velocidad
    10: {'gap': 200, 'velocity': -12, 'spawn_distance': 300}, # Experto
    15: {'gap': 190, 'velocity': -13, 'spawn_distance': 290}, # Profesional
    20: {'gap': 180, 'velocity': -14, 'spawn_distance': 280}, # Legendario
}
```

Comparativa de dificultad:
Nivel	Velocidad	Diferencia
Fácil (original)	-4	Referencia
Tu juego base	-10	2.5x más rápido
Tu juego máximo	-14	3.5x más rápido

## 🔧 Solución de Problemas
La cámara no se detecta
```bash
# Verificar permisos de cámara en Windows:
# Configuración > Privacidad > Cámara > Permitir aplicaciones

# Probar diferentes índices de cámara
python camera_debug.py
```

- Asegúrate de tener buena iluminación
- Tu configuración de velocidad es muy alta, considera reducir si es necesario
- No detecta mi rostro:
      - Acércate más a la cámara (50-80 cm)
      - Mejora la iluminación
      - Mira directamente a la cámara

Prueba el modo debug: python camera_debug.py

El juego es demasiado rápido
Si la velocidad es muy alta para ti, puedes modificarla en server/game_logic.py:

python
# Reduce las velocidades
```bash
DIFFICULTY_CONFIG = {
    0: {'gap': 220, 'velocity': -6, 'spawn_distance': 400},   # Más lento
    5: {'gap': 210, 'velocity': -7, 'spawn_distance': 350},
    # ... etc
}
```

Error de importación
```bash
# Reinstalar dependencias
pip uninstall opencv-python pygame numpy
pip install opencv-python pygame numpy
```

## 🎨 Personalización
Cambiar resolución
Edita client/renderer.py:
```
python
def __init__(self, width=1024, height=600):  # Cambia estos valores
Ajustar sensibilidad del control
Edita main.py:
```
python
sensitivity = 0.85  # 0.1 (suave) a 1.0 (rápido)
Modificar dificultad (valores actuales)
Edita server/game_logic.py:
```
python
DIFFICULTY_CONFIG = {
    0: {'gap': 220, 'velocity': -10, 'spawn_distance': 400},  # Ajusta según prefieras
    5: {'gap': 210, 'velocity': -11, 'spawn_distance': 350},
    # Modifica estos valores
}
```
Hacer el juego más lento (recomendado para principiantes)
```python
DIFFICULTY_CONFIG = {
    0: {'gap': 240, 'velocity': -5, 'spawn_distance': 450},
    5: {'gap': 230, 'velocity': -6, 'spawn_distance': 420},
    10: {'gap': 220, 'velocity': -7, 'spawn_distance': 390},
    15: {'gap': 210, 'velocity': -8, 'spawn_distance': 360},
    20: {'gap': 200, 'velocity': -9, 'spawn_distance': 330},
}
```

## 📊 Rendimiento
- FPS: 60 (estables)
- Latencia de control: ~50-100ms
- Uso de CPU: ~15-25%
- Uso de RAM: ~150-200 MB

⚠️ Nota sobre la dificultad
Este juego está configurado con velocidades extremadamente rápidas (hasta -14). Si eres principiante o encuentras el juego muy difícil, te recomendamos reducir las velocidades en server/game_logic.py a valores entre -5 y -8.

## 🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:
```
Fork el proyecto
Crea tu rama (git checkout -b feature/AmazingFeature)
Commit tus cambios (git commit -m 'Add AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)
Abre un Pull Request
```

## 📝 Licencia
Este proyecto está bajo Licencia. Ver el archivo LICENSE para más detalles.

## 🙏 Agradecimientos
- Pygame - Framework de juegos
- OpenCV - Visión por computadora
- Inspirado en el clásico juego Flappy Bird

## 📧 Contacto
- Autor: MeDuza
- Email: mariamelinaduarte@gmail,com
- GitHub: @xxMeDuzaa
