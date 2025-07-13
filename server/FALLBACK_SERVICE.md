# Fallback Service with Reddit Scraping

This service implements the complete fallback logic for searching places with automatic Reddit review scraping.

## Overview

The fallback service follows this logic:

1. **Search Database**: First check existing database for places matching criteria
2. **Check Threshold**: If ≥ 5 results found, return them directly
3. **Fallback Logic**: If < 5 results:
   - Fetch additional places from TomTom API
   - Scrape Reddit reviews for each new place
   - Store places with reviews in database
   - Return combined results

## New Endpoint

### POST `/api/fallback/search`

Searches for places with automatic fallback and Reddit review scraping.

#### Request Body (JSON)
```json
{
    "city": "Delhi",
    "category": "cafe",
    "vibe_tags": ["aesthetic"],
    "min_results": 5
}
```

#### Parameters
- `city` (required): City to search in (e.g., "Delhi", "Mumbai")
- `category` (required): Category to search for (e.g., "cafe", "restaurant", "park")
- `vibe_tags` (optional): Array of vibe tags to match (e.g., ["aesthetic", "cozy"])
- `min_results` (optional): Minimum results required before fallback (default: 5)

#### Response
```json
{
    "success": true,
    "message": "Found 7 places",
    "source": "database_and_tomtom",
    "places": [
        {
            "original": {
                "fsq_id": "tomtom_cafe_1",
                "name": "TomTom Coffee Shop 1",
                "category": "Coffee Shop",
                "address": "101 Main Street, Delhi",
                "locality": "Delhi",
                "city": "Delhi",
                "country": "India",
                "photo_url": "https://...",
                "coordinates": {
                    "type": "Point",
                    "coordinates": [77.2090, 28.6139]
                }
            },
            "processed": {
                "vibe_tags": [],
                "emojis": [],
                "summary": "",
                "citations": []
            },
            "reviews": [
                {
                    "source": "reddit",
                    "content": "Just visited TomTom Coffee Shop 1 in Delhi and it was amazing! The atmosphere is perfect for studying and the coffee is top-notch.",
                    "url": "https://reddit.com/r/delhi/comments/mock1",
                    "score": 45,
                    "created_utc": 1640995200
                }
            ],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "count": 7,
    "fallback_used": true,
    "tomtom_fetched": 3,
    "reviews_scraped": 3
}
```

## How It Works

### 1. Database Search
- Searches existing places by city, category, and vibe tags
- Uses case-insensitive regex matching for categories
- Filters by vibe tags if provided

### 2. Threshold Check
- If ≥ `min_results` found, returns immediately
- No fallback needed

### 3. TomTom Fallback
- Maps categories to TomTom search queries
- Fetches additional places to reach minimum threshold
- Currently uses mock data (API calls commented out)

### 4. Reddit Scraping
- For each TomTom place, constructs Reddit search query
- Format: `"<place name> <city> review"`
- Scrapes 3-5 top Reddit posts/comments
- Includes post content, URL, score, and timestamp

### 5. Database Storage
- Transforms TomTom data to match schema
- Adds Reddit reviews to `reviews` field
- Uses bulk insert for efficiency
- Skips duplicates by `fsq_id`

## Reddit Scraping Details

### Search Query Construction
```
"<place name>" "<city>" review
```

### Review Data Structure
```json
{
    "source": "reddit",
    "content": "Review text content...",
    "url": "https://reddit.com/r/subreddit/comments/...",
    "score": 45,
    "created_utc": 1640995200
}
```

### Fallback to Mock Data
- If Reddit API fails or returns no results
- Generates realistic mock reviews
- Includes place name and city in content

## Category Mapping

The service maps categories to TomTom search queries:

| Category | TomTom Query |
|----------|--------------|
| cafe | cafe coffee |
| restaurant | restaurant food |
| park | park |
| bar | bar pub |
| museum | museum |
| shopping | shopping mall |
| gym | gym fitness |
| library | library |
| theater | theater cinema |

## Testing

### Test Endpoint
```bash
GET http://localhost:5000/api/fallback/test
```

### Test Script
```bash
cd Backend
python test_fallback_service.py
```

## Example Usage

### Using curl
```bash
curl -X POST http://localhost:5000/api/fallback/search \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Delhi",
    "category": "cafe",
    "vibe_tags": ["aesthetic"],
    "min_results": 5
  }'
```

### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:5000/api/fallback/search",
    json={
        "city": "Delhi",
        "category": "cafe",
        "vibe_tags": ["aesthetic"],
        "min_results": 5
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['count']} places")
    print(f"Fallback used: {result['fallback_used']}")
    print(f"Reviews scraped: {result['reviews_scraped']}")
else:
    print(f"Error: {response.text}")
```

## Response Sources

- `"database"`: All results from existing database
- `"database_only"`: Only database results (no TomTom fallback)
- `"database_and_tomtom"`: Combined database + TomTom results

## Notes

- Currently uses mock TomTom data to save API credits
- Reddit scraping includes rate limiting (1 second delay between requests)
- Reviews are limited to 1000 characters for storage efficiency
- All timestamps are in UTC
- Duplicate places are automatically skipped 