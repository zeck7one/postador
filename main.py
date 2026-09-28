import os
import time
import telebot
from telebot import apihelper
from dotenv import load_dotenv

load_dotenv()
#-1004382507494
#C:\Users\zeck0\OneDrive\Documents\Desktop\job\previas\test```python
import os
import time
import telebot
from telebot import apihelper
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Quantidade de uploads acontecendo ao mesmo tempo
MAX_UPLOADS_SIMULTANEOS = 2

# Tempo máximo para operações HTTP
TIMEOUT = 300

# Quantidade de tentativas para cada vídeo
MAX_TENTATIVAS = 3


# ============================================================
# CONFIGURAÇÃO DO TELEGRAM
# ============================================================

apihelper.CONNECT_TIMEOUT = TIMEOUT
apihelper.READ_TIMEOUT = TIMEOUT

bot = telebot.TeleBot(BOT_TOKEN)


# ============================================================
# ENVIAR VÍDEO
# ============================================================

def enviar_video(caminho, canal, numero, total):

    nome = os.path.basename(caminho)

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:

            print(
                f"[{numero}/{total}] "
                f"📤 {nome} | "
                f"Tentativa {tentativa}/{MAX_TENTATIVAS}"
            )

            with open(caminho, "rb") as video:

                bot.send_video(
                    chat_id=canal,
                    video=video,
                    supports_streaming=True,
                    timeout=TIMEOUT
                )

            print(
                f"[{numero}/{total}] "
                f"✅ {nome} enviado!"
            )

            return True, nome

        except Exception as erro:

            print(
                f"[{numero}/{total}] "
                f"⚠️ Erro em {nome}"
            )

            print(f"      {erro}")

            if tentativa < MAX_TENTATIVAS:

                print(
                    f"      ⏳ "
                    f"Tentando novamente em 5 segundos..."
                )

                time.sleep(5)

    print(
        f"[{numero}/{total}] "
        f"❌ Falha definitiva: {nome}"
    )

    return False, nome


# ============================================================
# POSTAR TODOS OS VÍDEOS
# ============================================================

def postar_videos():

    print()
    print("=" * 60)
    print("              📤 POSTADOR DE VÍDEOS")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # PASTA
    # --------------------------------------------------------

    pasta = input(
        "📁 Digite o caminho da pasta dos vídeos: "
    ).strip()

    pasta = pasta.strip('"').strip("'")

    if not os.path.isdir(pasta):

        print()
        print("❌ A pasta não existe.")
        return

    # --------------------------------------------------------
    # ID DO CANAL
    # --------------------------------------------------------

    canal = input(
        "📺 Digite o ID do canal: "
    ).strip()

    try:

        canal = int(canal)

    except ValueError:

        print()
        print("❌ ID do canal inválido.")
        print("Exemplo: -1001234567890")
        return

    # --------------------------------------------------------
    # PROCURAR VÍDEOS
    # --------------------------------------------------------

    print()
    print("🔎 Procurando vídeos...")

    extensoes = (
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm"
    )

    videos = []

    for arquivo in os.listdir(pasta):

        caminho = os.path.join(pasta, arquivo)

        if not os.path.isfile(caminho):
            continue

        if arquivo.lower().endswith(extensoes):

            videos.append(caminho)

    videos.sort()

    # --------------------------------------------------------
    # NENHUM VÍDEO
    # --------------------------------------------------------

    if not videos:

        print()
        print("❌ Nenhum vídeo encontrado.")
        return

    # --------------------------------------------------------
    # INFORMAÇÕES
    # --------------------------------------------------------

    print()
    print("=" * 60)

    print("📁 Pasta:")
    print(pasta)

    print()

    print("📺 Canal:")
    print(canal)

    print()

    print(f"🎬 Vídeos encontrados: {len(videos)}")

    print(
        f"⚡ Uploads simultâneos: "
        f"{MAX_UPLOADS_SIMULTANEOS}"
    )

    print("=" * 60)

    print()

    # --------------------------------------------------------
    # LISTAR VÍDEOS
    # --------------------------------------------------------

    for numero, caminho in enumerate(videos, 1):

        nome = os.path.basename(caminho)

        tamanho = os.path.getsize(caminho)

        tamanho_mb = tamanho / (1024 * 1024)

        print(
            f"{numero:02d}. "
            f"{nome} "
            f"({tamanho_mb:.2f} MB)"
        )

    # --------------------------------------------------------
    # CONFIRMAÇÃO
    # --------------------------------------------------------

    print()

    confirmar = input(
        "🚀 Começar o envio? [S/N]: "
    ).strip().lower()

    if confirmar != "s":

        print()
        print("❌ Operação cancelada.")
        return

    # --------------------------------------------------------
    # ENVIO PARALELO
    # --------------------------------------------------------

    sucesso = []
    falhas = []

    print()
    print("=" * 60)
    print("🚀 INICIANDO ENVIO PARALELO")
    print("=" * 60)
    print()

    total = len(videos)

    # Cria no máximo 2 trabalhadores
    with ThreadPoolExecutor(
        max_workers=MAX_UPLOADS_SIMULTANEOS
    ) as executor:

        tarefas = {}

        # ----------------------------------------------------
        # COLOCA OS VÍDEOS NA FILA
        # ----------------------------------------------------

        for numero, caminho in enumerate(videos, 1):

            tarefa = executor.submit(
                enviar_video,
                caminho,
                canal,
                numero,
                total
            )

            tarefas[tarefa] = caminho

        # ----------------------------------------------------
        # RECEBE OS RESULTADOS
        # ----------------------------------------------------

        for tarefa in as_completed(tarefas):

            try:

                resultado, nome = tarefa.result()

                if resultado:

                    sucesso.append(nome)

                else:

                    falhas.append(nome)

            except Exception as erro:

                caminho = tarefas[tarefa]

                nome = os.path.basename(caminho)

                falhas.append(nome)

                print()
                print(
                    f"❌ Erro inesperado em {nome}"
                )

                print(f"   {erro}")

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("🏁 ENVIO FINALIZADO")
    print("=" * 60)

    print()
    print(f"🎬 Total: {len(videos)}")
    print(f"✅ Sucesso: {len(sucesso)}")
    print(f"❌ Falhas: {len(falhas)}")

    # --------------------------------------------------------
    # VÍDEOS COM ERRO
    # --------------------------------------------------------

    if falhas:

        print()
        print("❌ VÍDEOS QUE NÃO FORAM ENVIADOS:")

        for nome in falhas:

            print(f"   • {nome}")

    # --------------------------------------------------------
    # SUCESSOS
    # --------------------------------------------------------

    if sucesso:

        print()
        print("✅ VÍDEOS ENVIADOS:")

        for nome in sucesso:

            print(f"   • {nome}")

    print()
    print("Programa encerrado.")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    postar_videos()