import threading
import ipaddress
import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification

# Iconos vectoriales builtin (con fallback)
try:
    from ttkbootstrap.icons import Icon  # ttkbootstrap >= algunas versiones
except Exception:
    Icon = None

from .gui_queue import GuiQueue
from InstVirtualLib.Sweep.GUI.network_finder.scanner import escanear_red
from .measurement import run_measurement


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")

        self.title("Sistema de Medición")
        self.minsize(980, 660)
        self.geometry("1040x720")

        self.gui_queue = GuiQueue()
        self._icons = {}            # evita GC en PhotoImage
        self._sort_state = {}       # sorting por columna
        self._measurement_total = 0
        self._measurement_zero_based = None

        self._build_widgets()
        self._defaults()
        self._tick_queue()

    # =========================
    # Helpers UI
    # =========================
    def _toast(self, title: str, msg: str, style: str = "info", duration: int = 2600):
        """
        style: info | success | warning | danger
        """
        try:
            ToastNotification(
                title=title,
                message=msg,
                duration=duration,
                bootstyle=style,
                position=(24, 24, "se"),
            ).show_toast()
        except Exception:
            print(f"[{style.upper()}] {title}: {msg}")

    def _set_status(self, text: str, style: str = "secondary"):
        self.lbl_status.configure(text=text, bootstyle=style)

    def _set_busy(self, busy: bool, *, task: str = "idle", status: str | None = None):
        if status is not None:
            if task == "scan":
                self._set_status(status, "info")
            elif task == "measure":
                self._set_status(status, "success")
            else:
                self._set_status(status, "secondary")

        state = "disabled" if busy else "normal"
        for b in (self.btn_scan, self.btn_assign_osc, self.btn_assign_gen, self.btn_measure):
            b.configure(state=state)

        if busy and task == "scan":
            self.progress.configure(mode="determinate")
            self.progress.stop()
            self.progress["value"] = 0
            self.lbl_pct.configure(text="0%")
        elif busy and task == "measure":
            total = self._measurement_total if self._measurement_total > 0 else 1
            self.progress.stop()
            self.progress.configure(mode="determinate", maximum=total)
            self.progress["value"] = 0
            self.lbl_pct.configure(text=f"0/{self._measurement_total}" if self._measurement_total > 0 else "")
        else:
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress["value"] = 0
            self.lbl_pct.configure(text="")
            self._measurement_total = 0
            self._measurement_zero_based = None

    def _make_icon(self, name: str, size: int = 16):
        """
        Ícono vectorial builtin (font-based) si existe.
        Si no existe Icon en tu entorno, devuelve None (y el botón queda texto-only).
        """
        if Icon is None:
            return None
        key = f"{name}_{size}"
        if key not in self._icons:
            try:
                self._icons[key] = Icon(name=name, size=size).image
            except Exception:
                self._icons[key] = None
        return self._icons[key]

    # =========================
    # Build UI
    # =========================
    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        header = tb.Frame(self, padding=(18, 16, 18, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tb.Label(header, text="Sistema de Medición", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        tb.Label(
            header,
            text="Scan SCPI → asignás Osc/Gen → corrés el sweep → sale reporte. Clean.",
            bootstyle="secondary",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Content
        content = tb.Frame(self, padding=(18, 10, 18, 10))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=5)
        content.rowconfigure(0, weight=1)

        # Left: Params
        card_params = tb.Labelframe(content, text=" Parámetros de Sweep ", padding=14, bootstyle="info")
        card_params.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        card_params.columnconfigure(1, weight=1)

        tb.Label(
            card_params,
            text="Tip: si no sabés qué tocar, dejá defaults y mandale.",
            bootstyle="secondary",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self.entry_f_inicio = self._field(card_params, 1, "F inicio", "Hz", kind="float")
        self.entry_f_stop = self._field(card_params, 2, "F stop", "Hz", kind="float")
        self.entry_puntos = self._field(card_params, 3, "Puntos", "", kind="int")
        self.entry_mediciones = self._field(card_params, 4, "Mediciones / freq", "", kind="int")
        self.entry_amplitud = self._field(card_params, 5, "Amplitud", "Vpp", kind="float")

        tb.Separator(card_params).grid(row=6, column=0, columnspan=3, sticky="ew", pady=12)

        tb.Label(card_params, text="IP Osciloscopio").grid(row=7, column=0, sticky="w", pady=6)
        self.entry_ip_osc = tb.Entry(card_params)
        self.entry_ip_osc.grid(row=7, column=1, columnspan=2, sticky="ew", pady=6)

        tb.Label(card_params, text="IP Generador").grid(row=8, column=0, sticky="w", pady=6)
        self.entry_ip_gen = tb.Entry(card_params)
        self.entry_ip_gen.grid(row=8, column=1, columnspan=2, sticky="ew", pady=6)

        # Right: Instruments
        card_scan = tb.Labelframe(content, text=" Instrumentos SCPI ", padding=14, bootstyle="primary")
        card_scan.grid(row=0, column=1, sticky="nsew")
        card_scan.columnconfigure(0, weight=1)
        card_scan.rowconfigure(2, weight=1)

        tb.Label(
            card_scan,
            text="Doble click: asignación automática (Osc si vacío, sino Gen).",
            bootstyle="secondary",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        actions = tb.Frame(card_scan)
        actions.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        actions.columnconfigure(4, weight=1)

        # Icons (builtin vector, con fallback)
        img_search = self._make_icon("search", 16)
        img_osc = self._make_icon("display", 16)       # si no existe, cae a texto
        img_gen = self._make_icon("music", 16)         # si no existe, cae a texto
        img_play = self._make_icon("play", 16)

        self.btn_scan = tb.Button(
            actions,
            text=" Buscar",
            image=img_search,
            compound=LEFT if img_search else None,
            bootstyle="info",
            command=self._escaneo_en_hilo,
        )
        self.btn_scan.grid(row=0, column=0, padx=(0, 8))

        self.btn_assign_osc = tb.Button(
            actions,
            text=" Asignar a Osc",
            image=img_osc,
            compound=LEFT if img_osc else None,
            bootstyle="secondary",
            command=lambda: self._assign_selected("osc"),
        )
        self.btn_assign_osc.grid(row=0, column=1, padx=(0, 8))

        self.btn_assign_gen = tb.Button(
            actions,
            text=" Asignar a Gen",
            image=img_gen,
            compound=LEFT if img_gen else None,
            bootstyle="secondary",
            command=lambda: self._assign_selected("gen"),
        )
        self.btn_assign_gen.grid(row=0, column=2, padx=(0, 8))

        self.btn_measure = tb.Button(
            actions,
            text=" Iniciar medición",
            image=img_play,
            compound=LEFT if img_play else None,
            bootstyle="success",
            command=self._iniciar_medicion,
        )
        self.btn_measure.grid(row=0, column=5, sticky="e")

        # Table (ttk.Treeview)
        table_frame = tb.Frame(card_scan)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("ip", "proto", "idn")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = tb.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, bootstyle="round")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("ip", text="IP", command=lambda: self._sort_by("ip"))
        self.tree.heading("proto", text="Proto", command=lambda: self._sort_by("proto"))
        self.tree.heading("idn", text="IDN", command=lambda: self._sort_by("idn"))

        self.tree.column("ip", width=160, anchor="w", stretch=False)
        self.tree.column("proto", width=90, anchor="center", stretch=False)
        self.tree.column("idn", width=520, anchor="w", stretch=True)

        self.tree.bind("<Double-Button-1>", lambda e: self._assign_selected("auto"))
        self.tree.bind("<Return>", lambda e: self._assign_selected("auto"))

        # Bottom
        bottom = tb.Frame(self, padding=(18, 6, 18, 14))
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(1, weight=1)

        tb.Label(bottom, text="Estado:", bootstyle="secondary").grid(row=0, column=0, sticky="w")
        self.lbl_status = tb.Label(bottom, text="Listo.", bootstyle="secondary")
        self.lbl_status.grid(row=0, column=1, sticky="w")

        self.lbl_pct = tb.Label(bottom, text="", bootstyle="secondary")
        self.lbl_pct.grid(row=0, column=2, sticky="e")

        self.progress = tb.Progressbar(bottom, orient="horizontal", mode="determinate", bootstyle="success-striped")
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

    def _field(self, parent, row, label, unit, kind="str"):
        tb.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)

        e = tb.Entry(parent)
        e.grid(row=row, column=1, sticky="ew", pady=6, padx=(0, 8))
        e._kind = kind

        tb.Label(parent, text=unit or "", bootstyle="secondary").grid(row=row, column=2, sticky="w", pady=6)
        e.bind("<FocusIn>", lambda _e: e.configure(bootstyle=""))
        return e

    def _defaults(self):
        self.entry_f_inicio.insert(0, "200")
        self.entry_f_stop.insert(0, "20000")
        self.entry_puntos.insert(0, "20")
        self.entry_mediciones.insert(0, "3")
        self.entry_amplitud.insert(0, "5")

        self.entry_ip_osc.insert(0, "192.168.0.100")
        self.entry_ip_gen.insert(0, "192.168.0.101")

        self._update_table([])

    # =========================
    # Queue tick
    # =========================
    def _tick_queue(self):
        self.gui_queue.drain()
        self.after(50, self._tick_queue)

    # =========================
    # Scan
    # =========================
    def _set_progress(self, pct: float):
        if str(self.progress["mode"]) == "determinate":
            self.progress["value"] = pct
            self.lbl_pct.configure(text=f"{pct:0.0f}%")

    def _prepare_measure_progress(self, total: int):
        self._measurement_total = max(int(total), 1)
        self._measurement_zero_based = None
        self.progress.stop()
        self.progress.configure(mode="determinate", maximum=self._measurement_total)
        self.progress["value"] = 0
        self.lbl_pct.configure(text=f"0/{self._measurement_total}")

    def _set_measure_progress(self, estado_actual, total: int):
        total = max(int(total), 1)
        if self._measurement_total != total:
            self._prepare_measure_progress(total)

        try:
            current = float(estado_actual)
            if self._measurement_zero_based is None:
                self._measurement_zero_based = (current == 0)
            if self._measurement_zero_based:
                current += 1

            current_int = max(0, min(int(round(current)), total))
            self.progress["value"] = current_int
            self.lbl_pct.configure(text=f"{current_int}/{total}")
            self._set_status(f"Midiendo frecuencia {current_int}/{total}", "success")
        except (TypeError, ValueError):
            self._set_status(f"Midiendo... {estado_actual}", "success")

    def _clear_table(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    def _parse_result_line(self, r: str):
        parts = [p.strip() for p in r.split("|", 2)]
        ip = parts[0].replace("🟢", "").replace("✅", "").strip()
        proto = parts[1] if len(parts) > 1 else "SCPI"
        idn = parts[2] if len(parts) > 2 else ""
        return ip, proto, idn

    def _update_table(self, resultados: list[str]):
        self._clear_table()

        if not resultados:
            self._set_busy(False, task="idle", status="Listo.")
            self._toast("Scan", "No se detectaron instrumentos SCPI.", "warning")
            return

        for r in resultados:
            try:
                ip, proto, idn = self._parse_result_line(r)
                ipaddress.ip_address(ip)
                self.tree.insert("", "end", values=(ip, proto, idn))
            except Exception:
                continue

        self._set_busy(False, task="idle", status="Listo.")
        self._toast("Scan", f"Encontré {len(self.tree.get_children())} instrumento(s).", "success")

    def _escaneo_en_hilo(self):
        self._clear_table()
        self._set_busy(True, task="scan", status="Escaneando instrumentos SCPI...")
        self._toast("Scan", "Escaneando red… esto puede tardar un toque.", "info")

        threading.Thread(
            target=escanear_red,
            args=(self.gui_queue, self._set_progress, self._update_table),
            daemon=True,
        ).start()

    # =========================
    # Sorting
    # =========================
    def _sort_by(self, col: str):
        rows = [(self.tree.set(iid, col), iid) for iid in self.tree.get_children("")]
        ascending = not self._sort_state.get(col, True)
        self._sort_state[col] = ascending

        def key(v):
            val = v[0]
            if col == "ip":
                try:
                    return int(ipaddress.ip_address(val))
                except Exception:
                    return 0
            return (val or "").lower()

        rows.sort(key=key, reverse=not ascending)
        for idx, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", idx)

    # =========================
    # Selection -> assign
    # =========================
    def _get_selected_ip(self) -> str | None:
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return values[0] if values else None

    def _assign_selected(self, target: str):
        ip = self._get_selected_ip()
        if not ip:
            self._toast("Selección", "Seleccioná un instrumento primero.", "warning")
            return

        try:
            ipaddress.ip_address(ip)
        except Exception:
            self._toast("Selección", "La IP seleccionada no es válida.", "danger")
            return

        if target == "auto":
            if not self.entry_ip_osc.get().strip():
                target = "osc"
            elif not self.entry_ip_gen.get().strip():
                target = "gen"
            else:
                target = "osc"

        if target == "osc":
            self.entry_ip_osc.delete(0, tk.END)
            self.entry_ip_osc.insert(0, ip)
            self._set_status(f"Asignado Osc: {ip}", "info")
            self._toast("Asignación", f"Osciloscopio ← {ip}", "info")
        elif target == "gen":
            self.entry_ip_gen.delete(0, tk.END)
            self.entry_ip_gen.insert(0, ip)
            self._set_status(f"Asignado Gen: {ip}", "info")
            self._toast("Asignación", f"Generador ← {ip}", "info")

    # =========================
    # Measurement
    # =========================
    def _collect_params(self) -> dict:
        def mark_bad(entry):
            try:
                entry.configure(bootstyle="danger")
            except Exception:
                pass

        def parse(entry, name: str):
            raw = entry.get().strip()
            if raw == "":
                mark_bad(entry)
                raise ValueError(f"Falta: {name}")

            kind = getattr(entry, "_kind", "str")
            try:
                if kind == "int":
                    return int(raw)
                if kind == "float":
                    return float(raw)
                return raw
            except Exception:
                mark_bad(entry)
                raise ValueError(f"Valor inválido en {name}: '{raw}'")

        ip_osc = self.entry_ip_osc.get().strip()
        ip_gen = self.entry_ip_gen.get().strip()
        try:
            ipaddress.ip_address(ip_osc)
            ipaddress.ip_address(ip_gen)
        except Exception:
            mark_bad(self.entry_ip_osc)
            mark_bad(self.entry_ip_gen)
            raise ValueError("IP inválida (osc o gen).")

        f_inicio = parse(self.entry_f_inicio, "F inicio")
        f_stop = parse(self.entry_f_stop, "F stop")
        if f_inicio <= 0 or f_stop <= 0 or f_stop <= f_inicio:
            mark_bad(self.entry_f_inicio)
            mark_bad(self.entry_f_stop)
            raise ValueError("Frecuencias inválidas (stop debe ser > inicio, y > 0).")

        puntos = parse(self.entry_puntos, "Puntos")
        mediciones = parse(self.entry_mediciones, "Mediciones/freq")
        amplitud = parse(self.entry_amplitud, "Amplitud Vpp")

        if puntos <= 0 or mediciones <= 0 or amplitud <= 0:
            mark_bad(self.entry_puntos)
            mark_bad(self.entry_mediciones)
            mark_bad(self.entry_amplitud)
            raise ValueError("Puntos/mediciones/amplitud deben ser > 0.")

        return {
            "ip_osc": ip_osc,
            "ip_gen": ip_gen,
            "f_inicio": float(f_inicio),
            "f_stop": float(f_stop),
            "puntos": int(puntos),
            "mediciones": int(mediciones),
            "amplitud": float(amplitud),
        }

    def _measurement_worker(self):
        try:
            params = self._collect_params()
            total_puntos = int(params["puntos"])
            self.gui_queue.put(lambda t=total_puntos: self._prepare_measure_progress(t))
            self.gui_queue.put(lambda: self._set_status("Midiendo... (no toques nada 🙃)", "success"))

            def progress_callback(estado_actual, total):
                self.gui_queue.put(
                    lambda estado=estado_actual, total_med=total: self._set_measure_progress(estado, total_med)
                )

            run_measurement(params, progress_callback=progress_callback)
            self.gui_queue.put(lambda: self._toast("Medición", "Finalizada correctamente ✅", "success", duration=3200))
            self.gui_queue.put(lambda: self._set_busy(False, task="idle", status="Listo."))
        except Exception as e:
            msg = str(e) if str(e) else "Error desconocido"
            self.gui_queue.put(lambda: self._toast("Error", msg, "danger", duration=4200))
            self.gui_queue.put(lambda: self._set_busy(False, task="idle", status="Listo."))

    def _iniciar_medicion(self):
        self._set_busy(True, task="measure", status="Iniciando medición...")
        self._toast("Medición", "Arrancando…", "info")
        threading.Thread(target=self._measurement_worker, daemon=True).start()
