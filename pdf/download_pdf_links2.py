from __future__ import annotations

import re
from pathlib import Path
from typing import Set

from pypdf import PdfReader
import requests
from typing import Tuple, List
from urllib.parse import quote


PDF_PATH = Path(__file__).parent / "doc.pdf"
URL_RE = re.compile(r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+", re.IGNORECASE)

DOWNLOADS_DIR = Path(__file__).parent / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

def extract_links_with_text_from_annotations(reader: PdfReader) -> List[Tuple[str, str]]:
    results: List[Tuple[str, str]] = []
    for page_num, page in enumerate(reader.pages, start=1):
        annots = page.get('/Annots') or page.get('/Annots', None)
        if not annots:
            continue
        try:
            for annot in annots:
                obj = annot.get_object()
                a = obj.get('/A')
                if a and '/URI' in a:
                    uri = str(a.get('/URI'))
                    text = obj.get('/Contents')
                    if text:
                        results.append((uri, str(text)))
                    else:
                        results.append((uri, ""))
                elif obj.get('/Subtype') == '/Link':
                    a = obj.get('/A')
                    if a and '/URI' in a:
                        uri = str(a.get('/URI'))
                        text = obj.get('/Contents')
                        if text:
                            results.append((uri, str(text)))
                        else:
                            results.append((uri, ""))
        except Exception:
            continue
    return results

def extract_links_with_text_from_text(reader: PdfReader) -> List[Tuple[str, str]]:
    results: List[Tuple[str, str]] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        for m in URL_RE.finditer(text):
            url = m.group(0)
            # Extrae el texto alrededor de la URL (por ejemplo, 40 caracteres antes y después)
            start = max(m.start() - 40, 0)
            end = min(m.end() + 40, len(text))
            context = text[start:end].replace('\n', ' ')
            results.append((url, context))
    return results

def get_links_with_text(reader: PdfReader) -> List[Tuple[str, str]]:
    # Combina enlaces de anotaciones y texto, priorizando el texto si está disponible
    links = {}
    for url, text in extract_links_with_text_from_annotations(reader) + \
        extract_links_with_text_from_text(reader):
        if url not in links or (text and links[url] == ""):
            links[url] = text
    return [(url, links[url]) for url in sorted(links)]

def sanitize_filename(text: str, url: str) -> str:
    # Usa el texto como nombre de archivo, si no está vacío, si no usa el nombre del archivo de la URL
    base = text.strip() or url.split("/")[-1] or "downloaded_file"
    # Elimina caracteres no válidos para nombres de archivo
    base = re.sub(r'[\\/*?:"<>|]', "_", base)
    # Limita la longitud del nombre
    return base[:100]

def main() -> None:
    if not PDF_PATH.exists():
        print(f"Archivo no encontrado: {PDF_PATH}")
        return

    reader = PdfReader(str(PDF_PATH))

    links_with_text = get_links_with_text(reader)

    if not links_with_text:
        print("No se encontraron enlaces en el PDF.")
        return

    print("Enlaces encontrados:")
    i = 0
    for url, text in links_with_text:
        #print(text, url)
        new_url = url
        filename = sanitize_filename(text, url)
        # Maneja redirecciones HTML específicas de OneDrive/SharePoint
        response = requests.get(new_url, timeout=15)
        response.raise_for_status()
        if response.headers.get("Content-Type", "").startswith("text/html"):
            html = response.text
            # Busca la variable FileRef en el HTML (formato: "FileRef": "xyz")
            match_fileleafref = re.search(r'"FileLeafRef"\s*:\s*"([^"]+)"', html)
            if match_fileleafref:
                filename = match_fileleafref.group(1)
            match = re.search(r'".downloadUrl"\s*:\s*"([^"]+)"', html)
            if match:
                new_url = match.group(1)           
                new_url = bytes(new_url, "utf-8").decode("unicode_escape")
                with open("links.txt", "a", encoding="utf-8") as link_file:
                    link_file.write(f"{new_url}\n")
                print(f"{new_url}")
        """ 
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
                }
                #not working
                #response = requests.get(new_url,  headers=headers, timeout=15, allow_redirects=True)
                #response.raise_for_status()
        
        try:
            filepath = DOWNLOADS_DIR / filename
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Descargado: {url} -> {filepath}")
        except Exception as e:
            print(f"Error al descargar {url}: {e}") """
        i += 1

if __name__ == '__main__':
    main()

#https://educorpperu-my.sharepoint.com/personal/renzo_reyes_upc_pe/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Frenzo%5Freyes%5Fupc%5Fpe%2FDocuments%2FStartUPC%202025%2FIdea%20FitBack%2F2025%2D2%2FDise%C3%B1o%20del%20programa%2FEntregables%2FEntregable%2010%20%2D%20Experiment%20Canvas%2002%2Epdf&parent=%2Fpersonal%2Frenzo%5Freyes%5Fupc%5Fpe%2FDocuments%2FStartUPC%202025%2FIdea%20FitBack%2F2025%2D2%2FDise%C3%B1o%20del%20programa%2FEntregables&ga=1
#https://educorpperu-my.sharepoint.com/personal/renzo_reyes_upc_pe/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Frenzo_reyes_upc_pe%2FDocuments%2FStartUPC%202025%2FIdea%20FitBack%2F2025-2%2FDise%C3%B1o%20del%20programa%2FEntregables%2FEntregable%2010%20-%20Experiment%20Canvas%2002.pdf
#                                                                                                                                                                                                                                                                                       FileDirRef": "\u002fpersonal\u002frenzo_reyes_upc_pe\u002fDocuments\u002fStartUPC 2025\u002fIdea FitBack\u002f2025-2\u002fDise\u00f1o del programa\u002fEntregables",