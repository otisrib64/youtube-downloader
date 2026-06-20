import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import yt_dlp
import imageio_ffmpeg
import os

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


class YTDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("620x560")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")

        self._download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self._queue: list[str] = []
        self._running = False
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#16213e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="#16213e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TProgressbar", troughcolor="#16213e", background="#4CAF50")
        style.configure("Queue.TButton", font=("Segoe UI", 9), padding=4)

        pad = {"padx": 16, "pady": 5}

        tk.Label(self, text="YouTube Downloader", bg="#1a1a2e", fg="#ffffff",
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 2))
        tk.Label(self, text="Adicione um ou mais links para baixar em fila", bg="#1a1a2e", fg="#aaaaaa",
                 font=("Segoe UI", 9)).pack(pady=(0, 10))

        # URL input row
        url_frame = tk.Frame(self, bg="#1a1a2e")
        url_frame.pack(fill="x", **pad)
        ttk.Label(url_frame, text="Link do YouTube:").pack(anchor="w")
        row = tk.Frame(url_frame, bg="#1a1a2e")
        row.pack(fill="x", pady=(4, 0))
        self._url_var = tk.StringVar()
        url_entry = ttk.Entry(row, textvariable=self._url_var, width=56)
        url_entry.pack(side="left", fill="x", expand=True)
        url_entry.bind("<Return>", lambda _: self._add_to_queue())
        ttk.Button(row, text="Adicionar", style="Queue.TButton",
                   command=self._add_to_queue).pack(side="left", padx=(6, 0))

        # Queue list
        queue_frame = tk.Frame(self, bg="#1a1a2e")
        queue_frame.pack(fill="x", **pad)
        header = tk.Frame(queue_frame, bg="#1a1a2e")
        header.pack(fill="x")
        ttk.Label(header, text="Fila de downloads:").pack(side="left", anchor="w")
        ttk.Button(header, text="Remover selecionado", style="Queue.TButton",
                   command=self._remove_selected).pack(side="right", padx=(4, 0))
        ttk.Button(header, text="Limpar tudo", style="Queue.TButton",
                   command=self._clear_queue).pack(side="right")

        list_frame = tk.Frame(queue_frame, bg="#16213e", bd=1, relief="sunken")
        list_frame.pack(fill="x", pady=(4, 0))
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self._listbox = tk.Listbox(
            list_frame, height=7, bg="#16213e", fg="#e0e0e0",
            selectbackground="#0f3460", selectforeground="#ffffff",
            font=("Segoe UI", 9), relief="flat", bd=0,
            yscrollcommand=scrollbar.set, activestyle="none"
        )
        scrollbar.config(command=self._listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self._listbox.pack(fill="x", padx=4, pady=4)

        self._count_var = tk.StringVar(value="0 links na fila")
        tk.Label(queue_frame, textvariable=self._count_var, bg="#1a1a2e", fg="#888888",
                 font=("Segoe UI", 8)).pack(anchor="e", pady=(2, 0))

        # Directory picker
        dir_frame = tk.Frame(self, bg="#1a1a2e")
        dir_frame.pack(fill="x", **pad)
        ttk.Label(dir_frame, text="Pasta de destino:").pack(anchor="w")
        row2 = tk.Frame(dir_frame, bg="#1a1a2e")
        row2.pack(fill="x", pady=(4, 0))
        self._dir_var = tk.StringVar(value=self._download_dir)
        ttk.Entry(row2, textvariable=self._dir_var, width=56).pack(side="left", fill="x", expand=True)
        ttk.Button(row2, text="...", width=4, command=self._pick_dir).pack(side="left", padx=(6, 0))

        # Format selector
        fmt_frame = tk.Frame(self, bg="#1a1a2e")
        fmt_frame.pack(fill="x", **pad)
        ttk.Label(fmt_frame, text="Formato:").pack(anchor="w")
        self._fmt_var = tk.StringVar(value="Melhor qualidade (vídeo + áudio)")
        formats = [
            "Melhor qualidade (vídeo + áudio)",
            "1080p (MP4)",
            "720p (MP4)",
            "480p (MP4)",
            "Apenas áudio (MP3)",
        ]
        ttk.Combobox(fmt_frame, textvariable=self._fmt_var, values=formats,
                     state="readonly", width=40).pack(anchor="w", pady=(4, 0))

        # Cookie browser selector
        cookie_frame = tk.Frame(self, bg="#1a1a2e")
        cookie_frame.pack(fill="x", **pad)
        ttk.Label(cookie_frame, text="Cookies do navegador (use se o YouTube bloquear):").pack(anchor="w")
        self._browser_var = tk.StringVar(value="Nenhum")
        browsers = ["Nenhum", "Chrome", "Firefox", "Edge", "Brave"]
        ttk.Combobox(cookie_frame, textvariable=self._browser_var, values=browsers,
                     state="readonly", width=20).pack(anchor="w", pady=(4, 0))

        # Progress
        self._progress = ttk.Progressbar(self, mode="indeterminate", length=588)
        self._progress.pack(pady=(10, 0))

        self._status_var = tk.StringVar(value="Pronto para baixar.")
        tk.Label(self, textvariable=self._status_var, bg="#1a1a2e", fg="#aaaaaa",
                 font=("Segoe UI", 9), wraplength=580, justify="left").pack(pady=(4, 0))

        self._btn = ttk.Button(self, text="Baixar tudo", command=self._start_queue)
        self._btn.pack(pady=(10, 0))

    def _add_to_queue(self):
        url = self._url_var.get().strip()
        if not url:
            return
        if url in self._queue:
            messagebox.showwarning("Aviso", "Esse link já está na fila.")
            return
        self._queue.append(url)
        short = url if len(url) <= 70 else url[:67] + "..."
        self._listbox.insert("end", short)
        self._url_var.set("")
        self._update_count()

    def _remove_selected(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._listbox.delete(idx)
        self._queue.pop(idx)
        self._update_count()

    def _clear_queue(self):
        self._listbox.delete(0, "end")
        self._queue.clear()
        self._update_count()

    def _update_count(self):
        n = len(self._queue)
        self._count_var.set(f"{n} link{'s' if n != 1 else ''} na fila")

    def _pick_dir(self):
        folder = filedialog.askdirectory(initialdir=self._dir_var.get())
        if folder:
            self._dir_var.set(folder)

    def _format_opts(self):
        fmt = self._fmt_var.get()
        out_tmpl = os.path.join(self._dir_var.get(), "%(title)s.%(ext)s")
        base = {
            "outtmpl": out_tmpl,
            "progress_hooks": [self._on_progress],
            "ffmpeg_location": FFMPEG_PATH,
        }

        browser = self._browser_var.get().lower()
        if browser != "nenhum":
            base["cookiesfrombrowser"] = (browser, None, None, None)
        if fmt == "Apenas áudio (MP3)":
            return {**base, "format": "bestaudio/best",
                    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]}
        if fmt == "1080p (MP4)":
            return {**base, "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
                    "merge_output_format": "mp4"}
        if fmt == "720p (MP4)":
            return {**base, "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
                    "merge_output_format": "mp4"}
        if fmt == "480p (MP4)":
            return {**base, "format": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
                    "merge_output_format": "mp4"}
        return {**base, "format": "bestvideo+bestaudio/best", "merge_output_format": "mp4"}

    def _on_progress(self, d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            self._status_var.set(f"Baixando... {pct}  |  {speed}  |  ETA {eta}")
        elif d["status"] == "finished":
            self._status_var.set("Processando arquivo...")

    def _start_queue(self):
        if not self._queue:
            messagebox.showwarning("Aviso", "Adicione pelo menos um link à fila.")
            return
        dest = self._dir_var.get().strip()
        if not os.path.isdir(dest):
            messagebox.showerror("Erro", "Pasta de destino não existe.")
            return
        self._running = True
        self._btn.state(["disabled"])
        self._progress.start(10)
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        queue_snapshot = self._queue.copy()
        errors: list[tuple[str, str]] = []

        for i, url in enumerate(queue_snapshot):
            self.after(0, self._status_var.set,
                       f"[{i+1}/{len(queue_snapshot)}] Iniciando...")
            try:
                with yt_dlp.YoutubeDL(self._format_opts()) as ydl:
                    ydl.download([url])
                self.after(0, self._listbox.itemconfig, i, {"fg": "#4CAF50"})
            except Exception as exc:
                errors.append((url, str(exc)))
                self.after(0, self._listbox.itemconfig, i, {"fg": "#f44336"})

        self.after(0, self._queue_done, errors)

    def _queue_done(self, errors: list[tuple[str, str]]):
        self._progress.stop()
        self._btn.state(["!disabled"])
        total = len(self._queue)
        ok = total - len(errors)

        if not errors:
            self._status_var.set(f"Concluido! {total} arquivo(s) salvo(s) em: {self._dir_var.get()}")
            messagebox.showinfo("Pronto!", f"{total} download(s) concluido(s)!\nSalvo em:\n{self._dir_var.get()}")
        else:
            self._status_var.set(f"{ok}/{total} concluidos. {len(errors)} erro(s).")
            err_msg = "\n\n".join(f"{u[:60]}...\n{e}" for u, e in errors)
            messagebox.showerror("Alguns downloads falharam", err_msg)


if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()
