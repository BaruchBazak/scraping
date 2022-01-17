import requests
from bs4 import BeautifulSoup as bs
import pymongo

html = requests.get("http://books.toscrape.com/").content
soup = bs(html, "html.parser")


def scrap_zaner_links():
    links_by_zaner = []
    all_zaner = soup.find_all("ul", class_="nav nav-list")
    with open("./links", "w") as fw:
        fw.write(str(all_zaner))
    with open("./links", "r") as fr:
        fr = fr.readlines()
        for i in fr:
            if "href" in i:
                link = i.split('"')
                links_by_zaner.append(link[1])
    return links_by_zaner


def get_prices(soup):
    prices = []
    prices_list = soup.find_all("p", {"class": "price_color"})
    for i in prices_list:
        prices.append(i.text)
    return prices


def get_names(soup):
    all_names = []
    names = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
    for i in names:
        for text in i.find_all("h3"):
            for name in text.find_all("a"):
                all_names.append(name["title"])
    return all_names


def next_page(soup, url, page):
    pages = soup.find_all("li", class_="next")
    if len(pages) == 1:
        a = pages[0].find_all("a", href=True)
        if url[-5:-10] == "index":
            page += 1
            next_page_url = url[:-10] + "page-{0}.html".format(page)
            return next_page_url
        else:
            page += 1
            next_page_url = url[:-10] + "page-{0}.html".format(page)
            return next_page_url
    else:
        return False
#        requests.get(url)
#        print(pages)


def main():
    full_info = []
    all_names = []
    all_prices = []
    data = {""}
    url = "http://books.toscrape.com/"
    html = requests.get(url).content
    soup = bs(html, "html.parser")
    url_by_zaner = scrap_zaner_links()
    full_links = [url + i for i in url_by_zaner]
    for i in range(1, len(full_links)):
        html = requests.get(full_links[i]).content
        soup = bs(html, "html.parser")
        names = get_names(soup)
        all_names += names
        prices = get_prices(soup)
        all_prices += prices
        page = 1
        next_page_url = next_page(soup, full_links[i], page)
        while next_page_url != False:
            html = requests.get(next_page_url).content
            soup = bs(html, "html.parser")
            names = get_names(soup)
            prices = get_prices(soup)
            all_names += names
            all_prices += prices
            page += 1
            next_page_url = next_page(soup, full_links[i], page)

    for i in range(1, len(all_names) + 1):
        full_info.append({"_id":i, "name": all_names[i - 1], "price": all_prices[i - 1]})

    myclient = pymongo.MongoClient(
        "mongodb+srv://baruch:XXXpasswordXXX@cluster0.mfa9n.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    mydb = myclient["mydatabase"]
    print(myclient.list_database_names())
    dblist = myclient.list_database_names()
    if "mydatabase" in dblist:
        print("The database exists.")

    mycol = mydb["books"]
    x = mycol.insert_many(full_info)
    print(x)


if __name__ == '__main__':
    main()
