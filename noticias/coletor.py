import feedparser
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import os
import dateutil.parser
from dateutil.tz import tzutc, tzlocal

# --- Configurações dos Sites ---
CONFIGURACOES = [
    {
        "nome": "G1",
        "rss_url": "https://g1.globo.com/rss/g1/",
        "site_url": "https://g1.globo.com/",
        "seletores": {
            # Seletor de Web Scraping atualizado para a estrutura mais recente do G1
            "noticia_bloco": "div.feed-post-body",
            "titulo": "h2.feed-post-link",
            "link": "a.feed-post-link"
        }
    },
    {
        "nome": "CNN Brasil",
        "rss_url": "https://www.cnnbrasil.com.br/feed/",
        "site_url": "https://www.cnnbrasil.com.br/",
        "seletores": {
            "noticia_bloco": "figcaption a",
            "titulo": "h2",
            "link": ""
        }
    },  
    {  
        "nome": "Jovem Pan", 
        "rss_url": "https://jovempan.com.br/feed", 
        "site_url": "https://jovempan.com.br/",
        "seletores": {
            "noticia_bloco": ".latest-news-list li",
            "titulo": "h3",
            "link": "a"
        }
    },
    {
        "nome": "Folha de S.Paulo",
        "rss_url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
        "site_url": "https://www.folha.uol.com.br/",
        "seletores": {
            "noticia_bloco": ".c-main-headline, .c-headline",
            "titulo": "h2, h3",
            "link": "a"
        }
    },
    {
        "nome": "Exame",
        "rss_url": "https://exame.com/feed/",
        "site_url": "https://exame.com/",
        "seletores": {
            "noticia_bloco": "article",
            "titulo": "h3, h2",
            "link": "a"
        }
    },
    {
        "nome": "Terra",
        "rss_url": "https://www.terra.com.br/rss",
        "site_url": "https://www.terra.com.br/",
        "seletores": {
            "noticia_bloco": ".card-news, .feed-item",
            "titulo": "h2, h3",
            "link": "a"
        }
    },
    {
        "nome": "Veja",
        "rss_url": "https://veja.abril.com.br/feed/",
        "site_url": "https://veja.abril.com.br/",
        "seletores": {
            "noticia_bloco": "a.card-imagem-container",
            "titulo": "h3",
            "link": "a"
        }
    }
]

# --- Lista de User-Agents para Rotação ---
user_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 7077.134.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.156 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16",
    "Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
]

def get_random_user_agent():
    return random.choice(user_agents)

def get_current_time_from_api(api_url="https://api-data-hora-python.onrender.com/data-hora"):
    """
    Chama a API de data e hora para obter a data e hora local.
    Retorna a string de data formatada ou None em caso de erro.
    """
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Lança um erro para códigos de status HTTP ruins
        data = response.json()
        return data.get('data_formatada')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar na API de data e hora: {e}")
        return None

# --- Funções de Captura ---

def capturar_rss(config, data_do_dia):
    """
    Tenta capturar notícias via feed RSS. Se a data da notícia não estiver disponível,
    usa a data e hora fornecidas pela API.
    """
    nome = config["nome"]
    url_rss = config["rss_url"]
    
    if not url_rss:
        print(f"[{nome}] Não há URL de RSS configurada. Pulando...")
        return []

    try:
        print(f"[{nome}] Tentando usar RSS...")
        feed = feedparser.parse(url_rss)
        noticias = []              
        
        if feed.entries:
            for entry in feed.entries[:5]:
                data_publicacao = entry.get('published_parsed')
                if data_publicacao:
                    # Converte a data do feed (assumida como UTC) para o fuso horário local
                    data_utc = datetime(*data_publicacao[:6], tzinfo=tzutc())
                    data_local = data_utc.astimezone(tzlocal())
                    data_formatada = data_local.strftime("%d/%m/%Y %H:%M")
                else:
                    # Se a data não estiver no RSS, usa a data da API
                    data_formatada = data_do_dia

                noticias.append({
                    "titulo": entry.title,
                    "link": entry.link,
                    "data": data_formatada,
                    "fonte": nome,
                    "metodo": "RSS"
                })
            print(f"[{nome}] Sucesso! Notícias encontradas via RSS.")
        return noticias
    except Exception as e:
        print(f"[{nome}] Erro ao processar o feed RSS: {e}")
        return []

def capturar_web_scraping(config, **kwargs):
    """Tenta capturar notícias via Web Scraping."""
    nome = config["nome"]
    url_site = config["site_url"]
    seletores = config["seletores"]
    
    # Obtém a data_atual da variável passada por kwargs, ou usa o fallback
    data_atual = kwargs.get('data_atual')
    if not data_atual:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

    print(f"[{nome}] Tentando usar Web Scraping...")
    try:
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url_site, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        noticias_elementos = soup.select(seletores["noticia_bloco"])
        
        noticias = []
        for elemento in noticias_elementos[:5]:
            if seletores['link']:
                link_elemento = elemento.select_one(seletores['link'])
                titulo_elemento = elemento.select_one(seletores['titulo'])
                link = link_elemento.get('href') if link_elemento else None
                titulo = titulo_elemento.text.strip() if titulo_elemento else None
            else:
                link = elemento.get('href')
                titulo = elemento.find('h2').text.strip() if elemento.find('h2') else None
            
            if titulo and link:
                if not link.startswith('http'):
                    link = url_site + link
                
                noticias.append({
                    "titulo": titulo,
                    "link": link,
                    "data": data_atual,
                    "fonte": nome,
                    "metodo": "Web Scraping"
                })
        
        if noticias:
            print(f"[{nome}] Sucesso! Notícias encontradas via Web Scraping.")
        else:
            print(f"[{nome}] Falha. Nenhum elemento encontrado com o seletor: '{seletores['noticia_bloco']}'")
        
        return noticias
    except Exception as e:
        print(f"[{nome}] Erro ao fazer Web Scraping: {e}")
        return []

def extrair_imagem_da_noticia(url):
    """
    Tenta extrair a URL de uma imagem principal da página da notícia.
    Adicionado delay e timeout para maior robustez.
    Retorna a URL da imagem ou None se não encontrar.
    """
    try:
        # Adiciona um delay aleatório para evitar ser detectado como bot
        time.sleep(random.uniform(1, 3))
        
        headers = {'User-Agent': get_random_user_agent()}
        # Aumenta o timeout para 15 segundos
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
    
        # Tentativas de encontrar a imagem em seletores comuns
        img_tag = soup.select_one('meta[property="og:image"]')
        if img_tag and img_tag.get('content'):
            return img_tag['content']

        img_tag = soup.select_one('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
            
    except Exception as e:
        print(f"Erro ao extrair imagem da URL {url}: {e}")
        return None

# --- Lógica Principal do Bot ---

def main():
    todas_noticias = []

    # Chama a API de data e hora apenas uma vez, no início
    print("Obtendo data e hora da API...")
    data_do_dia = get_current_time_from_api()
    if not data_do_dia:
        print("Falha ao obter data da API. Usando data e hora locais do sistema.")
        data_do_dia = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    for config in CONFIGURACOES:
        # Passa a data e hora obtida para as funções de captura
        noticias_encontradas = capturar_rss(config, data_do_dia)
        
        if not noticias_encontradas:
            # Se RSS falhar, tenta Web Scraping, passando a mesma data
            noticias_encontradas = capturar_web_scraping(config, data_atual=data_do_dia)
            
        # Adiciona a extração da imagem para cada notícia
        for noticia in noticias_encontradas:
            noticia['image'] = extrair_imagem_da_noticia(noticia['link'])
            
        todas_noticias.extend(noticias_encontradas)
        print("-" * 40)

    if todas_noticias:
        print("\n--- Todas as Notícias Coletadas ---")
        for noticia in todas_noticias:
            print(f"Título: {noticia['titulo']}")
            print(f"Link: {noticia['link']}")
            print(f"Data: {noticia['data']}")
            print(f"Fonte: {noticia['fonte']} ({noticia['metodo']})")
            print(f"Imagem: {noticia['image']}")
            print("-" * 20)
    else:
        print("\nNão foi possível coletar notícias de nenhuma fonte.")

    # Garante que a pasta 'noticias' exista
    if not os.path.exists('noticias'):
        os.makedirs('noticias')

    # Salva o arquivo JSON dentro da pasta 'noticias'
    with open('noticias/todas_as_noticias.json', 'w', encoding='utf-8') as f:
        json.dump(todas_noticias, f, ensure_ascii=False, indent=4)
    print("\nAs notícias foram salvas em 'noticias/todas_as_noticias.json'")

if __name__ == "__main__":
    print("Iniciando a coleta de notícias...")
    main()
    print(f"Coleta concluída. O bot irá pausar por 3 horas e depois rodará novamente...")
