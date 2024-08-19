# Libib Cover Scraper

The [Libib](https://www.libib.com/) library management software has a data export option, but it does not include the book covers included in the collection. This program provides a way to download those cover images and name them with the title of their respective book titles.

## Downloading the HTML

Since the Libib library collection page is behind a login, it's just easier to go to your personal collection and download the page as an HTML file (this also downloads the images).

    1. Log into Libib and go to your library page.
    2. Scroll down to the bottom of your collection. Since Libib lazy loads the items on the page, if you download the page without doing this, only a partial set of your collection will be downloaded.
    3. Right-click anywhere on the page and click `Save Page As...` Then choose a name and select a location for your download.

## Running the Program

There are two ways to use the program-

    1. Rename the downloaded images with their respective book titles
    2. Download the files from Libib's cdn into another folder (I mainly just included this for fun—the other option is better)

View the program's help page by running it with the `-h` option.