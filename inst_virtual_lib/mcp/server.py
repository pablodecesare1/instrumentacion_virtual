"""
Servidor MCP para instrumental de laboratorio.
Expone herramientas para descubrir, configurar y medir con instrumentos
conectados por USB o red VXI-11.
"""

import asyncio
import traceback

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, TextContent, Tool

from inst_virtual_lib.mcp.instrument_registry import InstrumentRegistry

registry = InstrumentRegistry()

server = Server("instrumentacion")


# ---------------------------------------------------------------------------
# Herramienta 1: listar_dispositivos
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="listar_dispositivos",
            description=(
                "Descubre instrumentos conectados por USB (VISA) y "
                "opcionalmente por red (VXI-11). Si no se especifica subred, "
                "solo escanea USB."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "subred": {
                        "type": "string",
                        "description": (
                            "Subred a escanear en formato CIDR "
                            "(ej: 10.42.0.0/24). Solo escanea VISA si se omite."
                        ),
                    }
                },
            },
        ),
        Tool(
            name="acciones_disponibles",
            description=(
                "Lista las acciones/metodos disponibles para uno o todos los "
                "tipos de instrumento. Sirve para que el agente sepa que "
                "operaciones puede realizar."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tipo_dispositivo": {
                        "type": "string",
                        "description": (
                            'Filtrar por tipo: "osciloscopio", "generador", '
                            '"analizador". Si se omite, muestra todos.'
                        ),
                    }
                },
            },
        ),
        Tool(
            name="operadores_disponibles",
            description=(
                "Lista los operadores de medicion disponibles y sus metodos. "
                "Los operadores permiten realizar mediciones de alto nivel "
                "(Vrms, THD, RC) sobre los instrumentos."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="accion_instrumento",
            description=(
                "Ejecuta una accion sobre un instrumento. Antes de llamar a "
                "esta herramienta, use acciones_disponibles para conocer que "
                "acciones y parametros acepta cada tipo de instrumento. "
                "Para get_trace con muchos puntos, devuelve una referencia a "
                "archivo temporal .npy."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dispositivo_id": {
                        "type": "string",
                        "description": ("ID del dispositivo obtenido de listar_dispositivos"),
                    },
                    "accion": {
                        "type": "string",
                        "description": (
                            "Nombre del metodo a ejecutar (ej: get_trace, set_chan_div, senoidal)"
                        ),
                    },
                    "parametros": {
                        "type": "object",
                        "description": ("Parametros de la accion como clave:valor"),
                    },
                },
                "required": ["dispositivo_id", "accion"],
            },
        ),
        Tool(
            name="ejecutar_operador",
            description=(
                "Inicializa y ejecuta un operador de medicion sobre un "
                "instrumento. Use operadores_disponibles para conocer metodos "
                "y parametros."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dispositivo_id": {
                        "type": "string",
                        "description": "ID del dispositivo",
                    },
                    "tipo_operador": {
                        "type": "string",
                        "description": ('Tipo de operador: "osciloscopio" o "generador"'),
                    },
                    "metodo": {
                        "type": "string",
                        "description": (
                            "Metodo del operador (ej: medir_vrms, medir_thd, medir_rc)"
                        ),
                    },
                    "parametros": {
                        "type": "object",
                        "description": "Parametros del metodo como clave:valor",
                    },
                },
                "required": ["dispositivo_id", "tipo_operador", "metodo"],
            },
        ),
        Tool(
            name="comando_visa",
            description=(
                "Envia un comando VISA crudo a un instrumento. "
                "Usar es_query=true (default) si se espera respuesta."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dispositivo_id": {
                        "type": "string",
                        "description": "ID del dispositivo",
                    },
                    "comando": {
                        "type": "string",
                        "description": "Comando SCPI/VISA a enviar",
                    },
                    "es_query": {
                        "type": "boolean",
                        "description": (
                            "Si es true (default), espera respuesta del "
                            "instrumento. Si es false, solo escribe."
                        ),
                    },
                },
                "required": ["dispositivo_id", "comando"],
            },
        ),
    ]


def _clean_device_for_response(dev: dict) -> dict:
    """Limpia campos internos antes de devolver al cliente."""
    return {k: v for k, v in dev.items() if k != "vxi11_handle"}


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | EmbeddedResource]:
    try:
        if name == "listar_dispositivos":
            subnet = arguments.get("subred")
            devices = registry.list_devices(subnet=subnet)
            cleaned = [_clean_device_for_response(d) for d in devices]
            return [TextContent(type="text", text=str(cleaned))]

        elif name == "acciones_disponibles":
            tipo = arguments.get("tipo_dispositivo")
            actions = registry.get_available_actions(device_type=tipo)
            return [TextContent(type="text", text=str(actions))]

        elif name == "operadores_disponibles":
            operators = registry.get_available_operators()
            return [TextContent(type="text", text=str(operators))]

        elif name == "accion_instrumento":
            device_id = arguments["dispositivo_id"]
            action = arguments["accion"]
            params = arguments.get("parametros", {})
            result = registry.execute_action(device_id, action, params)
            return [TextContent(type="text", text=str(result))]

        elif name == "ejecutar_operador":
            device_id = arguments["dispositivo_id"]
            op_type = arguments["tipo_operador"]
            method = arguments["metodo"]
            params = arguments.get("parametros", {})
            result = registry.execute_operator(device_id, op_type, method, params)
            return [TextContent(type="text", text=str(result))]

        elif name == "comando_visa":
            device_id = arguments["dispositivo_id"]
            command = arguments["comando"]
            is_query = arguments.get("es_query", True)
            result = registry.send_visa(device_id, command, is_query=is_query)
            return [TextContent(type="text", text=str(result))]

        else:
            raise ValueError(f"Herramienta desconocida: {name}")

    except Exception as e:
        tb = traceback.format_exc()
        return [
            TextContent(
                type="text",
                text=f"Error: {e}\n{tb}",
            )
        ]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
