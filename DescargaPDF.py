


import requests
from bs4 import BeautifulSoup
import os
import re
from os import listdir
from os.path import isfile, join


def downloading_sentence(url):
    
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')


    
    href = soup.find("object", {"id": "objtcontentpdf"})
    href = href.find("a", href=True)
    href = "https://www.poderjudicial.es" + href["href"]

    
    location = r"ProyectoPSP/PDF"
    
    
    i = requests.get(url=href)
    with open(os.path.join(location, 'sentence.pdf'), 'wb') as f:
        f.write(i.content)

    
    m = re.search('\d\d\d\d\d\d\d\d', href)
    if m:
        name_file = m.group(0)
    name_file = str(name_file) + ".pdf"
    onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
    file = onlyfiles[0]

    
    old_file = os.path.join(location, file)
    new_file = os.path.join(location, name_file)
    os.rename(old_file, new_file)


def main():
    
    url = "https://www.poderjudicial.es/search/AN/openDocument/a5521408b0c85d13a0a8778d75e36f0d/20240404"
    downloading_sentence(url)
    print("Descarga completada. Verifica el directorio para el archivo descargado.")

if __name__ == "__main__":
    main()
