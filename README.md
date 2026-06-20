# YouTube Downloader

Interface gráfica simples para baixar vídeos e músicas do YouTube no Windows.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Funcionalidades

- Cole qualquer link do YouTube e baixe com um clique
- Escolha a pasta de destino pelo explorador de arquivos
- Selecione o formato de saída:
  - Melhor qualidade disponível (vídeo + áudio)
  - 1080p, 720p ou 480p em MP4
  - Apenas áudio em MP3
- Progresso em tempo real: porcentagem, velocidade e tempo restante
- **100% standalone** — ffmpeg embutido, nenhuma instalação adicional necessária

---

## Download

Baixe o executável pronto na página de [Releases](../../releases/latest) e execute diretamente. Não requer Python nem nenhuma dependência instalada.

---

## Como usar

1. Abra o `YouTube Downloader.exe`
2. Cole o link do vídeo no campo **Link do YouTube**
3. Clique em `...` para escolher a pasta onde salvar (padrão: `Downloads`)
4. Escolha o formato desejado
5. Clique em **Baixar**

---

## Compilar do código fonte

Requer Python 3.10 ou superior.

```bash
# Instalar dependências
pip install yt-dlp imageio-ffmpeg pyinstaller

# Gerar o executável
pyinstaller --onefile --windowed --name "YouTube Downloader" --collect-all imageio_ffmpeg ytdl_gui.py
```

O arquivo gerado estará em `dist/YouTube Downloader.exe`.

---

## Tecnologias

| Biblioteca | Função |
|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Download e extração de vídeos |
| [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | FFmpeg embutido (mescla vídeo/áudio, converte MP3) |
| [tkinter](https://docs.python.org/3/library/tkinter.html) | Interface gráfica |
| [PyInstaller](https://pyinstaller.org) | Empacotamento em executável único |

---

## Licença

MIT
