import requests
from lxml import html

for i in range(1):
    url = f"https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&ILChkBx=yes&Submit=Search&start={25*i}"
    response = requests.get(url)
    # Parse the HTML content using lxml.html
    tree = html.fromstring(response.content)
    # Find all the table rows
    table = tree.xpath("//tr")
    for row in table:
        # Get the text content from each table cell in the row
        data = row.xpath(".//td/text()")
        print(data)
