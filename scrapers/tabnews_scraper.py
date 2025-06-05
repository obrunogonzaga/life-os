import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Artigo:
    titulo: str
    link: str
    comentarios: int
    autor: str
    tempo_postagem: str
    origem: str
    tags: Optional[List[str]] = None


@dataclass
class ArtigoDetalhado:
    titulo: str
    link: str
    autor: str
    tempo_postagem: str
    conteudo_markdown: str
    comentarios: List['Comentario']
    origem: str


@dataclass
class Comentario:
    autor: str
    conteudo: str
    tempo_postagem: str
    respostas: List['Comentario'] = None


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
                tempo_postagem=tempo,
                origem="TabNews",
                tags=None  # Será preenchido futuramente com IA
            )
            artigos.append(artigo)
        
        return artigos
    
    def scrape_artigo_detalhado(self, url: str) -> Optional[ArtigoDetalhado]:
        """
        Scrape detalhes completos de um artigo do TabNews
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair título
            titulo_elem = soup.find('h1')
            titulo = titulo_elem.text.strip() if titulo_elem else "Título não encontrado"
            
            # Extrair autor e tempo
            autor = ""
            tempo_postagem = ""
            
            # Procurar informações do autor e tempo no cabeçalho do artigo
            metadata_sections = soup.find_all(['p', 'div', 'span'])
            for section in metadata_sections:
                text = section.text.strip()
                if "atrás" in text and not tempo_postagem:
                    tempo_postagem = text
                # Procurar por links de usuário para encontrar o autor
                user_links = section.find_all('a')
                for link in user_links:
                    href = link.get('href', '')
                    if href.startswith('/') and href.count('/') == 1 and len(href) > 1:
                        autor = link.text.strip()
                        break
                if autor and tempo_postagem:
                    break
            
            # Extrair conteúdo em markdown
            conteudo_markdown = ""
            
            # O conteúdo no TabNews geralmente está em divs com texto
            # Vamos procurar por parágrafos e texto que não sejam metadados
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote', 'pre', 'code'])
            
            content_lines = []
            titulo_processado = False
            
            for elem in content_elements:
                text = elem.text.strip()
                
                # Pular o título principal
                if not titulo_processado and text == titulo:
                    titulo_processado = True
                    continue
                
                # Pular metadados (autor, tempo, etc.)
                if any(keyword in text.lower() for keyword in ['atrás', 'comentário', 'curtir']):
                    continue
                
                # Pular textos muito curtos ou vazios
                if len(text) < 10:
                    continue
                
                # Converter elementos HTML para formato markdown-like
                if elem.name.startswith('h'):
                    level = int(elem.name[1])
                    content_lines.append(f"{'#' * level} {text}")
                elif elem.name in ['ul', 'ol']:
                    # Para listas, extrair itens
                    items = elem.find_all('li')
                    for item in items:
                        content_lines.append(f"- {item.text.strip()}")
                elif elem.name == 'blockquote':
                    content_lines.append(f"> {text}")
                elif elem.name in ['pre', 'code']:
                    content_lines.append(f"```\n{text}\n```")
                else:
                    content_lines.append(text)
            
            conteudo_markdown = '\n\n'.join(content_lines)
            
            # Extrair comentários
            comentarios = self._extrair_comentarios(soup)
            
            return ArtigoDetalhado(
                titulo=titulo,
                link=url,
                autor=autor,
                tempo_postagem=tempo_postagem,
                conteudo_markdown=conteudo_markdown,
                comentarios=comentarios,
                origem="TabNews"
            )
            
        except Exception as e:
            print(f"Erro ao fazer scraping do artigo {url}: {e}")
            return None
    
    def _extrair_comentarios(self, soup: BeautifulSoup) -> List[Comentario]:
        """
        Extrai comentários da página do artigo
        """
        comentarios = []
        
        # No TabNews, comentários geralmente estão em seções específicas
        # Esta é uma implementação básica - pode precisar de ajustes
        comment_sections = soup.find_all(['div', 'article'])
        
        for section in comment_sections:
            # Procurar por elementos que parecem comentários
            text = section.text.strip()
            
            # Critérios para identificar comentários:
            # - Contém texto substancial
            # - Tem informações de autor/tempo
            # - Não é o conteúdo principal
            
            if len(text) > 50 and any(keyword in text for keyword in ['atrás', 'comentário']):
                # Tentar extrair autor do comentário
                autor_comment = ""
                tempo_comment = ""
                
                links = section.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('/') and href.count('/') == 1:
                        autor_comment = link.text.strip()
                        break
                
                # Extrair tempo
                spans = section.find_all('span')
                for span in spans:
                    span_text = span.text.strip()
                    if 'atrás' in span_text:
                        tempo_comment = span_text
                        break
                
                # Extrair conteúdo do comentário (removendo metadados)
                content_text = text
                if autor_comment:
                    content_text = content_text.replace(autor_comment, '')
                if tempo_comment:
                    content_text = content_text.replace(tempo_comment, '')
                
                # Limpar o texto
                content_text = content_text.strip()
                
                if len(content_text) > 20 and autor_comment:
                    comentario = Comentario(
                        autor=autor_comment,
                        conteudo=content_text,
                        tempo_postagem=tempo_comment,
                        respostas=[]  # Por simplicidade, não implementando respostas aninhadas ainda
                    )
                    comentarios.append(comentario)
        
        # Remover duplicatas e limitar quantidade
        unique_comentarios = []
        seen_content = set()
        
        for comentario in comentarios:
            content_hash = comentario.conteudo[:100]  # Usar primeiros 100 chars como hash
            if content_hash not in seen_content:
                unique_comentarios.append(comentario)
                seen_content.add(content_hash)
        
        return unique_comentarios[:20]  # Limitar a 20 comentários


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
        print(f"  Origem: {artigo.origem}")
        print(f"  Tags: {artigo.tags if artigo.tags else 'Não classificado'}")
        print("-" * 50)


if __name__ == "__main__":
    main()