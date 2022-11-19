import streamlit as st
import pandas as pd
from streamlit_tags import st_tags
import requests, tldextract
#import json
from bs4 import BeautifulSoup
#from csv import writer

def adScraper(numberOfTimes, listOfKeywords):
    # Specify User Agent
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"}

    # header
    st.subheader("Progress:")
    my_bar = st.progress(0)

    resultDict = {}
    progress = 0

    # Write advertisement elements to csv file
    with open("Scraped_URLs_dataset.csv", "w", encoding='utf-8', newline='') as file:
        #thewriter = writer(file)
        header = ['URL', 'Company', 'Title', 'Product_Description']
        #thewriter.writerow(header)

        for keyword in listOfKeywords:
            # To find reoccurent companies
            companyList = []
            numOfAds = 0
            resultDict[keyword] = {}
            adElements = []
            print(keyword)

            for _ in range(numberOfTimes):
                # Get requests from google search query
                payload = {'q': keyword}
                html = requests.get("https://www.google.com/search?q=", params=payload, headers=headers)
                
                # Check valid request
                status_code = html.status_code
                if status_code == 200:
                    # Create BeautifulSoup object
                    response = html.text
                    soup = BeautifulSoup(response, 'lxml')
                        
                    # Scraping top and bottom advertisements -- Title URL, Company, Product desc
                    print('--------------------------------Advertisements--------------------------------')
                    topBotAds = soup.find(id = 'main')
                    if (topBotAds):
                        # Monitor number of ads for each keyword
                        if len(topBotAds.findAll('div', class_='uEierd')) > 0:
                            numOfAds += 1
                        absolute_top = 0

                        for container in topBotAds.findAll('div', class_='uEierd'):
                            try:
                                advertisementTitle = container.find('div', class_='CCgQ5 MUxGbd v0nnCb aLF0Z OSrXXb').span.text
                            except:
                                advertisementTitle = 'N/A'

                            try:
                                url = container.find('div', class_='v5yQqb jqWpsc').find('span', class_='qzEoUe').text
                                company = tldextract.extract(url).domain

                                # Determine absolute-top, ad positions
                                if company not in companyList:
                                    companyList.append(company)
                                    if absolute_top == 0:
                                        resultDict[keyword][company] = {'absolute-top':1, 'ad':0}
                                    else:
                                        resultDict[keyword][company] = {'absolute-top':0, 'ad':1}
                                else:
                                    if absolute_top == 0:
                                        resultDict[keyword][company]['absolute-top'] += 1
                                    else:
                                        resultDict[keyword][company]['ad'] += 1
                            except:
                                url = 'N/A'
                                company = 'N/A'

                            try:
                                productDesciption = container.find('div', class_='MUxGbd yDYNvb lyLwlc lEBKkf').text
                            except:
                                productDesciption = 'N/A'

                            print(url)
                            print(company)
                            print(advertisementTitle)
                            print(productDesciption)
                            print()
                            absolute_top += 1
                        
                            adElements = [url, company, advertisementTitle, productDesciption]
                            #thewriter.writerow(adElements)
                        
                            progress += (0.5/(len(listOfKeywords)*numberOfTimes))
                            if progress >= 1.0:
                                progress = 1.0
                            my_bar.progress(progress)

                        # Write advertisement source code to html file
                        with open("malignant.html", "w", encoding='utf-8') as file:
                            file.write(str(soup))        

            keys = list(resultDict[keyword].keys())
            for name in ['ad', 'absolute-top']:
                keys.sort(key=lambda k: resultDict[keyword][k][name], reverse=True)

            # Generate resulting dictionary
            resultDict[keyword]['top performers'] = keys
            resultDict[keyword]['total ads'] = numOfAds

    #print(json.dumps(resultDict, indent = 4))

    # success message
    st.success("Keyword scraping completed successfully!")
    return resultDict
    
def jsonToDataFrame(resultDict, listOfKeywords):
    resultList = []
    for keyword in listOfKeywords:
        if (resultDict[keyword]["top performers"] != []):
            for company in resultDict[keyword]["top performers"]:
                percentage = 0
                if resultDict[keyword][company]["ad"] != 0:
                    percentage = round((resultDict[keyword][company]["absolute-top"])/resultDict[keyword][company]["ad"] * 100,1)

                resultList.append(
                    [
                    keyword,
                    company,
                    resultDict[keyword][company]["absolute-top"],
                    percentage,
                    ]
                )
        else:
            resultList.append([keyword,None,0,0])

    df = pd.DataFrame(resultList,columns=["Keyword","Company","absolute-top","Keyword Ads Percentage(%)"])
    return df

# title
st.title(":male-detective: Malicious Advertisements and Threat Detection Automation")

# specify the number of times each keyword scraping is run
numberOfTimes = st.slider('Enter # of times to keyword scrape: ', 1, 100, 10)

listOfKeywords = ['nft', 'cryptocurrency', 'malware']

col1, col2 = st.columns(2)

with col1:
    chosen_keywords = st_tags(
        label="Add keywords here!",
        text="Press enter to add",
        value=listOfKeywords,
        suggestions=['insurance','loans','blockchain'],
        maxtags=10,
        key='aljnf'
    )

with col2:
    st.caption("Current List of Keywords")
    st.write((chosen_keywords))

submitted = st.button("Submit")
if submitted:
    st.write("Scraping for the following keywords:", str(chosen_keywords), 'for ', numberOfTimes, "times.")

    resultDict = adScraper(numberOfTimes, listOfKeywords)
    resultJson = st.json(resultDict)