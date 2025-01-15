import requests
from bs4 import BeautifulSoup
import csv
import constants

def digest_news() -> None:
    with open(constants.output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["EMPRESA", "TÍTULO", "DATA", "URL", "TEXTO"])

        for empresa in constants.empresas:
            print(f"\nBuscando notícias para: {empresa}")
            search_url = f"{constants.base_url}{empresa}/"  
            response = requests.get(search_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                articles = soup.find_all('span', class_='hl-title hl-title-2')

                if not articles:
                    print(f"Nenhuma notícia encontrada para {empresa}.")
                    continue

                for article in articles[:10]:
                    link_tag = article.find('a')
                    if not link_tag or 'href' not in link_tag.attrs:
                        continue

                    article_url = link_tag['href']
                    article_title = link_tag['title']

                    
                    article_response = requests.get(article_url)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')

                        
                        title_tag = article_soup.find('h1')
                        title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"

                        
                        date_tag = article_soup.find('time')
                        date = date_tag.get_text(strip=True) if date_tag else "Data não encontrada"

                        
                        body_tag = article_soup.find('article', class_='im-article clear-fix')  # Atualizar a classe conforme necessário
                        body = body_tag.get_text(strip=True) if body_tag else "Texto não encontrado"

                        
                        writer.writerow([empresa, title, date, article_url, body])

                        print(f"Título: {title}")
                        print(f"Data: {date}")
                        print(f"URL: {article_url}")
                        print(f"Texto: {body[:200]}...")  
                        print("=" * 50)
                    else:
                        print(f"Erro ao acessar a página da notícia: {article_url} - Status {article_response.status_code}")
            else:
                print(f"Erro ao acessar a busca para {empresa}: {response.status_code}")