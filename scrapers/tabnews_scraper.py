import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
import re


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
        
        # Procurar por todas as divs que possam conter comentários
        all_divs = soup.find_all('div')
        
        for div in all_divs:
            # Verificar se é um comentário potencial
            # Comentários têm: link de autor, tempo "X atrás", e conteúdo
            
            # Procurar por link de autor (formato /username)
            author_link = None
            links = div.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if href.startswith('/') and href.count('/') == 1 and len(href) > 1:
                    # Verificar se não é um link de navegação comum
                    link_text = link.text.strip()
                    if link_text and not link_text in ['TabNews', 'Recentes', 'Relevantes']:
                        author_link = link
                        break
            
            if not author_link:
                continue
                
            # Procurar por indicador de tempo
            time_text = ""
            time_elements = div.find_all(string=lambda text: text and 'atrás' in text)
            if time_elements:
                time_text = time_elements[0].strip()
            
            if not time_text:
                continue
            
            # Extrair texto do comentário
            comment_text = div.text.strip()
            
            # Filtros para evitar falsos positivos
            # 1. Não deve conter "min de leitura" (indica artigo principal)
            # 2. Não deve conter "Executando verificação de segurança"
            # 3. Não deve ser muito curto
            # 4. Não deve conter certas palavras-chave de navegação
            
            skip_keywords = [
                'min de leitura',
                'Executando verificação de segurança',
                'Carregando publicação patrocinada',
                'ResponderCarregando'
            ]
            
            if any(keyword in comment_text for keyword in skip_keywords):
                continue
            
            # Limpar o texto do comentário
            autor = author_link.text.strip()
            
            # Pegar apenas o texto relevante do comentário
            # Estratégia: encontrar onde termina os metadados e começa o conteúdo real
            clean_text = comment_text
            
            # Remover autor
            clean_text = clean_text.replace(autor, '', 1)
            
            # Encontrar e remover TODAS as ocorrências de padrões de tempo
            # Isso inclui "X horas atrás", "X dias atrás", etc.
            time_patterns = [
                r'\d+\s*segundos?\s*atrás',
                r'\d+\s*minutos?\s*atrás', 
                r'\d+\s*horas?\s*atrás',
                r'\d+\s*dias?\s*atrás',
                r'\d+\s*semanas?\s*atrás',
                r'\d+\s*mes(es)?\s*atrás',
                r'\d+\s*anos?\s*atrás'
            ]
            
            for pattern in time_patterns:
                clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
            
            # Remover "Responder" 
            clean_text = re.sub(r'\bResponder\b', '', clean_text)
            
            # Remover números isolados no início
            clean_text = re.sub(r'^\d+\s*', '', clean_text.strip())
            
            # Se o texto começar com "atrás" (resquício), remover
            words = clean_text.split()
            while words and words[0].lower() in ['atrás', 'atras']:
                words.pop(0)
            clean_text = ' '.join(words)
            
            # Limpar espaços extras
            clean_text = ' '.join(clean_text.split())
            
            # Verificar se o comentário é válido
            if len(clean_text) > 20 and len(clean_text) < 5000:  # Entre 20 e 5000 caracteres
                # Verificar se não é duplicata por conteúdo similar
                is_duplicate = False
                for existing in comentarios:
                    # Comparar primeiros 50 caracteres
                    if existing.conteudo[:50] == clean_text[:50]:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    comentario = Comentario(
                        autor=autor,
                        conteudo=clean_text,
                        tempo_postagem=time_text,
                        respostas=[]
                    )
                    comentarios.append(comentario)
        
        # Limitar a 20 comentários
        return comentarios[:20]


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