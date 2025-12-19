import os
from datetime import datetime
from io import BytesIO
from typing import Callable, Sequence, Optional, List, Union

import numpy as np
import pandas as pd
from PIL import Image

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from fpdf import FPDF, XPos, YPos, FontFace


class TPReport(FPDF):
    def __init__(self, fonts_dir: str = "./fonts"):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

        self._section_counter = 0
        self._subsection_counter = 0

        # Matplotlib: mathtext estilo CM
        plt.rcParams["mathtext.fontset"] = "cm"

        # Cargar NewCM desde .otf (CFF) -> FPDF2 lo soporta
        self._load_newcm(fonts_dir)

    # ---------- Fonts ----------
    def _load_newcm(self, fonts_dir: str):
        def p(name: str) -> str:
            return os.path.join(fonts_dir, name)

        self.add_font("NewCM", "",  p("NewCM10_Book.otf"))
        self.add_font("NewCM", "B", p("NewCM10_Bold.otf"))
        self.add_font("NewCM", "I", p("NewCM10_Italic.otf"))
        self.add_font("NewCM", "BI", p("NewCM10_BoldItalic.otf"))

    # ---------- Header/Footer ----------
    def header(self):
        if self.page_no() > 1:
            self.set_font("NewCM", "I", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f"{self.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("NewCM", "I", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f"Página {self.page_no()}", align="C")

    # ---------- Cover ----------
    def add_cover(
        self,
        title: str,
        subtitle: str,
        institution: str,
        authors: List[str],
        date_str: Optional[str] = None,
        logo_path: Optional[str] = None,
    ):
        self.add_page()

        primary = (0, 0, 0)
        secondary = (80, 80, 80)
        date_str = date_str or datetime.now().strftime("%B %Y")

        self.set_y(40)

        # Logo
        if logo_path and os.path.exists(logo_path):
            # centrado
            w = 28
            x = (self.w / 2) - (w / 2)
            self.image(logo_path, x=x, w=w)
            self.ln(25)

        # Title
        self.set_font("NewCM", "B", 22)
        self.set_text_color(*primary)
        self.multi_cell(0, 14, title.upper(), align="C")
        self.ln(5)

        # Subtitle
        if subtitle:
            self.set_font("NewCM", "I", 16)
            self.set_text_color(*secondary)
            self.multi_cell(0, 10, subtitle, align="C")
            self.ln(10)

        # Institution
        if institution:
            self.set_font("NewCM", "B", 14)
            self.set_text_color(*primary)
            self.cell(0, 10, institution, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(10)

        # Authors
        if authors:
            self.set_font("NewCM", "B", 12)
            self.set_text_color(*primary)
            self.cell(0, 8, "Autores", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

            self.set_font("NewCM", "I", 11)
            self.set_text_color(*secondary)
            self.cell(0, 6, ", ".join(authors), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(10)

        # Date
        self.set_font("NewCM", "I", 10)
        self.set_text_color(*secondary)
        self.cell(0, 6, date_str, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---------- Sections ----------
    def add_section(self, title: str):
        self._section_counter += 1
        self._subsection_counter = 0
        self.set_font("NewCM", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"{self._section_counter}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def add_subsection(self, title: str):
        self._subsection_counter += 1
        self.set_font("NewCM", "B", 12)
        self.set_text_color(60, 60, 60)
        self.cell(
            0, 8,
            f"{self._section_counter}.{self._subsection_counter}. {title}",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        self.ln(2)

    def add_text(self, text: str, font_size: float = 12):
        self.set_font("NewCM", "", font_size)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text, align="J")
        self.ln(1)

    # ---------- Tables ----------
    def add_table(
        self,
        title: str,
        header: Sequence[str],
        rows: Sequence[Sequence[Union[str, int, float]]],
        font_size: int = 11,
    ):
        self.add_subsection(title)
        self.set_font("NewCM", "", font_size)

        black = (0, 0, 0)
        green = (160, 200, 160)
        white = (250, 253, 250)

        head_style = FontFace(emphasis="BOLD", size_pt=font_size, color=black, fill_color=green)

        with self.table(
            cell_fill_mode="ROWS",
            text_align="CENTER",
            headings_style=head_style,
            repeat_headings=False,
        ) as table:
            # header
            r0 = table.row()
            for h in header:
                r0.cell(str(h))

            # rows
            for rr in rows:
                r = table.row()
                for c in rr:
                    r.cell(str(c))

        self.ln(2)

    def add_df_table(self, title: str, df: pd.DataFrame, font_size: int = 11):
        self.add_table(title, list(df.columns), df.values.tolist(), font_size=font_size)

    # ---------- Charts: plt.* directo ----------
    def add_chart(
        self,
        plot_fn,
        title: str = "",
        caption: str = "",
        figsize=(7, 3),
        dpi: int = 140,
        width_mm: float | None = None,
    ):
        """
        plot_fn: función SIN args que usa plt.plot/plt.semilogx/fill_between/etc.
        IMPORTANTE: NO uses plt.figure() ni plt.show() adentro.
        """
        if title:
            self.add_subsection(title)

        # Figura MANEJADA por pyplot (así plt.* funciona)
        fig = plt.figure(figsize=figsize, dpi=dpi)

        # Tu código de plot (usa plt.*)
        plot_fn()

        # Render a PNG en memoria
        buf = BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=dpi)
        plt.close(fig)
        buf.seek(0)

        # Meter al PDF (sin archivos)
        img = Image.open(buf)

        if width_mm is None:
            width_mm = self.epw  # ancho útil de página

        self.image(img, w=width_mm)

        if caption:
            self.set_font("NewCM", "I", 10)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 5, caption, align="L")
            self.ln(1)

        buf.close()
