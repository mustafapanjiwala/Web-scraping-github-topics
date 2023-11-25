import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


# A Single function to:
# 1.Function to get the list repositories of all the topics.
# 2.Get the list of the top repos from the individual topic pages
# 3.create a CSV file for each topic with the repo info


def scrape_topics():
    topics_url =  "https://github.com/topics"
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    topic_titles=[]
    topic_desc=[]
    topic_urls=[]

    topic_title_tags = soup.find_all('p',{'class':"f3 lh-condensed mb-0 mt-1 Link--primary"})
    topic_desc_tags = soup.find_all('p',{'class':"f5 color-fg-muted mb-0 mt-1"})

    for topic_title_tag in topic_title_tags:
        topic_titles.append(topic_title_tag.text)
    for topic_desc_tag in topic_desc_tags:
        topic_desc.append(topic_desc_tag.text.strip())
    for topic_title_tag in topic_title_tags:
        topic_link_tag = topic_title_tag.parent.get('href')
        topic_urls.append("https://github.com"+topic_link_tag)

    topics_dict={"Title":topic_titles,"Description":topic_desc,"URL":topic_urls}
    return pd.DataFrame(topics_dict)

# Scraping the top repositories of a topic

def get_repo_info(h1_tag,star_tag):
    # Returns the parsed stars about a repository
    def parse_star_count(stars_str):
        stars_str = stars_str.strip()
        if stars_str[-1] == 'k':
            return int(float(stars_str[:-1])*1000)
        return int(stars_str)
    # Returns all the required info about a repository
    a_tags = h1_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = "https://github.com"+a_tags[1].get('href')
    stars = parse_star_count(star_tag.text.strip())
    return username,repo_name,stars,repo_url

# Getting the top 30 repositories of a topic

def get_topic_page(topic_url):
    
    #Download the page
    response = requests.get(topic_url)
    #Check successful response
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    #Parse using Beautiful soup
    topic_soup = BeautifulSoup(response.text, 'html.parser')
    return topic_soup

def get_topic_repos(topic_soup):
    
    #Get the h1 tags containing repo title, repo URL and username
    repo_tags = topic_soup.find_all('h3',{'class':"f3 color-fg-muted text-normal lh-condensed"})
    star_tags = topic_soup.find_all('span',{'id':"repo-stars-counter-star"})
    #Get repo info from the above tags
    topic_repos_dict={
    'username':[],
    'repo_name':[],
    'ratings':[],
    'repo_url':[]
}
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i],star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['ratings'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
    
    return pd.DataFrame(topic_repos_dict)


def scrape_topic(topic_url,topic_name):
    topic_df = get_topic_repos(get_topic_page(topic_url))
    fname = topic_name+".csv"
    newpath = r'D:\Python Samples\Web-scraping-github-topics\scraped_data' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    if os.path.exists(fname):
        print("The file {} already exists. Skipping...".format(fname))
        os.remove(fname)

    topic_df.to_csv(newpath+"\\"+fname,index=None)


# Final function to scrape all the topics
def scrape_topic_repos():
    topic_df = scrape_topics()
    for index,row in topic_df.iterrows():
        scrape_topic(row['URL'],row['Title'])
        print("Scraped {}".format(row['Title']))
    
scrape_topic_repos()
    











