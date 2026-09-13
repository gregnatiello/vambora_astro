"""Interface desktop simples para gerar carrosseis sem usar o terminal."""

from __future__ import annotations

import threading
import tkinter as tk
import os
from pathlib import Path
from tkinter import messagebox, ttk

from main import generate_post
from src import topic_selector, trend_finder


class GeneratorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gerador de Carrosseis TikTok")
        self.geometry("780x650")
        self.minsize(700, 560)
        self.trends: list[dict] = []
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        header = ttk.Frame(self, padding=(24, 20, 24, 8))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Gerador de carrosseis", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text="Escolha um assunto, ajuste o tom e gere seu pacote pronto para revisar.").pack(anchor="w", pady=(4, 0))

        mode = ttk.LabelFrame(self, text="1. Escolha a origem do tema", padding=12)
        mode.grid(row=1, column=0, padx=24, pady=8, sticky="ew")
        self.mode = tk.StringVar(value="trend")
        ttk.Radiobutton(mode, text="Usar uma tendência", variable=self.mode, value="trend", command=self._toggle_mode).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(mode, text="Criar meu próprio tema", variable=self.mode, value="custom", command=self._toggle_mode).grid(row=0, column=1, padx=(24, 0), sticky="w")
        ttk.Radiobutton(mode, text="Teste local", variable=self.mode, value="test", command=self._toggle_mode).grid(row=0, column=2, padx=(24, 0), sticky="w")

        self.topic_entry = ttk.Entry(mode)
        self.topic_entry.grid(row=1, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        mode.columnconfigure(0, weight=1)
        mode.columnconfigure(1, weight=1)
        self.search_button = ttk.Button(mode, text="Buscar tendências", command=self._load_trends)
        self.search_button.grid(row=1, column=2, padx=(12, 0), pady=(12, 0))

        trends_frame = ttk.Frame(self, padding=(24, 0, 24, 8))
        trends_frame.grid(row=2, column=0, sticky="ew")
        trends_frame.columnconfigure(0, weight=1)
        ttk.Label(trends_frame, text="Tendências encontradas (selecione uma ou deixe vazio para escolher automaticamente):").grid(row=0, column=0, sticky="w")
        self.trend_list = tk.Listbox(trends_frame, height=6, exportselection=False)
        self.trend_list.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.trend_list.bind("<<ListboxSelect>>", self._select_trend)

        options = ttk.LabelFrame(self, text="2. Ajustes da geração", padding=12)
        options.grid(row=3, column=0, padx=24, pady=8, sticky="nsew")
        options.columnconfigure(0, weight=1)
        options.rowconfigure(1, weight=1)
        ttk.Label(options, text="Instrução adicional para a IA (opcional):").grid(row=0, column=0, sticky="w")
        self.instruction = tk.Text(options, height=5, wrap="word")
        self.instruction.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.instruction.insert("1.0", "Seja mais incisivo e provocador, sem fazer acusações não confirmadas.")

        footer = ttk.Frame(self, padding=(24, 8, 24, 20))
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.status = ttk.Label(footer, text="Pronto para gerar.")
        self.status.grid(row=0, column=0, sticky="w")
        self.generate_button = ttk.Button(footer, text="Gerar carrossel", command=self._generate)
        self.generate_button.grid(row=0, column=1, padx=(12, 0), ipadx=18, ipady=6)
        self._toggle_mode()

    def _toggle_mode(self) -> None:
        custom = self.mode.get() == "custom"
        trend = self.mode.get() == "trend"
        self.topic_entry.configure(state="normal" if custom else "disabled")
        self.search_button.configure(state="normal" if trend else "disabled")
        self.trend_list.configure(state="normal" if trend else "disabled")

    def _load_trends(self) -> None:
        self.search_button.configure(state="disabled")
        self.status.configure(text="Buscando tendências... Isso pode levar alguns segundos.")
        threading.Thread(target=self._load_trends_worker, daemon=True).start()

    def _load_trends_worker(self) -> None:
        try:
            trends = trend_finder.find_trends()
            self.after(0, self._show_trends, trends)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self._show_error(str(exc)))

    def _show_trends(self, trends: list[dict]) -> None:
        self.trends = trends
        self.trend_list.delete(0, tk.END)
        for item in trends:
            source = item.get("source", "")
            self.trend_list.insert(tk.END, f"{item['title']}  [{source}]")
        self.search_button.configure(state="normal")
        self.status.configure(text=f"{len(trends)} tendências encontradas. Escolha uma ou gere automaticamente.")

    def _select_trend(self, _event: object) -> None:
        selection = self.trend_list.curselection()
        if selection and selection[0] < len(self.trends):
            self.topic_entry.delete(0, tk.END)
            self.topic_entry.insert(0, self.trends[selection[0]]["title"])

    def _generate(self) -> None:
        mode = self.mode.get()
        selected = None
        if mode == "custom" and not self.topic_entry.get().strip():
            messagebox.showwarning("Tema necessário", "Digite o tema que deseja transformar em carrossel.")
            return
        if mode == "trend":
            selection = self.trend_list.curselection()
            if selection and selection[0] < len(self.trends):
                selected = self.trends[selection[0]]
        self.generate_button.configure(state="disabled")
        self.status.configure(text="Gerando conteúdo e imagens... aguarde.")
        threading.Thread(
            target=self._generate_worker,
            args=(mode, self.topic_entry.get(), selected, self.instruction.get("1.0", tk.END).strip()),
            daemon=True,
        ).start()

    def _generate_worker(self, mode: str, topic: str, selected: dict | None, instruction: str) -> None:
        try:
            output = generate_post(mode=mode, topic_text=topic, selected_topic=selected, instruction=instruction, test=mode == "test")
            self.after(0, self._generation_finished, output)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self._show_error(str(exc)))

    def _generation_finished(self, output: str) -> None:
        self.generate_button.configure(state="normal")
        self.status.configure(text=f"Pronto: {output}")
        if messagebox.askyesno("Carrossel criado", f"O pacote foi salvo em:\n{output}\n\nAbrir a pasta agora?"):
            os.startfile(Path(output).resolve())

    def _show_error(self, error: str) -> None:
        self.generate_button.configure(state="normal")
        self.search_button.configure(state="normal")
        self.status.configure(text="Não foi possível concluir a operação.")
        messagebox.showerror("Erro", error)


if __name__ == "__main__":
    GeneratorApp().mainloop()