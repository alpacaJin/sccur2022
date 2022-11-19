# Impot libraries
import requests, lxml, json, time, tldextract
from bs4 import BeautifulSoup
from csv import writer

# Specify User Agent to mitigate bot-blocking
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
}

# Example keywords
listOfKeywords = ["nft", "cloud computing services", "malware", "app development", "cryptocurrency", "web design", "web development", "resume building", "infographic maker", "job search sites", "job search", "internship search", "online news", "academic poster template", "video editing software", "photo editing software", "color correction software", "photoshop software", "augmented reality software", "artificial intelligence software", "adobe software"]
numberOfTimes = 10
resultDict = {}

# Write advertisement elements to csv file
with open("Scraped_URLs_dataset.csv", "w", encoding='utf-8', newline='') as file:
    thewriter = writer(file)
    header = ['URL', 'Company', 'Title', 'Product_Description']
    thewriter.writerow(header)

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
                #soup = BeautifulSoup(response, 'lxml')
                soup = BeautifulSoup(response, 'html.parser')
                    
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
                        thewriter.writerow(adElements)

                    # Write advertisement source code to html file
                    with open("malignant.html", "w", encoding='utf-8') as file:
                        file.write(str(soup))        

        keys = list(resultDict[keyword].keys())
        for name in ['ad', 'absolute-top']:
            keys.sort(key=lambda k: resultDict[keyword][k][name], reverse=True)

        # Generate resulting dictionary
        resultDict[keyword]['top performers'] = keys
        resultDict[keyword]['total ads'] = numOfAds

print(json.dumps(resultDict, indent = 4))