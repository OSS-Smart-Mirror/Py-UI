import requests

def NewsFromBBC():
    main_url = " https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=4dbc17e007ab436fb66416009dfb59a8"
    open_bbc_page = requests.get(main_url).json()
    articles = open_bbc_page["articles"]
    results = []
    for article in articles:
        yield article["title"]

if __name__ == '__main__':
    print(NewsFromBBC())
