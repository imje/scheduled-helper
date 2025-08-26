#!/usr/bin/env python3
"""
Hourly news search script using OpenAI API to find news article URLs.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List

from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_urls(urls: List[str]) -> List[str]:
    """Basic URL validation"""
    valid_urls = []
    for url in urls:
        url = url.strip()
        if url.startswith(("http://", "https://")) and len(url) > 10:
            valid_urls.append(url)
    return valid_urls


def search_news_with_retry(client: OpenAI, max_retries: int = 3) -> Dict[str, Any]:
    """Search for news with retry logic using responses API and web_search_preview tool"""

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting news search (attempt {attempt + 1}/{max_retries})")

            # Use the responses API with web_search_preview tool (correct syntax)
            response = client.responses.create(
                model="gpt-5-nano",
                tools=[
                    {
                        "type": "web_search_preview",
                        "user_location": {
                            "type": "approximate",
                            "country": "NO",
                            "city": "Trondheim",
                            "region": "Trondheim",
                        },
                        "search_context_size": "low",
                    }
                ],
                input="Find 1 positive news article URL from today in Norway. Return just the URL.",
                reasoning={"effort": "low"},
                text={"verbosity": "low"},
            )

            # Get the output text from the response
            content = response.output_text
            logger.info(f"Response received: {content[:200]}...")

            # Extract URLs from the response text
            lines = content.split("\n")
            news_urls = []

            for line in lines:
                line = line.strip()
                # Look for URLs in the line
                if "http" in line:
                    # Extract URLs from the line
                    urls_in_line = re.findall(r'https?://[^\s<>"{}|\\^`[\]]+', line)
                    news_urls.extend(urls_in_line)

            # Validate URLs
            valid_urls = validate_urls(news_urls)

            # If we still don't have valid URLs, try parsing differently
            if len(valid_urls) == 0:
                logger.warning(
                    f"Only found {len(valid_urls)} valid URLs, trying alternative parsing"
                )
                # Try to extract any URLs that might be formatted differently
                all_urls = re.findall(r'https?://[^\s<>"{}|\\^`[\]]+', content)
                valid_urls = validate_urls(all_urls)

            # Only return what we actually found from web search
            if len(valid_urls) == 0:
                raise ValueError("No valid URLs found in web search results")

            # Convert usage to dict if it exists
            usage_data = None
            if hasattr(response, "usage") and response.usage:
                usage_data = response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage._asdict()
            
            return {
                "urls": valid_urls[:1],  # Only return 1 URL
                "raw_response": content,
                "usage": usage_data,
            }

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                # All attempts failed - raise the error
                logger.error("All attempts to search for news failed")
                raise


def main():
    """Main function to search for news and save results"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        logger.info("Starting news search...")
        client = OpenAI(api_key=api_key)

        # Search for news with retry
        search_result = search_news_with_retry(client)

        timestamp = datetime.now().isoformat()
        result = {
            "timestamp": timestamp,
            "news_urls": search_result["urls"],
            "model_used": "gpt-5-nano",
            "url_count": len(search_result["urls"]),
            "usage": search_result.get("usage"),
            "status": "success",
        }

        logger.info(f"Found {len(result['news_urls'])} news URLs at {timestamp}")
        for i, url in enumerate(result["news_urls"], 1):
            logger.info(f"{i}. {url}")

        # Save results to file
        output_file = f"news_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

        # Also save latest results
        with open("news_results_latest.json", "w") as f:
            json.dump(result, f, indent=2)

        logger.info(f"Results saved to {output_file} and news_results_latest.json")

    except Exception as e:
        logger.error(f"Fatal error: {e}")

        # Save error information
        error_result = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "model_used": "gpt-5-nano",
        }

        with open("news_results_latest.json", "w") as f:
            json.dump(error_result, f, indent=2)

        raise


if __name__ == "__main__":
    main()
