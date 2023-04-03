# death-certificate-project

Project to collect, organize, and transform death certificate data for use in an academic research project.

## Scrape

The data is obtained using a two part web scraper, featuring a browser extension (designed for Firefox), which copies data from the page and into a consistent JSON format and a python script featuring pyautogui to navigate the webpage and save the data into series of files.

## Load

load_death_certs.py provides the facility to load the created JSON files into an available CouchDB document database, simultaneously providing an initial pass of data regularization. 

## Clean

dedup.py implements some wrappers around the CouchDB API to provide reuseable ability to search and update records in the database, as well as functionality to interactively clean up key fields in the database. Namely, given a file of suspected death date/name duplicates in the database, main() provides a facility for quickly comparing records to determine if they are truly duplicates, and deleting duplicated records. Additionally get_suggestions() provides the core functionality to use fuzzy matching to standardize the spelling of any of the free text fields in the data, by comparing the distinct values of a variable with a set of known good responses. This was used to reduce the number of distinct spellings of cities where individuals died from tens of thousands to fewer than one hundred, which could then be reliably filtered against.

For birthplaces, there was significantly more variety, requiring a more powerful approach. categorize.py defines a LocationForest tree structure which allows a user to progressively build a hierarchy of valid locations by using regular expressions to progressively categorize the uncategorized locations into new or existing leaves of the tree, starting with the most popular labels from the database in order to get the most value possible for a given effort put into categorizing.

uploadDC.zsh was used to associate images of death certificate records with their corresponding records in the database for easy availability.
