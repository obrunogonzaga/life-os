import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List


@dataclass
class Artigo:
    titulo: str
    link: str
    comentarios: int
    autor: str
    tempo_postagem: str


class TabNewsScraper:
    def __init__(self):
        self.base_url = "https://www.tabnews.com.br"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_artigos(self) -> List[Artigo]:
        response = requests.get(self.base_url, headers=self.headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        artigos = []
        
        # Encontrar todos os articles
        for article in soup.find_all('article'):
            # Título e link (dentro de um link <a>)
            titulo_elem = article.find('a')
            titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
            link = self.base_url + titulo_elem.get('href', '') if titulo_elem else ""
            
            # Buscar o autor - é o segundo link dentro do article
            autor = ""
            all_links = article.find_all('a')
            if len(all_links) > 1:
                # O segundo link geralmente é o autor (primeiro é o título)
                autor_link = all_links[1]
                if autor_link.get('href', '').startswith('/') and autor_link.get('href', '').count('/') == 1:
                    autor = autor_link.text.strip()
            
            # Informações do artigo (comentários, tempo)
            info_spans = article.find_all('span')
            
            comentarios = 0
            tempo = ""
            
            for span in info_spans:
                text = span.text.strip()
                
                # Identificar comentários (contém "comentário" ou "comentários")
                if "comentário" in text:
                    try:
                        comentarios = int(text.split()[0])
                    except:
                        comentarios = 0
                # Identificar tempo (contém "atrás")
                elif "atrás" in text:
                    tempo = text
            
            artigo = Artigo(
                titulo=titulo,
                link=link,
                comentarios=comentarios,
                autor=autor,
                tempo_postagem=tempo
            )
            artigos.append(artigo)
        
        return artigos


def main():
    scraper = TabNewsScraper()
    
    print("Fazendo scraping do TabNews...\n")
    artigos = scraper.scrape_artigos()
    
    print(f"Total de artigos encontrados: {len(artigos)}\n")
    
    for i, artigo in enumerate(artigos, 1):
        print(f"Artigo {i}:")
        print(f"  Título: {artigo.titulo}")
        print(f"  Link: {artigo.link}")
        print(f"  Autor: {artigo.autor}")
        print(f"  Comentários: {artigo.comentarios}")
        print(f"  Postado: {artigo.tempo_postagem}")
        print("-" * 50)


if __name__ == "__main__":
    main()