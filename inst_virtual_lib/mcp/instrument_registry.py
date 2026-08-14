"""
Registry de instrumentos: descubrimiento, conexion, cache y ejecucion de
acciones/operadores.
"""

import contextlib
import ipaddress
import socket
import tempfile
from typing import Any

import numpy as np
import pyvisa

from inst_virtual_lib.analizador_espectro import AnalizadorEspectro, RigolDsa800
from inst_virtual_lib.generadores_arbitrarios import (
    Agilent33512A,
    GeneradorArbitrario,
    RigolDG5071,
    Siglent1032X,
)
from inst_virtual_lib.instrument import Instrument
from inst_virtual_lib.operador import OperadorGenerador, OperadorOsciloscopio
from inst_virtual_lib.osciloscopios import (
    SDS2102,
    GwInstek,
    Mso3024A,
    Osciloscopio,
    Rigol,
    RigolDs2202,
    TektronixDsoDpoMsoTds,
)

# ---------------------------------------------------------------------------
# Mapping de patrones IDN -> (clase, categoria)
# ---------------------------------------------------------------------------

IDN_PATTERNS: list[tuple[callable, type[Instrument], str]] = [
    (
        lambda idn: (
            "MSO-X 3024A" in idn.upper() or ("MSO" in idn.upper() and "3024A" in idn.upper())
        ),
        Mso3024A,
        "osciloscopio",
    ),
    (
        lambda idn: "GW INSTEK" in idn.upper() or idn.upper().startswith("GW,"),
        GwInstek,
        "osciloscopio",
    ),
    (lambda idn: "TEKTRONIX" in idn.upper(), TektronixDsoDpoMsoTds, "osciloscopio"),
    (lambda idn: "SDS2102" in idn, SDS2102, "osciloscopio"),
    (lambda idn: "RIGOL" in idn.upper() and "DS2202" in idn.upper(), RigolDs2202, "osciloscopio"),
    (
        lambda idn: "RIGOL" in idn.upper() and any(x in idn.upper() for x in ("DS", "MSO")),
        Rigol,
        "osciloscopio",
    ),
    (
        lambda idn: "DG5071" in idn or ("RIGOL" in idn.upper() and "DG" in idn.upper()),
        RigolDG5071,
        "generador",
    ),
    (
        lambda idn: "33512A" in idn or ("AGILENT" in idn.upper() and "335" in idn),
        Agilent33512A,
        "generador",
    ),
    (
        lambda idn: "SDG1032X" in idn or ("SIGLENT" in idn.upper() and "SDG" in idn),
        Siglent1032X,
        "generador",
    ),
    (lambda idn: "DSA800" in idn or "DSA815" in idn, RigolDsa800, "analizador"),
]

# ---------------------------------------------------------------------------
# Metadatos de acciones disponibles por categoria
# ---------------------------------------------------------------------------

_OSC_METHODS: list[dict[str, Any]] = [
    {
        "nombre": "get_trace",
        "descripcion": "Adquiere el trazo de un canal",
        "parametros": [
            {
                "nombre": "canal",
                "tipo": "integer",
                "requerido": True,
                "descripcion": "Numero de canal",
            }
        ],
        "retorno": "array (tiempo, tension)",
    },
    {
        "nombre": "set_chan_div",
        "descripcion": "Configura voltios/division de un canal",
        "parametros": [
            {
                "nombre": "valor",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Voltios por division",
            },
            {
                "nombre": "canal",
                "tipo": "integer",
                "requerido": True,
                "descripcion": "Numero de canal",
            },
        ],
        "retorno": "void",
    },
    {
        "nombre": "get_chan_div",
        "descripcion": "Obtiene voltios/division de un canal",
        "parametros": [
            {
                "nombre": "canal",
                "tipo": "integer",
                "requerido": True,
                "descripcion": "Numero de canal",
            }
        ],
        "retorno": "string",
    },
    {
        "nombre": "set_bt",
        "descripcion": "Configura la base de tiempo",
        "parametros": [
            {
                "nombre": "tiempo_div",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Segundos por division",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "get_bt",
        "descripcion": "Obtiene la base de tiempo",
        "parametros": [],
        "retorno": "number",
    },
    {
        "nombre": "get_samplerate",
        "descripcion": "Obtiene la frecuencia de muestreo",
        "parametros": [],
        "retorno": "number",
    },
    {
        "nombre": "set_trigger_level",
        "descripcion": "Configura el nivel de disparo",
        "parametros": [
            {
                "nombre": "valor",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Nivel de trigger en volts",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "get_trigger_level",
        "descripcion": "Obtiene el nivel de disparo",
        "parametros": [],
        "retorno": "number",
    },
]

_GEN_METHODS: list[dict[str, Any]] = [
    {
        "nombre": "senoidal",
        "descripcion": "Genera una senoidal",
        "parametros": [
            {
                "nombre": "freq",
                "tipo": "number",
                "requerido": False,
                "descripcion": "Frecuencia en Hz",
            },
            {"nombre": "amp", "tipo": "number", "requerido": False, "descripcion": "Amplitud Vpp"},
            {
                "nombre": "canal",
                "tipo": "integer",
                "requerido": False,
                "descripcion": "Canal (0 o 1)",
            },
        ],
        "retorno": "void",
    },
    {
        "nombre": "continua",
        "descripcion": "Configura salida DC",
        "parametros": [
            {"nombre": "amp", "tipo": "number", "requerido": False, "descripcion": "Tension DC"}
        ],
        "retorno": "void",
    },
]

_ANALIZADOR_METHODS: list[dict[str, Any]] = [
    {
        "nombre": "set_freq_center",
        "descripcion": "Configura frecuencia central",
        "parametros": [
            {
                "nombre": "hz",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Frecuencia central en Hz",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "set_freq_start",
        "descripcion": "Configura frecuencia de inicio",
        "parametros": [
            {
                "nombre": "hz",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Frecuencia de inicio en Hz",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "set_freq_stop",
        "descripcion": "Configura frecuencia de fin",
        "parametros": [
            {
                "nombre": "hz",
                "tipo": "number",
                "requerido": True,
                "descripcion": "Frecuencia de fin en Hz",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "set_span",
        "descripcion": "Configura el span",
        "parametros": [
            {"nombre": "hz", "tipo": "number", "requerido": True, "descripcion": "Span en Hz"}
        ],
        "retorno": "void",
    },
    {
        "nombre": "get_trace",
        "descripcion": "Obtiene el trazo del analizador",
        "parametros": [],
        "retorno": "array",
    },
    {
        "nombre": "get_marker",
        "descripcion": "Obtiene frecuencia y amplitud de un marker",
        "parametros": [
            {
                "nombre": "marker",
                "tipo": "integer",
                "requerido": True,
                "descripcion": "Numero de marker",
            }
        ],
        "retorno": "(freq, amp)",
    },
    {
        "nombre": "peaksearch",
        "descripcion": "Busca el pico en un marker",
        "parametros": [
            {
                "nombre": "marker",
                "tipo": "integer",
                "requerido": True,
                "descripcion": "Numero de marker",
            }
        ],
        "retorno": "void",
    },
    {
        "nombre": "set_referencelevel",
        "descripcion": "Configura nivel de referencia",
        "parametros": [
            {"nombre": "dbm", "tipo": "number", "requerido": True, "descripcion": "Nivel en dBm"}
        ],
        "retorno": "void",
    },
    {
        "nombre": "set_rbw",
        "descripcion": "Configura resolución de ancho de banda",
        "parametros": [
            {"nombre": "hz", "tipo": "number", "requerido": True, "descripcion": "RBW en Hz"}
        ],
        "retorno": "void",
    },
]

CATEGORY_ACTIONS: dict[str, list[dict[str, Any]]] = {
    "osciloscopio": _OSC_METHODS,
    "generador": _GEN_METHODS,
    "analizador": _ANALIZADOR_METHODS,
}

CATEGORY_TO_BASE: dict[str, type] = {
    "osciloscopio": Osciloscopio,
    "generador": GeneradorArbitrario,
    "analizador": AnalizadorEspectro,
}

# ---------------------------------------------------------------------------
# Metadatos de operadores
# ---------------------------------------------------------------------------

OPERATOR_METADATA: list[dict[str, Any]] = [
    {
        "tipo": "osciloscopio",
        "clase": "OperadorOsciloscopio",
        "descripcion": "Operador para realizar mediciones sobre osciloscopios",
        "metodos": [
            {
                "nombre": "medir_vrms",
                "descripcion": "Mide el valor RMS de un canal",
                "parametros": [
                    {
                        "nombre": "canal",
                        "tipo": "integer",
                        "requerido": False,
                        "descripcion": "Numero de canal",
                    }
                ],
                "retorno": "number",
            },
            {
                "nombre": "medir_thd",
                "descripcion": "Mide la distorsion armonica total",
                "parametros": [
                    {
                        "nombre": "canal",
                        "tipo": "integer",
                        "requerido": False,
                        "descripcion": "Numero de canal",
                    }
                ],
                "retorno": "number",
            },
            {
                "nombre": "medir_rc",
                "descripcion": "Mide capacitancia con circuito RC",
                "parametros": [
                    {
                        "nombre": "r",
                        "tipo": "number",
                        "requerido": True,
                        "descripcion": "Resistencia en ohms",
                    },
                    {
                        "nombre": "canal_vg",
                        "tipo": "string",
                        "requerido": False,
                        "descripcion": "Canal del generador",
                    },
                    {
                        "nombre": "canal_vr",
                        "tipo": "string",
                        "requerido": False,
                        "descripcion": "Canal del resistor",
                    },
                    {
                        "nombre": "metodo",
                        "tipo": "string",
                        "requerido": False,
                        "descripcion": "FFT/Potencia/Lissajous/Tiempo",
                    },
                ],
                "retorno": "number (capacitancia en faradios)",
            },
        ],
    },
    {
        "tipo": "generador",
        "clase": "OperadorGenerador",
        "descripcion": "Operador para generar senales moduladas",
        "metodos": [
            {
                "nombre": "generar_fm",
                "descripcion": "Genera una senal modulada en frecuencia",
                "parametros": [],
                "retorno": "void (stub)",
            },
            {
                "nombre": "generar_am",
                "descripcion": "Genera una senal modulada en amplitud",
                "parametros": [],
                "retorno": "void (stub)",
            },
        ],
    },
]

MAX_INLINE_ELEMENTS = 10000


def _to_json_safe(obj: Any) -> Any:
    """Convierte tipos numpy a tipos Python serializables."""
    if isinstance(obj, np.ndarray):
        if obj.size > MAX_INLINE_ELEMENTS:
            return _serialize_large_array(obj)
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, tuple):
        return [_to_json_safe(x) for x in obj]
    if isinstance(obj, list):
        return [_to_json_safe(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return obj


def _serialize_large_array(arr: np.ndarray) -> dict:
    """Guarda un array grande en archivo temporal y devuelve referencia."""
    with tempfile.NamedTemporaryFile(suffix=".npy", prefix="iv_data_", delete=False) as f:
        np.save(f, arr)
        path = f.name
    return {
        "tipo": "archivo",
        "ruta": path,
        "forma": list(arr.shape),
        "dtype": str(arr.dtype),
        "descripcion": f"Array numpy de {arr.size} elementos guardado en {path}",
    }


def _serialize_trace(time_arr: np.ndarray, voltage_arr: np.ndarray) -> dict:
    """Guarda trazo (tiempo, tension) en archivo temporal si es grande."""
    n = len(time_arr)
    if n > MAX_INLINE_ELEMENTS:
        stacked = np.column_stack((time_arr, voltage_arr))
        with tempfile.NamedTemporaryFile(suffix=".npy", prefix="iv_trace_", delete=False) as f:
            np.save(f, stacked)
            path = f.name
        return {
            "tipo": "archivo",
            "ruta": path,
            "forma": list(stacked.shape),
            "descripcion": f"Trazo de {n} puntos. Array Nx2: col0=tiempo, col1=tension",
        }
    return {"tiempo": time_arr.tolist(), "tension": voltage_arr.tolist()}


def _match_idn(idn: str) -> tuple[type[Instrument], str] | None:
    """Busca una clase de instrumento que coincida con el IDN."""
    for matcher, cls, category in IDN_PATTERNS:
        try:
            if matcher(idn):
                return cls, category
        except Exception:
            continue
    return None


def _scan_subnet_vxi11(subnet: str, timeout_ms: int = 2000) -> list[dict]:
    """Escanea una subred buscando dispositivos VXI-11."""
    import vxi11

    found = []
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        return found

    for host in network.hosts():
        ip = str(host)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 111))
            sock.close()
            if result != 0:
                continue
        except Exception:
            continue

        try:
            inst = vxi11.Instrument(ip)
            inst.timeout = timeout_ms
            idn = inst.ask("*IDN?")
            found.append(
                {
                    "id": f"vxi11_{ip}",
                    "idn": idn.strip(),
                    "conexion": "red",
                    "direccion": ip,
                    "vxi11_handle": inst,
                }
            )
        except Exception:
            pass

    return found


class InstrumentRegistry:
    """Mantiene el estado de los instrumentos descubiertos y conectados."""

    def __init__(self):
        self._connections: dict[str, tuple[Instrument, str]] = {}
        self._rm: pyvisa.ResourceManager | None = None

    # ------------------------------------------------------------------
    # Descubrimiento
    # ------------------------------------------------------------------

    def list_devices(self, subnet: str | None = None) -> list[dict[str, Any]]:
        """Descubre instrumentos via VISA y opcionalmente via VXI-11 en subred."""
        devices = []

        # 1. Escaneo VISA (USB, GPIB, TCPIP)
        try:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()
            for res in resources:
                try:
                    inst = rm.open_resource(res)
                    inst.timeout = 2000
                    idn = inst.query("*IDN?").strip()
                    devices.append(
                        {
                            "id": f"visa_{res}",
                            "idn": idn,
                            "conexion": "usb" if "USB" in res.upper() else "red",
                            "direccion": res,
                        }
                    )
                    inst.close()
                except Exception:
                    pass
            rm.close()
        except Exception:
            pass

        # 2. Escaneo VXI-11 en subred
        if subnet:
            for dev in _scan_subnet_vxi11(subnet):
                dev.pop("vxi11_handle", None)
                devices.append(dev)

        # 3. Eliminar duplicados por IDN
        seen_idns = set()
        unique = []
        for dev in devices:
            clean_idn = dev["idn"].strip().lower()
            if clean_idn and clean_idn not in seen_idns:
                seen_idns.add(clean_idn)
                match = _match_idn(dev["idn"])
                dev["tipo"] = match[1] if match else "desconocido"
                unique.append(dev)
        return unique

    # ------------------------------------------------------------------
    # ResourceManager
    # ------------------------------------------------------------------

    def _get_rm(self) -> pyvisa.ResourceManager:
        """Retorna el ResourceManager global, creandolo si es necesario."""
        if self._rm is None:
            self._rm = pyvisa.ResourceManager()
        return self._rm

    # ------------------------------------------------------------------
    # Conexion
    # ------------------------------------------------------------------

    def connect(self, device_id: str, subnet: str | None = None) -> tuple[Instrument, str]:
        """Conecta a un dispositivo por su ID. Retorna (instancia, categoria)."""
        if device_id in self._connections:
            return self._connections[device_id]

        rm = self._get_rm()

        try:
            # Intentar conexion VISA
            res = rm.open_resource(device_id.replace("visa_", "", 1))
            res.timeout = 3000
            idn = res.query("*IDN?").strip()
            match = _match_idn(idn)
            if match is None:
                res.close()
                raise ValueError(f"No se reconoce el instrumento: {idn}")

            cls, category = match

            inst = cls(res) if cls is RigolDs2202 or issubclass(cls, Osciloscopio) else cls(res)

            self._connections[device_id] = (inst, category)
            # NOTA: NO cerrar rm! El ResourceManager debe mantenerse abierto
            # para que los recursos VISA sigan siendo válidos.
            return inst, category

        except pyvisa.Error:
            # Si falla, cerramos el recurso si se abrio
            if self._rm is not None:
                with contextlib.suppress(Exception):
                    self._rm.close()
                self._rm = None

        # Intentar conexion VXI-11 directa
        if device_id.startswith("vxi11_"):
            ip = device_id.replace("vxi11_", "", 1)
            import vxi11

            vxi = vxi11.Instrument(ip)
            vxi.timeout = 3000
            idn = vxi.ask("*IDN?").strip()
            match = _match_idn(idn)
            if match is None:
                vxi.close()
                raise ValueError(f"No se reconoce el instrumento: {idn}")

            cls, category = match
            inst = cls(None, vxi)
            self._connections[device_id] = (inst, category)
            return inst, category

        raise ValueError(f"No se pudo conectar al dispositivo: {device_id}")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def execute_action(self, device_id: str, action: str, params: dict | None = None) -> Any:
        """Ejecuta un metodo sobre un instrumento."""
        inst, category = self.connect(device_id)
        params = params or {}
        method = getattr(inst, action, None)
        if method is None:
            raise ValueError(f"La accion '{action}' no existe en {type(inst).__name__}")

        result = method(**params)

        # Serializar resultado (manejo especial para get_trace)
        if action == "get_trace" and isinstance(result, tuple) and len(result) == 2:
            t, v = result
            if isinstance(t, np.ndarray) and isinstance(v, np.ndarray):
                return _serialize_trace(t, v)

        return _to_json_safe(result)

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    def execute_operator(
        self, device_id: str, operator_type: str, method: str, params: dict | None = None
    ) -> Any:
        """Instancia un operador y ejecuta un metodo."""
        inst, category = self.connect(device_id)
        params = params or {}

        if operator_type == "osciloscopio":
            op = OperadorOsciloscopio(inst, f"mcp_{device_id}")
        elif operator_type == "generador":
            op = OperadorGenerador(inst, f"mcp_{device_id}")
        else:
            raise ValueError(f"Tipo de operador desconocido: {operator_type}")

        fn = getattr(op, method, None)
        if fn is None:
            raise ValueError(f"El metodo '{method}' no existe en Operador{operator_type.title()}")

        result = fn(**params)
        return _to_json_safe(result)

    # ------------------------------------------------------------------
    # Comandos VISA crudos
    # ------------------------------------------------------------------

    def send_visa(self, device_id: str, command: str, is_query: bool = True) -> str:
        """Envia un comando VISA crudo a un instrumento."""
        inst, _ = self.connect(device_id)
        if is_query:
            return inst.query(command)
        inst.write(command)
        return "OK"

    # ------------------------------------------------------------------
    # Metadatos
    # ------------------------------------------------------------------

    @staticmethod
    def get_available_actions(device_type: str | None = None) -> dict[str, Any]:
        """Retorna las acciones disponibles."""
        if device_type:
            if device_type in CATEGORY_ACTIONS:
                return {device_type: CATEGORY_ACTIONS[device_type]}
            return {}
        return dict(CATEGORY_ACTIONS)

    @staticmethod
    def get_available_operators() -> list[dict[str, Any]]:
        """Retorna los operadores disponibles."""
        return list(OPERATOR_METADATA)

    @staticmethod
    def get_device_types() -> list[str]:
        """Retorna los tipos de dispositivo conocidos."""
        return list(CATEGORY_ACTIONS.keys())

    # ------------------------------------------------------------------
    # Gestion de conexiones
    # ------------------------------------------------------------------

    def close(self, device_id: str):
        """Cierra una conexion especifica."""
        if device_id in self._connections:
            inst, _ = self._connections[device_id]
            with contextlib.suppress(Exception):
                inst.close()
            del self._connections[device_id]

    def close_all(self):
        """Cierra todas las conexiones."""
        for device_id in list(self._connections.keys()):
            self.close(device_id)
        if self._rm is not None:
            with contextlib.suppress(Exception):
                self._rm.close()
            self._rm = None
