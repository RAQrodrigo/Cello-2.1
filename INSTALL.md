# Guía de Instalación — Cello v2.1 Core

Instrucciones para poner en marcha **Cello v2.1 Core** desde el código fuente, tanto en **Ubuntu** como en **Windows**.  
El proyecto tiene dos modos de uso:
- **CLI** (`run.py`): interfaz de línea de comandos.
- **Web App** (`webapp/app.py`): interfaz web local servida con Flask.

---

## Requisitos generales

| Dependencia | Versión mínima | Notas |
|---|---|---|
| Python | 3.11 | Recomendado 3.11.x |
| Java (JDK/JRE) | 11 | Necesario para el gateway Py4J |
| Yosys | cualquiera reciente | Síntesis lógica de Verilog |
| Graphviz | cualquiera reciente | Generación de gráficos (`dot`) |
| pip | — | Incluido con Python |
| git | — | Para clonar el repositorio |

---

## Instalación en Ubuntu

### 1. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git
sudo apt install -y default-jdk          # Java 11 o superior
sudo apt install -y yosys graphviz
```

Verificar instalaciones:
```bash
python3.11 --version
java -version
yosys --version
dot -V
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/CIDARLAB/Cello-v2-1-Core-main.git
cd Cello-v2-1-Core-main
```

> Si ya tenés la carpeta descargada, simplemente `cd` al directorio raíz del proyecto.

### 3. Crear y activar un entorno virtual

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias de Python del core

```bash
pip install -r requirements.txt
```

### 5. Instalar dependencias de la web app

```bash
pip install -r webapp/requirements.txt
```

### 6. Ejecutar

**Modo CLI:**
```bash
python run.py
```

**Modo Web App:**
```bash
cd webapp
python app.py
```
Luego abrí el navegador en: `http://localhost:5000`

---

## Instalación en Windows

### 1. Instalar Python 3.11

Descargá el instalador desde [python.org](https://www.python.org/downloads/).  
Durante la instalación, marcá la opción **"Add Python to PATH"**.

Verificar:
```powershell
python --version
```

### 2. Instalar Java 11

Descargá el JDK 11 desde [Adoptium / Eclipse Temurin](https://adoptium.net/temurin/releases/?version=11).  
El instalador agrega Java al PATH automáticamente.

Verificar:
```powershell
java -version
```

### 3. Instalar Graphviz

Descargá el instalador `.exe` desde [graphviz.org/download](https://www.graphviz.org/download/).

Luego agregá la carpeta `bin` de Graphviz al `PATH` del sistema:
1. Buscá **"Editar las variables de entorno del sistema"** en el menú inicio.
2. Click en **Variables de entorno → Path → Editar → Nuevo**.
3. Agregá: `C:\Program Files\Graphviz\bin`

Verificar:
```powershell
dot -V
```

### 4. Instalar Yosys (OSS CAD Suite)

Descargá el paquete **oss-cad-suite** para Windows desde:  
[https://github.com/YosysHQ/oss-cad-suite-build/releases](https://github.com/YosysHQ/oss-cad-suite-build/releases)

Extraé el contenido y movelo a, por ejemplo, `C:\oss-cad-suite`.

**Nota:** Yosys **no** se agrega al PATH de forma permanente con este método.  
Antes de cada sesión de trabajo, ejecutá el entorno desde PowerShell:
```powershell
C:\oss-cad-suite\start.bat
```
Luego continuá en esa misma ventana de PowerShell.

Alternativamente, si tenés **MSYS2** instalado (`C:\msys64`), Yosys ya debería estar en:
```
C:\msys64\mingw64\bin
```
En ese caso, agregá esa ruta al PATH del sistema de la misma forma que hiciste con Graphviz.

### 5. Clonar el repositorio

```powershell
git clone https://github.com/CIDARLAB/Cello-v2-1-Core-main.git
cd Cello-v2-1-Core-main
```

### 6. Crear y activar un entorno virtual

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la ejecución de scripts, ejecutá primero:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 7. Instalar dependencias de Python del core

```powershell
pip install -r requirements.txt
```

### 8. Instalar dependencias de la web app

```powershell
pip install -r webapp\requirements.txt
```

### 9. Ejecutar

**Modo CLI:**
```powershell
python run.py
```

**Modo Web App:**
```powershell
cd webapp
python app.py
```
Luego abrí el navegador en: `http://localhost:5000`

---

## Estructura de carpetas relevante

```
Cello-v2-1-Core-main/
├── run.py                  # Punto de entrada CLI
├── requirements.txt        # Dependencias del core
├── config.py               # Rutas de directorios
├── core_algorithm/         # Algoritmo principal
├── library/
│   ├── constraints/        # Archivos UCF (.UCF.json, .input, .output)
│   └── verilogs/           # Archivos Verilog de diseño (.v)
├── output/                 # Resultados generados
├── webapp/
│   ├── app.py              # Servidor Flask (web app)
│   ├── requirements.txt    # Dependencias Flask
│   └── static/             # Frontend HTML/JS/CSS
└── bin/                    # Utilidades de conversión CSV/UCF
```

---

## Resumen de dependencias Python

### `requirements.txt` (core)

| Paquete | Versión |
|---|---|
| matplotlib | ~3.7.2 |
| numpy | ~1.26.4 |
| scipy | ~1.12 |
| Pillow | 10.3.0 |
| dnaplotlib | 1.0 |
| sbol3 | ~1.1 |
| py4j | 0.10.9.7 |
| memory-profiler | ~0.61.0 |
| pytest | ~7.4.4 |

### `webapp/requirements.txt`

| Paquete | Notas |
|---|---|
| flask | Servidor web |
| flask-cors | Soporte CORS |

---

## Solución de problemas frecuentes

| Problema | Causa probable | Solución |
|---|---|---|
| `yosys: command not found` | Yosys no está en el PATH | Ejecutá `oss-cad-suite\start.bat` (Windows) o verificá la instalación (Ubuntu) |
| `dot: command not found` | Graphviz no está en el PATH | Agregá `C:\Program Files\Graphviz\bin` al PATH |
| `Failed to start Java Py4J gateway` | Java no instalado o no en PATH | Instalá JDK 11 y verificá con `java -version` |
| Error de imports de Python | Entorno virtual no activado | Activá el `venv` antes de correr cualquier script |
| Error de codificación UTF-8 (Windows) | Encoding de la consola | La webapp ya configura `PYTHONIOENCODING=utf-8` automáticamente |
