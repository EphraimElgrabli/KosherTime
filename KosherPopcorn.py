from flask import Flask, request, jsonify
import requests
import json
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

EXTERNAL_API_BASE_URL = "https://shows.cf"

# Create a SQLite database and SQLAlchemy setup
engine = create_engine('sqlite:///kosher_cache.db', echo=True)
Base = declarative_base()

# Define a model for the cached kosher levels
class KosherCache(Base):
    __tablename__ = 'kosher_cache'
    imdb_id = Column(String, primary_key=True)
    kosher_level = Column(Integer)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session for database interactions
Session = sessionmaker(bind=engine)
db_session = Session()

# Kosher filter
def kosherFilter(imdb_id):
    # Check the cache first
    cached_kosher_level = db_session.query(KosherCache).filter_by(imdb_id=imdb_id).first()

    if cached_kosher_level is not None:
        return cached_kosher_level.kosher_level

    # If not found in the cache, fetch data from IMDb
    url = f"https://www.imdb.com/title/{imdb_id}/parentalguide"
    response = requests.get(url)

    if response.status_code == 200:
        strainer = SoupStrainer('section', attrs={'id': 'advisory-nudity'})
        soup = BeautifulSoup(response.content, 'lxml', parse_only=strainer)
        severity_divs = soup.find('div', {'class': 'advisory-severity-vote__container ipl-zebra-list__item'})
        section_contents = severity_divs.get_text()
        rating = section_contents.split()[0]

        if rating == "None":
            kosher_level = int(0)
        elif rating == "Mild":
            kosher_level = int(1)
        elif rating == "Moderate":
            kosher_level = int(2)
        elif rating == "Severe":
            kosher_level = int(3)
        else:
            kosher_level = int(3)

        # Cache the kosher level in the database
        db_session.add(KosherCache(imdb_id=imdb_id, kosher_level=kosher_level))
        db_session.commit()

        return kosher_level

    return int(3)


@app.route('/movie/<imdb_id>')
@app.route('/show/<imdb_id>')
def movie_show_loader(imdb_id=None):
    if imdb_id and kosherFilter(imdb_id) <= 0:
        media_type = request.url_rule.rule.split('/')[1]  # Extract the media type from the URL
        external_api_url2 = f"{EXTERNAL_API_BASE_URL}/{media_type}/{imdb_id}"
        headers = {
            'User-Agent': 'Popcorn Time NodeJS'
        }
        try:
            response = requests.get(external_api_url2, headers=headers)
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            return jsonify({'error': 'External API request error', 'message': str(e)}), 500
    else:
        return jsonify({'error': 'IMDb ID not provided'}), 400

@app.route('/', defaults={'u_path': ''}, methods=['GET'])
@app.route("/<string:u_path>")
@app.route('/<path:u_path>')
def proxy_api(u_path):
    endpoint = request.full_path
    print(endpoint)
    kosher_level = 0
    if not endpoint:
        return jsonify({'error': 'Missing "endpoint" parameter in the request'}), 400

    external_api_url = f"{EXTERNAL_API_BASE_URL}{endpoint}"
    headers = {
        'User-Agent': 'Popcorn Time NodeJS'
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(external_api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        filtered_data = []
        for item in data:
            if kosherFilter(item.get("_id")) <= kosher_level and item.get("certification") != "R" and item.get("certification") != "NR":
                filtered_data.append(item)
        return jsonify(filtered_data)
    else:
        return jsonify({'error': 'Failed to fetch data from the external API'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
