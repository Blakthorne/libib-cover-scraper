import requests
import shutil
from bs4 import BeautifulSoup
import os
import sys

# Get the names of pre-existing images in the directory
def get_existing_images():
    return os.listdir(image_dir_path)


# Download the image with the book title as its file name
def download_image(url, title):

    # Retrieve the image from the provided URL
    image = requests.get(url, stream=True)

    # If the request was sucessful, create the image file
    if image.status_code == 200:
        with open(image_dir_path + title, "xb") as  f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
        print("Downloaded " + title + "...")
    else:
        print("Request Failed")


# Append ` (copy #)` to a filename if it already exists
def create_title_copy(title, existing_images):

    copy_number = 0
    final_title = title

    # Keep increasing the copy number until we get to one that doesn't exist yet
    while final_title in existing_images:
        copy_number += 1
        final_title = title + " (copy " + str(copy_number) + ")"

    return final_title


# Create a compliant and distinct filename for the image based on the book title
def get_final_title(title_tag):

    # Get the current list of images in the directory here instead of earlier
    # so that it's always an up-to-date list.
    # It takes a lot longer this way, but prevents the program from crashing
    existing_images = get_existing_images()

    # Get the text for the book title from the title tag
    # and ake sure the title doesn't contain a forward slash, as that is a forbidden filename character in Linux
    title = title_tag.string.replace("/", "-")

    # If the title already exists, create a numbered copy of it
    if title in existing_images:
        title = create_title_copy(title, existing_images)

    return title


# Find the image and book titles from an HTML soup
def get_titles_and_image_files(soup):

    # Extract all the image tags from the soup
    images = soup.find_all('img')

    # Iterate over all the image tags
    for image in images:

        # Extract the file source and data-join-id for the image
        image_code = image.get('src')
        data_id = image.get('data-join-id')

        # Get the book title associated with the image
        title_tag = soup.find("div", { "class" : "item-title", "data-join-id" : data_id })

        # Make sure both title and image_code are not empty
        if title_tag != "" and title_tag != None and image_code != "" and image_code != None:

            # Reformat the image source to have correct URL
            [front_waste, source] = image_code.split("/")
            url = "https://d23tvywehq0xq.cloudfront.net/" + source

            title = get_final_title(title_tag)

            # Download the image
            download_image(url, title)


# Open an HTML file and create a parsed soup
def create_soup():

    # Import the html file
    page = open("./Libib _ Library management web app.html").read()

    # Parse it and create a soup
    return BeautifulSoup(page, "html.parser")


# Get the directory path the command line argument
def get_dir():

    # Do some error checking on the provided directory argument.
    # If anything is wrong, print an error message and exit the program
    if len(sys.argv) < 2:
        print("Too few arguments given. Please call the program in this format: \"libib-cover-scraper.py dir\"")
        sys.exit()
    if len(sys.argv) > 2:
        print("Too many arguments given. Please call the program in this format: \"libib-cover-scraper.py dir\"")
        sys.exit()
    elif not os.path.exists(sys.argv[1]):
        print("The directory provided does not exist.")
        sys.exit()
    elif len(os.listdir(sys.argv[1])):
        print("The directory provided is not empty. It must be empty.")
        sys.exit()

    # Extract the directory
    dir = sys.argv[1]

    # If the directory doesn't end in a forward slash, add one
    if dir[-1] != "/":
        dir += "/"

    # Return the path to the directory
    return dir

image_dir_path = get_dir()
get_titles_and_image_files(create_soup())