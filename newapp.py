from flask import Flask, request, render_template
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import requests
import pymongo

app = Flask(__name__)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@app.route("/scrap", methods=["GET", "POST"])
def scrapDetails():
    if request.method == "POST":
        searchString = request.form['content'].replace(" ", "")
        try:
            DEFAULT_CONNECTION_URL = "mongodb://localhost:27017"
            client = pymongo.MongoClient(DEFAULT_CONNECTION_URL)
            dataBase = client["crawlerDB"]
            collection = dataBase["productDetails"]
            allRecords = collection.find()
            reviews = []
            for record in allRecords:
                data = record.get(searchString)
                if data is not None:
                    reviews = data
                    break
            if not len(reviews):
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
                uClient = uReq(flipkart_url)  # requesting the webpage from the internet
                flipkartPage = uClient.read()  # reading the webpage
                uClient.close()  # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
                bigBoxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                # seacrhing for appropriate tag to redirect to the product link
                del bigBoxes[0:3]  # the first 3 members of the list do not contain relevant information, hence deleting
                # them.
                box = bigBoxes[0]  # taking the first iteration (for demo)
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                # extracting the actual product link
                prodRes = requests.get(productLink)  # getting the product page from server
                prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
                commentBoxes = prod_html.find_all('div',
                                                  {'class': "_2wzgFH"})  # finding the HTML section containing the
                # customer table = db[searchString] # creating a collection with the same name as search string. Tables
                # and Collections are analogous. filename = searchString+".csv" #  filename to save the details fw =
                # open(filename, "w") # creating a local file to save the details headers = "Product, Customer Name,
                # Rating, Heading, Comment \n" # providing the heading of the columns' fw.write(headers) # writing first
                # the headers to file
                #  iterating over the comment section to get the details of customer and their comments
                for commentBox in commentBoxes:
                    try:
                        name = commentBox.div.nextSibling.nextSibling.nextSibling.div.find_all("p", {
                            "class": "_2sc7ZR _2V5EHH"})[0].text
                    except:
                        name = 'No Name'
                    try:
                        rating = commentBox.div.div.text
                    except:
                        rating = 'No Rating'
                    try:
                        commentHead = commentBox.div.div.nextSibling.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        custComment = commentBox.div.nextSibling.div.text
                    except:
                        custComment = 'No Customer Comment'
                    # fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",",
                    # ":") + "," + custComment.replace(",", ":") + "\n")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}
                    reviews.append(mydict)  # appending the comments to the review list
                record = {searchString: reviews}
                collection.insert_one(record)
            return render_template('results.html', reviews=reviews)  # showing the review to the user
        except:
            return "Something is wrong"


if __name__ == "__main__":
    app.run(port=8001, debug=True)
