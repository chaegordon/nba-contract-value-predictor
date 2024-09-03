import requests
from lxml import html
import pandas as pd
import time
import tqdm


end_index = int(39825 / 25)

data_rows = []
for i in tqdm.tqdm(range(end_index + 1)):
    time.sleep(1)
    url = f"https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=&EndDate=&ILChkBx=yes&Submit=Search&start={25*i}"
    response = requests.get(url)
    # Parse the HTML content using lxml.html
    tree = html.fromstring(response.content)
    # Find all the table rows
    table = tree.xpath("//tr")
    for j, row in enumerate(table):
        if j == 0 and i == 0:
            # Get the text content from each table cell in the row
            header = row.xpath(".//td/text()")
            # cut out " • " from the text
            header = [k.replace("\xa0", "") for k in header]
        elif j == 0:
            # ignore first row
            continue
        # elif if last row
        elif j == len(table) - 1:
            # ignore last row
            continue

        else:
            # Get the text content from each table cell in the row
            data = row.xpath(".//td/text()")
            # cut out " • " from the text
            data = [i.replace(" • ", "") for i in data]
            data_rows.append(data)

# build pandas df
df = pd.DataFrame(data_rows, columns=header)
df.to_csv("injuries.csv", index=False)
