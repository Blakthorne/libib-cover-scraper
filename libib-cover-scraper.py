import requests
import shutil
from bs4 import BeautifulSoup
import os
from os.path import exists
import argparse

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

    if exists(existing_image_file_name):
        os.rename(existing_image_file_name, new_image_file_name)
        print("Successfully renamed image file associated with " + title + "...")
    elif exists(new_image_file_name):
        print(title + " already exists...")
    else:
        print("Couldn't find file image file associated with " + title + "...")


# Append ` (copy #)` to a filename if it already exists
def create_title_copy(title, existing_titles):

    copy_number = 0
    final_title = title

    # Keep increasing the copy number until we get to one that doesn't exist yet
    while final_title in existing_titles:
        copy_number += 1
        final_title = title + " (copy " + str(copy_number) + ")"

    return final_title


# Create a compliant and distinct filename for the image based on the book title
def get_final_title(title_tag, titles_dict):

    # Get the text for the book title from the title tag
    # and ake sure the title doesn't contain a forward slash, as that is a forbidden filename character in Linux
    title = title_tag.string.replace("/", "-")

    # If the title already exists, create a numbered copy of it
    if title in titles_dict.values():
        title = create_title_copy(title, titles_dict.values())

    return title


# Remove files that were downloaded with the html page
# that aren't book cover images so the directory isn't bloated
def remove_extra_files(titles_dict):

    # Iterate over all the files in the directory
    for file in os.listdir(args.folder):

        # If the file doesn't have a book title for a name, remove it
        if (file) not in titles_dict.values():
            os.remove(args.folder + file)
            print("Removed file " + file)


# Find the image and book titles from an HTML soup
def get_titles_and_image_files(soup):

    # Create the dictionary that will hold image code and title pairs
    titles_dict = {}

    # Extract all the image tags from the soup
    images = soup.find_all('img')

    print("Extrapolating book titles...")

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
            title = get_final_title(title_tag, titles_dict)

            titles_dict[image_code] = title

    # Return the dictionary
    return titles_dict


# Open an HTML file and create a parsed soup
def create_soup():

    # Import the html file
    page = open(args.input).read()

    # Parse it and create a soup
    return BeautifulSoup(page, "html.parser")


# If the provided directory names don't end with a forward slash, add one
def format_dirs():

    if args.output is not None and args.output[-1] != "/":
        args.output += "/"

    if args.folder is not None and args.folder[-1] != "/":
        args.folder += "/"

    return args

        
# Initialize command line argument parser
def create_command_line_parser():
    parser = argparse.ArgumentParser(
        prog="Libib Cover Scraper",
        description="Create a folder of titled images from an online Libib library")

    parser.add_argument("input", help = "Required Path to the HTML file from which to extract book titles")
    parser.add_argument("-d", "--download", help = "Provide this option if wanting to download the images", action="store_true")
    parser.add_argument("-o", "--output", help = "If the download flag is provided, define the images download folder")
    parser.add_argument("-f", "--folder", help = "Folder containing image files when not wanting to download")
    parser.add_argument("-r", "--remove", help = "Provide this option if wanting to remove the HTML file after completion", action="store_true")

    return parser

# Parse command line arguments
args = create_command_line_parser().parse_args()

# Make sure that directories are in the correct format
format_dirs()

# Create the dictionary associating image codes and book titles
titles_dict = get_titles_and_image_files(create_soup())

# Take appropriate action based on the value of `download`
if args.download:
    for image_code in titles_dict.keys():
        download_image(image_code, titles_dict[image_code])
    print("\nFinished downloading files...\n")
else:
    for image_code in titles_dict.keys():
        rename_image_files(image_code, titles_dict[image_code])
    print("\nFinished renaming files...\n")

# If we renamed existing files, clean up the directory
if args.download is False:
    remove_extra_files(titles_dict)
    print("\nFinished removing extra files...\n")

# Remove the HTML file if desired
if args.remove is True:
    os.remove(args.input)
    print("Removed HTML file...")