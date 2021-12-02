from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd

s = requests.Session()
retry = Retry(connect=10, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
s.mount('http://', adapter)
s.mount('https://', adapter)

page = 1
url = 'https://budaya-indonesia.org'
allResult = list()
while True:
    home = s.get('{}/cari?element=3&page={}'.format(url,page))
    if home.status_code!=200:
        print('error request 1 {} | {}'.format(page,home.status_code))

    else:
        soup = BeautifulSoup(home.content, "html.parser")
        tables = soup.find('div',{'class':'hasil-search'}).find_all('table')
        if len(tables)==0:
            print('finish')
            break
        else:
            for table in tables:
                link = table.find('td').find('a')['href']
                detail = s.get(link)
                if detail.status_code!=200:
                    print('error request 2 {} | {}'.format(link,detail.status_code))

                else:
                    result = dict()
                    soup = BeautifulSoup(detail.content, "html.parser")
                    content = soup.find_all('div',{'class':'card-body'})
                    result['nama'] = table.find('td').find('a').find('b').text
                    result['kategori'] = content[0].text.strip().split('\n')[-1].strip()
                    result['elemen_budaya'] = content[1].text.strip().split('\n')[-1].strip()
                    result['provinsi'] = content[2].text.strip().split('\n')[-1].strip()
                    result['asal_daerah'] = content[3].text.strip().split('\n')[-1].strip()
                    result['deskripsi'] = content[4].text.strip()
                    result['link'] = link
                    try:
                        result['image'] = content[4].find('img')['src']
                    except:
                        result['image'] = ''
                        
                allResult.append(result)
    page=page+1

df = pd.DataFrame(allResult)
df.to_csv('budayaindonesia.csv',index=False)
