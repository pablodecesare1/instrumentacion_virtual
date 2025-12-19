import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import MultipleLocator

from Sweep.Report_generator.TP_REPORT import TPReport
from Sweep.Report_generator.weather_getter import fetch_weather_caba

# -------------------------
# Parámetros de la medición
# -------------------------
F_START = 20.0
F_STOP = 20_000.0
NUM_POINTS = 5
AMPLITUDE_VPP = 5.0
MEDICIONES_POR_FREQ = 3

def createReport(freqs, G_db, incerts, phases_unwrapped, incerts_phases, ruidos, assets_dir):
    pdf = TPReport(fonts_dir=f"{assets_dir}/Fonts")

    pdf.add_cover(
        title="TP Final – Instrumentación Virtual",
        subtitle="Análisis de respuesta en frecuencia",
        institution="UTN",
        authors=["Juan Maurin", "Ariel Sharpe", "Ignacio Gomez", "Pedro Guzman", "Facundo Farcy"],
        date_str=datetime.now().strftime("%B %Y"),
        logo_path=f"{assets_dir}/UTN_logo.jpg",
    )

    pdf.add_page()
    pdf.add_section("Resultados")
    pdf.add_text("En esta sección se muestran los resultados principales del barrido en frecuencia.")

    # -----------------------------------
    # Tabla: parámetros / setup de medida
    # -----------------------------------
    pdf.add_table(
        title="Datos de la medición",
        header=["Parámetro", "Valor"],
        rows=[
            ["F_START [Hz]", f"{F_START:g}"],
            ["F_STOP [Hz]", f"{F_STOP:g}"],
            ["NUM_POINTS", f"{NUM_POINTS:d}"],
            ["AMPLITUDE [Vpp]", f"{AMPLITUDE_VPP:g}"],
            ["MEDICIONES_POR_FREQ", f"{MEDICIONES_POR_FREQ:d}"],
        ]
    )

    # -----------------------------------
    # Tabla: clima actual (API externa)
    # -----------------------------------
    try:
        weather = fetch_weather_caba()
        pdf.add_table(
            title="Condiciones ambientales (CABA) – API externa",
            header=["Magnitud", "Valor"],
            rows=weather["rows"]
        )
    except Exception as e:
        pdf.add_text(f"No se pudo obtener el clima actual (API): {e}", font_size=11)

    # --------------------------------------
    # Tabla: Frecuencia vs Ruido (freq/ruidos)
    # --------------------------------------
    rows_ruido = [[f"{float(f):g}", f"{float(r):.3g}"] for f, r in zip(freqs, ruidos)]
    pdf.add_table(
        title="Ruido por frecuencia",
        header=["Frecuencia [Hz]", "Ruido"],
        rows=rows_ruido
    )

    pdf.add_page()

    # -------------
    # Gráfico bode
    # -------------
    def plot_ganancia():
        plt.semilogx(freqs, G_db, marker="o", label="Ganancia [dB]")
        plt.fill_between(freqs, G_db - incerts, G_db + incerts, alpha=0.3,
                         label="±incerts (k=2)", color='red')
        plt.grid(True, which="both")
        plt.xlabel("Frecuencia [Hz]")
        plt.ylabel("Ganancia [dB]")
        plt.legend()
        plt.title("Bode")

    pdf.add_chart(
        plot_fn=plot_ganancia,
        title="Ganancia",
        caption="Ganancia con incertidumbre expandida (k=2).",
        figsize=(7, 3), dpi=140
    )

    # ------------
    # Gráfico phases_unwrapped
    # ------------
    def plot_phases_unwrapped():
        phases_unwrapped_grad = phases_unwrapped * (180 / np.pi)
        incerts_phases_grad = incerts_phases * (180 / np.pi)

        plt.semilogx(freqs, phases_unwrapped_grad, marker="o", label="phases_unwrapped [°]")
        plt.fill_between(freqs, phases_unwrapped_grad - incerts_phases_grad, phases_unwrapped_grad + incerts_phases_grad, alpha=0.3,
                         label="±incerts_phases (k=2)", color='red')

        plt.xlabel("Frecuencia [Hz]")
        plt.ylabel("phases_unwrapped [°]")
        plt.ylim(-180, 180)

        ax = plt.gca()
        ax.yaxis.set_major_locator(MultipleLocator(45))
        ax.yaxis.set_minor_locator(MultipleLocator(15))
        ax.grid(True, which="major", linestyle="-", linewidth=0.8)
        ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.7)

        plt.legend()
        plt.title("phases_unwrapped")

    pdf.add_chart(
        plot_fn=plot_phases_unwrapped,
        title="phases_unwrapped",
        caption="phases_unwrapped con incertidumbre expandida (k=2).",
        figsize=(7, 3), dpi=140
    )

    pdf.output("TP_reporte.pdf")
    print("Generado: TP_reporte.pdf")
