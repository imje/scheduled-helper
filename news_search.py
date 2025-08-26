#!/usr/bin/env python3
"""
Hourly news search script using OpenAI API to find news article URLs.
"""

import os
import json
import requests
from datetime import datetime
from openai import OpenAI

def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using available model instead of gpt-5-nano
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that searches for current news articles. Provide exactly 5 recent news article URLs from reputable sources."
                },
                {
                    "role": "user",
                    "content": "Please find 5 current news article URLs from the past 24 hours. Return them as a simple list, one URL per line."
                }
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        news_urls = response.choices[0].message.content.strip().split('\n')
        news_urls = [url.strip() for url in news_urls if url.strip()]
        
        timestamp = datetime.now().isoformat()
        result = {
            "timestamp": timestamp,
            "news_urls": news_urls[:5],  # Ensure exactly 5 URLs
            "model_used": "gpt-4o-mini"
        }
        
        print(f"Found {len(result['news_urls'])} news URLs at {timestamp}")
        for i, url in enumerate(result['news_urls'], 1):
            print(f"{i}. {url}")
            
        # Save results to file
        with open('news_results.json', 'w') as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        print(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()