import time
import mss
import pytesseract
from PIL import Image
from datetime import datetime
from collections import Counter
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

# ------------------- Configurações -------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

INTERVALO = 5            # segundos entre capturas
TOTAL_CAPTURAS = 5       # número de capturas
ARQUIVO_PDF = r"C:\Users\Cliente\Desktop\IA teste\Relatorio_Tela.pdf"
TEMP_IMG_DIR = r"C:\Users\Cliente\Desktop\IA teste\capturas_temp"

# Criar pasta temporária se não existir
os.makedirs(TEMP_IMG_DIR, exist_ok=True)

# ------------------- Funções -------------------
def capturar_texto(indice):
    try:
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            # Salva a imagem temporariamente
            img_path = os.path.join(TEMP_IMG_DIR, f"captura_{indice+1}.png")
            img.save(img_path)

            # OCR em inglês (funciona sem instalar idioma extra)
            texto = pytesseract.image_to_string(img, lang="eng")
            
            # Limpeza de texto: remove linhas curtas ou caracteres sem sentido
            linhas = [linha.strip() for linha in texto.split('\n') if len(linha.strip()) > 1 and re.search(r'\w', linha)]
            texto_limpo = '\n'.join(linhas) if linhas else "(Nenhum texto reconhecido)"
            
        return texto_limpo, img_path
    except Exception as e:
        print(f"[!] Erro na captura: {e}")
        return "(Erro na captura)", None

def gerar_pdf(dados, estatisticas):
    doc = SimpleDocTemplate(ARQUIVO_PDF, pagesize=A4)
    estilos = getSampleStyleSheet()
    conteudo = []

    # ----------------- Resumo -----------------
    conteudo.append(Paragraph("📄 Relatório de Captura de Tela", estilos["Title"]))
    conteudo.append(Spacer(1, 12))
    conteudo.append(Paragraph(f"Total de capturas: {TOTAL_CAPTURAS}", estilos["Normal"]))
    conteudo.append(Paragraph(f"Capturas com texto válido: {estatisticas['capturas_validas']}", estilos["Normal"]))
    conteudo.append(Paragraph("Palavras mais frequentes:", estilos["Normal"]))

    for palavra, cont in estatisticas['palavras_frequentes']:
        conteudo.append(Paragraph(f"{palavra}: {cont}", estilos["Normal"]))
    conteudo.append(Spacer(1, 24))

    # ----------------- Capturas detalhadas -----------------
    for i, entrada in enumerate(dados):
        conteudo.append(Paragraph(f"📸 Captura {i+1} - {entrada['hora']}", estilos["Heading4"]))
        if entrada['imagem']:
            # Redimensiona imagem para caber na página
            try:
                img = Image.open(entrada['imagem'])
                max_width = 400
                max_height = 300
                width, height = img.size
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                conteudo.append(RLImage(entrada['imagem'], width=new_width, height=new_height))
            except Exception as e:
                conteudo.append(Paragraph(f"[Erro ao carregar imagem: {e}]", estilos["Normal"]))
        conteudo.append(Paragraph(entrada['texto'].replace("\n", "<br/>"), estilos["Normal"]))
        conteudo.append(Spacer(1, 12))

    doc.build(conteudo)
    print(f"[✔] Relatório salvo em {ARQUIVO_PDF}")

def analisar_estatisticas(dados):
    todas_palavras = []
    capturas_validas = 0
    for entrada in dados:
        if entrada['texto'] != "(Nenhum texto reconhecido)" and entrada['texto'] != "(Erro na captura)":
            capturas_validas += 1
            palavras = re.findall(r'\w+', entrada['texto'])
            todas_palavras.extend(palavras)
    palavras_frequentes = Counter(todas_palavras).most_common(10)
    return {'capturas_validas': capturas_validas, 'palavras_frequentes': palavras_frequentes}

# ------------------- Execução principal -------------------
def main():
    dados = []

    for i in range(TOTAL_CAPTURAS):
        print(f"📸 Captura {i+1}/{TOTAL_CAPTURAS}...")
        texto, img_path = capturar_texto(i)
        dados.append({
            "hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "texto": texto,
            "imagem": img_path
        })
        time.sleep(INTERVALO)

    estatisticas = analisar_estatisticas(dados)
    gerar_pdf(dados, estatisticas)

    # Opcional: apagar imagens temporárias
    # for entrada in dados:
    #     if entrada['imagem']:
    #         os.remove(entrada['imagem'])

if __name__ == "__main__":
    main()
