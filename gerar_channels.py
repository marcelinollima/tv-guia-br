"""Monta o custom.channels.xml do grabber do iptv-org so' com os canais da lista do Brasil.

Uso: python gerar_channels.py > custom.channels.xml
"""
import json
import re
import sys
import urllib.request
from xml.sax.saxutils import escape, quoteattr

LISTA = "https://iptv-org.github.io/iptv/countries/br.m3u"
GUIAS = "https://iptv-org.github.io/api/guides.json"

# quando o canal aparece em mais de um site, fica o primeiro desta ordem
PREFERENCIA = ["i.mjh.nz", "pluto.tv", "meuguia.tv", "mi.tv", "plex.tv"]


def baixar(url):
    return urllib.request.urlopen(url, timeout=60).read().decode("utf-8")


def prioridade(site):
    return PREFERENCIA.index(site) if site in PREFERENCIA else len(PREFERENCIA)


def main():
    ids = re.findall(r'tvg-id="([^"]+)"', baixar(LISTA))
    guias = json.loads(baixar(GUIAS))

    por_canal = {}
    for g in guias:
        if not g.get("channel"):
            continue
        chaves = [g["channel"]]
        if g.get("feed"):
            chaves.insert(0, f'{g["channel"]}@{g["feed"]}')
        for chave in chaves:
            atual = por_canal.get(chave)
            if atual is None or prioridade(g["site"]) < prioridade(atual["site"]):
                por_canal[chave] = g

    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', "<channels>"]
    achados = 0
    for xmltv_id in dict.fromkeys(ids):
        g = por_canal.get(xmltv_id) or por_canal.get(xmltv_id.split("@")[0])
        if not g:
            continue
        achados += 1
        linhas.append(
            f'  <channel site={quoteattr(g["site"])} lang={quoteattr(g["lang"])} '
            f'xmltv_id={quoteattr(xmltv_id)} site_id={quoteattr(g["site_id"])}>'
            f'{escape(g["site_name"])}</channel>'
        )
    linhas.append("</channels>")
    print("\n".join(linhas))
    print(f"{achados} de {len(set(ids))} canais com guia", file=sys.stderr)


if __name__ == "__main__":
    main()
