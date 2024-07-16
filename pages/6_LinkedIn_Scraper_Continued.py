import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def build_job_url(keywords, job_location):
    b = ['%20'.join(i.split()) for i in keywords]
    keyword = '%2C%20'.join(b)
    link = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location={job_location}"
    return link

def build_articles_url(keywords):
    base_url = 'https://www.linkedin.com/pulse/topics/home/?trk=guest_homepage-basic_guest_nav_menu_articles'
    encoded_keywords = '%20'.join(keywords)  # Encode keywords for URL
    url = f"{base_url}&keywords={encoded_keywords}"
    return url

def build_companies_url(keywords, company_location):
    b = ['%20'.join(i.split()) for i in keywords]
    keyword = '%2C%20'.join(b)
    link = f"https://www.linkedin.com/search/results/companies/?keywords={keyword}&location={company_location}"
    return link

def scrape_job_listings(url, job_count):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    joblist = []
    try:
        divs = soup.find_all('div', class_='base-search-card__info')
    except:
        print("Empty page, no jobs found")
        return pd.DataFrame()

    for item in divs:
        title = item.find('h3').text.strip()
        company = item.find('a', class_='hidden-nested-link')
        location = item.find('span', class_='job-search-card__location')
        parent_div = item.parent
        entity_urn = parent_div['data-entity-urn']
        job_posting_id = entity_urn.split(':')[-1]
        job_url = 'https://www.linkedin.com/jobs/view/' + job_posting_id + '/'

        date_tag_new = item.find('time', class_='job-search-card__listdate--new')
        date_tag = item.find('time', class_='job-search-card__listdate')
        date = date_tag['datetime'] if date_tag else (date_tag_new['datetime'] if date_tag_new else '')

        job = {
            'Title': title,
            'Company': company.text.strip().replace('\n', ' ') if company else '',
            'Location': location.text.strip() if location else '',
            'Date': date,
            'Job URL': job_url,
        }
        joblist.append(job)

    df = pd.DataFrame(joblist)
    return df.head(job_count)

def scrape_linkedin_search_results(url, result_count):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    results = []
    try:
        items = soup.find_all('li', class_='search-result')
    except:
        print("Empty page, no results found")
        return pd.DataFrame()

    for item in items[:result_count]:
        # Parse individual result item
        title = item.find('span', class_='name actor-name').text.strip()
        subtitle = item.find('p', class_='subline-level-1').text.strip()
        link = item.find('a')['href'] if item.find('a') else ''
        description = item.find('p', class_='subline-level-2').text.strip()

        result = {
            'Title': title,
            'Subtitle': subtitle,
            'Link': link,
            'Description': description
        }
        results.append(result)

    df = pd.DataFrame(results)
    return df.head(result_count)

def scrape_linkedin_articles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_listings = soup.find_all('div', {'class': 'content-hub-entity-card-redesign mt-3 mb-4 flex flex-row'})
        articles = []
        for article in article_listings:
            title = article.find('h2', {'class': 'break-words'}).text.strip()
            description = article.find('p', {'class': 'content-description'}).text.strip()
            anchor_tag = article.find('a', class_='min-w-0')
            href_link = anchor_tag['href'] if anchor_tag else ''
            articles.append({
                'Title': title,
                'Description': description,
                'Article Link': href_link
            })
        return pd.DataFrame(articles)
    else:
        print("Failed to fetch article listings.")
        return pd.DataFrame()
    
def scrape_company_listings(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    company_listings = []
    results = soup.find_all('div', class_='oMuTduEsldOHSSxbmbErLMcjOviIDhxHw')

    for result in results:
        name = result.find('div', class_='entity-result__title-text t-16').find('a').text.strip()
        location = result.find('div', class_='entity-result__primary-subtitle t-14 t-black t-normal').text.strip()
        description = result.find('p', class_='entity-result__summary t-12 t-black--light').text.strip()
        company_url = result.find('div', class_='entity-result__title-text t-16').find('a')['href']

        company = {
            'Name': name,
            'Location': location,
            'Description': description,
            'Company URL': company_url
        }
        company_listings.append(company)

    df = pd.DataFrame(company_listings)
    return df
    
def main():
    st.title("LinkedIn Research Data - Part 2")
    st.write ("articles do not have have a straight keyword search the way the otehrs do")

    with st.form(key='linkedin_search_form'):
        st.header("Search Parameters")
        keyword_input = st.text_input(label='Enter Keywords (comma-separated)').split(',')
        location = st.text_input(label='Location', value='North America')
        search_type = st.selectbox(label='Search Type', options=['jobs', 'companies', 'articles'])
        result_count = st.number_input(label='Result Count', min_value=1, value=10, step=1)
        submit = st.form_submit_button(label='Search')

    if submit and keyword_input and location and search_type == 'jobs':
        url = build_job_url(keyword_input, location)
        df = scrape_job_listings(url, result_count)

        if not df.empty:
            st.header(f"{search_type.capitalize()} Search Results")
            st.table(df)

    elif submit and keyword_input and search_type == 'articles':
        url = build_articles_url(keyword_input)
        df = scrape_linkedin_articles(url)

        if not df.empty:
            st.header(f"{search_type.capitalize()} Search Results")
            st.table(df)
        else:
            st.warning("No articles found. Please check your search parameters.")

    elif submit and keyword_input and location and search_type == 'companies':
        url = build_companies_url(keyword_input, location)
        df = scrape_company_listings(url)

        if not df.empty:
            st.header(f"{search_type.capitalize()} Search Results")
            st.table(df)
        else:
            st.warning("No companies found. Please check your search parameters.")

if __name__ == "__main__":
    main()