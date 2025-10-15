import os
import csv
from dotenv import load_dotenv
import serpapi

load_dotenv()

API_KEY = os.getenv("SERPAPI_API_KEY")

def get_reviews(data_id, csv_writer):
    """Fetches all reviews for a given place and writes them to a CSV file."""
    all_reviews = []
    place_info = {}
    next_page_token = None

    while True:
        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "hl": "es",
            "api_key": API_KEY,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token

        search = serpapi.search(params)
        results = search.as_dict()

        if "error" in results:
            print(f"Error fetching reviews: {results['error']}")
            return

        if "place_info" in results and not place_info:
            place_info = results.get("place_info", {})

        all_reviews.extend(results.get("reviews", []))

        pagination = results.get("serpapi_pagination", {})
        next_page_token = pagination.get("next_page_token")

        if not next_page_token:
            break

    place_title = place_info.get("title")
    place_overall_rating = place_info.get("rating")

    for review in all_reviews:
        user_info = review.get("user", {})
        response_info = review.get("response", {})
        csv_writer.writerow([
            place_title,
            place_overall_rating,
            user_info.get("name"),
            user_info.get("reviews"),
            user_info.get("photos"),
            review.get("likes"),
            review.get("snippet"),
            review.get("rating"),
            review.get("iso_date"),
            response_info.get("iso_date"),
            response_info.get("snippet"),
        ])

def get_places():
  MAX_PAGES = 1 #6
  ROWS_PER_PAGE = 20
  for page in range(0, MAX_PAGES):
    start = page * ROWS_PER_PAGE
    params = {
      "engine": "google_maps",
      "q": "talleres mecánicos",
      "ll": "@-12.0562172,-76.7971774,10z",
      "api_key": API_KEY,
      "start": start
    }

    search = serpapi.search(params)
    results = search.as_dict()
    for place in results["local_results"]:
      print(place['title'])
      get_reviews(place['data_id'])
def get_places():
    """Searches for places and triggers review extraction for each."""
    MAX_PAGES = 6
    ROWS_PER_PAGE = 20
    with open('reviews.csv', 'w', newline='', encoding='utf-8') as csvfile:
      csv_writer = csv.writer(csvfile)
      # Write header
      csv_writer.writerow([
          'place_title', 'place_overall_rating', 'review_user_name',
          'review_user_total_reviews', 'review_user_total_photos', 'review_likes',
          'review_text', 'review_rating', 'review_date', 'owner_response_date', 'owner_response_text'
      ])
      for page in range(0, MAX_PAGES):
          start = page * ROWS_PER_PAGE
          params = {
              "engine": "google_maps",
              "q": "talleres mecánicos",
              "ll": "@-12.0562172,-76.7971774,10z",
              "api_key": API_KEY,
              "start": start
          }
          search = serpapi.search(params)
          results = search.as_dict()
          for place in results.get("local_results", []):
              print(f"Fetching reviews for: {place['title']}")
              get_reviews(place['data_id'], csv_writer)

get_places()