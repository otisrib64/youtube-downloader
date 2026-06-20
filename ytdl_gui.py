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
        self.geometry("600x420")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")

        self._download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#16213e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="#16213e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TProgressbar", troughcolor="#16213e", background="#4CAF50")

        pad = {"padx": 16, "pady": 6}

        # Title
        tk.Label(self, text="YouTube Downloader", bg="#1a1a2e", fg="#ffffff",
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 4))
        tk.Label(self, text="Cole o link e escolha onde salvar", bg="#1a1a2e", fg="#aaaaaa",
                 font=("Segoe UI", 9)).pack(pady=(0, 16))

        # URL field
        url_frame = tk.Frame(self, bg="#1a1a2e")
        url_frame.pack(fill="x", **pad)
        ttk.Label(url_frame, text="Link do YouTube:").pack(anchor="w")
        self._url_var = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self._url_var, width=70).pack(fill="x", pady=(4, 0))

        # Directory picker
        dir_frame = tk.Frame(self, bg="#1a1a2e")
        dir_frame.pack(fill="x", **pad)
        ttk.Label(dir_frame, text="Pasta de destino:").pack(anchor="w")
        row = tk.Frame(dir_frame, bg="#1a1a2e")
        row.pack(fill="x", pady=(4, 0))
        self._dir_var = tk.StringVar(value=self._download_dir)
        ttk.Entry(row, textvariable=self._dir_var, width=56).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="...", width=4, command=self._pick_dir).pack(side="left", padx=(6, 0))

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

        # Progress bar
        self._progress = ttk.Progressbar(self, mode="indeterminate", length=560)
        self._progress.pack(pady=(12, 0))

        # Status label
        self._status_var = tk.StringVar(value="Pronto para baixar.")
        tk.Label(self, textvariable=self._status_var, bg="#1a1a2e", fg="#aaaaaa",
                 font=("Segoe UI", 9), wraplength=560, justify="left").pack(pady=(6, 0))

        # Download button
        self._btn = ttk.Button(self, text="Baixar", command=self._start_download)
        self._btn.pack(pady=(16, 0))

    def _pick_dir(self):
        folder = filedialog.askdirectory(initialdir=self._dir_var.get())
        if folder:
            self._dir_var.set(folder)

    def _format_opts(self):
        fmt = self._fmt_var.get()
        out_tmpl = os.path.join(self._dir_var.get(), "%(title)s.%(ext)s")
        base = {"outtmpl": out_tmpl, "progress_hooks": [self._on_progress], "ffmpeg_location": FFMPEG_PATH}

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
        # best
        return {**base, "format": "bestvideo+bestaudio/best", "merge_output_format": "mp4"}

    def _on_progress(self, d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            self._status_var.set(f"Baixando... {pct}  |  {speed}  |  ETA {eta}")
        elif d["status"] == "finished":
            self._status_var.set("Processando arquivo...")

    def _start_download(self):
        url = self._url_var.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole o link do YouTube primeiro.")
            return
        dest = self._dir_var.get().strip()
        if not os.path.isdir(dest):
            messagebox.showerror("Erro", "Pasta de destino não existe.")
            return

        self._btn.state(["disabled"])
        self._progress.start(10)
        self._status_var.set("Iniciando download...")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        try:
            with yt_dlp.YoutubeDL(self._format_opts()) as ydl:
                ydl.download([url])
            self.after(0, self._done, True, None)
        except Exception as exc:
            self.after(0, self._done, False, str(exc))

    def _done(self, success, error):
        self._progress.stop()
        self._btn.state(["!disabled"])
        if success:
            self._status_var.set(f"Concluído! Salvo em: {self._dir_var.get()}")
            messagebox.showinfo("Pronto!", f"Download concluído!\nSalvo em:\n{self._dir_var.get()}")
        else:
            self._status_var.set(f"Erro: {error}")
            messagebox.showerror("Erro no download", error)


if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()
