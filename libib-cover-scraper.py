import requests
import shutil
from bs4 import BeautifulSoup
import os
from os.path import exists
import argparse

image_files_in_existing = []

# Get the names of pre-existing images in the directory
def get_existing_images():
    return os.listdir(args.output)


# Download the image with the book title as its file name
def download_image(image_code, title):
            
    # Reformat the image source to have correct URL
    [front_waste, source] = image_code.split("/")
    url = "https://d23tvywehq0xq.cloudfront.net/" + source

    # Retrieve the image from the provided URL
    image = requests.get(url, stream=True)

    # If the request was sucessful, create the image file
    if image.status_code == 200:
        with open(args.output + title, "xb") as  f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
        print("Downloaded " + title + "...")
    else:
        print("Request Failed")


# Rename the image files in the sibling folder containing the previously downloaded images
def rename_image_files(image_code, title):

    # Reformat the image source to have the correct file name
    [front_waste, source] = image_code.split("/")
    existing_image_file_name = args.folder + source
    new_image_file_name = args.folder + title

    image_files_in_existing.append(new_image_file_name)

    if exists(existing_image_file_name):
        os.rename(existing_image_file_name, new_image_file_name)
        print("Successfully renamed image file associated with " + title + "...")
    elif exists(new_image_file_name):
        print(title + " already exists...")
    else:
        print("Couldn't find file image file associated with " + title + "...")


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

            # Get the title from the title tag
            title = get_final_title(title_tag)

            # Take appropriate action based on the value of should_download
            if args.download:
                download_image(image_code, title)
            else:
                rename_image_files(image_code, title)


# Open an HTML file and create a parsed soup
def create_soup():

    # Import the html file
    page = open("./libib_page.html").read()

    # Parse it and create a soup
    return BeautifulSoup(page, "html.parser")


# If the provided directory names don't end with a forward slash, add one
def format_dirs():
    if args.output is not None and args.output[-1] != "/":
        args.output += "/"

    if args.folder is not None and args.folder[-1] != "/":
        args.folder += "/"

        
# Initialize command line argument parser
def create_command_line_parser():
    parser = argparse.ArgumentParser(
        prog="Libib Cover Scraper",
        description="Create a folder of titled images from an online Libib library")

    parser.add_argument("-o", "--output", help = "Define output folder when downloading the images")
    parser.add_argument("-f", "--folder", help = "Define folder containing image files when not needing to download")
    parser.add_argument("-d", "--download", help = "Define whether to download the images or rename images in an existing folder", action="store_true")

    return parser


args = create_command_line_parser().parse_args()
format_dirs()

get_titles_and_image_files(create_soup())

if args.download is False:
    for file in os.listdir(args.folder):
        if (args.folder + file) not in image_files_in_existing:
            os.remove(args.folder + file)
            print("Removed file " + file)