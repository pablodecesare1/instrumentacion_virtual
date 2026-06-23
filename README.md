# instrumentacion_virtual

Este repositorio contiene las clases que implementan el VISA para la automatización de diversos instrumentos de medición. Actualmente en construcción...


# Instrucciones para la instalación en Ubuntu 

1. Instalar NI-visa y pyvisa:

```sh
sudo apt update
```


https://www.ni.com/es/support/downloads/drivers/download.ni-visa.html#565016

Descomprimir la carpeta e instalar los drivers (ubuntu 24.04):

```sh
sudo dpkg -i ni-ubuntu2404-drivers-2025Q2.deb
sudo dpkg -i ni-ubuntu2404-drivers-stream.deb
```


Ubuntu 24.04:
```sh
sudo apt install python3-pyvisa-py
```

2. Instalar entorno con uv:

Instalar uv:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Instalar dependencias (incluyendo las de desarrollo):
```sh
uv sync
```

Activar el entorno virtual:
```sh
source .venv/bin/activate
```

3. Dar acceso al usb al usuario de python:
```sh
sudo nano  /etc/udev/rules.d/99-com.rules
```
--- Agregar la siguiente linea:
```sh
SUBSYSTEM=="usb", MODE="0666", GROUP="usbusers"
```
Crear el grupo y agregar al usuario
```sh
sudo groupadd usbusers
```
```sh
sudo usermod -a -G usbusers $USER
```

4. Reiniciar el equipo


# Uso con OpenCode

Este repositorio incluye un servidor MCP en `inst_virtual_lib/mcp/` y un
agente de [opencode](https://github.com/anomalyco/opencode) (`instrumentacion`) para controlar instrumentos desde
el chat de opencode. El agente aparece automáticamente en el selector al
abrir opencode desde este directorio.

El MCP expone 6 herramientas: `listar_dispositivos`, `acciones_disponibles`,
`operadores_disponibles`, `accion_instrumento`, `ejecutar_operador` y
`comando_visa`. La subred VXI-11 se pasa como parámetro opcional a
`listar_dispositivos`, no hay configuración fija.