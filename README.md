# Overview

This is a Python-based Flask application that serves as a proxy API for Popcorn Time. It filters movie and show data based on a "kosher" level, preventing content with certain advisory ratings from being displayed. The application also caches kosher levels in a SQLite database to improve performance and reduce external API requests. It's a useful tool for those who want to filter out content based on parental guidance ratings.

## Features

Filters movies and shows based on their "kosher" level, which is determined by parental guidance ratings from IMDb.
Caches kosher levels in a local SQLite database to reduce the need for repetitive API requests to IMDb.
Provides a proxy API to interact with the Popcorn Time API and filter results based on kosher levels.
Supports two main routes: /movie/<imdb_id> and /show/<imdb_id>, and a generic proxy route for other API requests.

## Technology Stack

* Flask: A Python web framework used for building the API.
* SQLite: A lightweight, serverless database for caching kosher levels.
* Beautiful Soup: A Python library for web scraping, used to extract parental guidance ratings from IMDb.
* SQLAlchemy: A SQL toolkit and Object-Relational Mapping (ORM) library used for interacting with the SQLite database.
* Requests: A Python library for making HTTP requests to external APIs.
* Popcorn Time API: An external API used for retrieving movie and show data.
* LXML: A library for processing XML and HTML documents, used by Beautiful Soup for parsing HTML content.

## How It Works

The application starts by defining a Flask web server and sets up a SQLite database to cache kosher levels.
When a request is made to the /movie/<imdb_id> or /show/<imdb_id> endpoint, the kosherFilter function is called. This function checks if the kosher level for the given IMDb ID is cached in the database. If it is, it returns the cached value. If not, it scrapes the IMDb website for the parental guidance rating, calculates the kosher level, and caches it in the database before returning the result.
If the kosher level is less than or equal to 0, the application makes an external API request to retrieve movie or show data from Popcorn Time. The data is filtered based on the kosher level and the movie's certification rating (e.g., "R" or "NR").
The filtered data is then returned as a JSON response to the client.
The application also provides a generic proxy route (/ and /<u_path>) for making requests to external APIs through Popcorn Time's API. It filters the results based on kosher levels and certification ratings before returning the data to the client.

## Note
IMDb parental guidance ratings are used to determine kosher levels. If these ratings are not available or inaccurate, the filtering may not work correctly.
This application is a tool to filter content based on parental guidance, but it should not be used as a sole means of content control. Parental discretion is advised, and ratings from external sources may be more accurate and comprehensive.
Always respect content copyrights and adhere to the terms of use of external APIs when using this application.
Be aware of web scraping policies and consider adding appropriate error handling and rate limiting for external API requests.
