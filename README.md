# instrumentacion_virtual

Este repositorio contiene las clases que implementan el VISA para la automatización de diversos instrumentos de medición. Actualmente en construcción...


# Instrucciones para la instalación en Ubuntu 18.04

1. Instalar pyvisa-py:

```sh
sudo apt update
```
```sh
sudo apt install python-pyvisa-py
```
2. Instalar dependencias de python:
```sh
pip3 install -r requirements.txt
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
sudo usermod -a -G usbusers NOMBREUSUARIO
```

4. Reiniciar el equipo
