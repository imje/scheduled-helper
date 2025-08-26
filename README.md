# Scheduled Helper

A GitHub Actions workflow that automatically searches for positive news from Norway every 15 minutes using OpenAI's GPT-5-nano model with web search capabilities.

## What it does

- Runs every 15 minutes via GitHub Actions
- Uses OpenAI's responses API with `gpt-5-nano` model
- Searches for positive news articles from Norway published today
- Configured for Trondheim, Norway location context
- Saves results as JSON artifacts with timestamps

## Setup

1. Add your OpenAI API key to GitHub repository secrets as `OPENAI_API_KEY`
2. Push the workflow file to your default branch
3. The workflow will run automatically every 15 minutes

## Manual Testing

You can manually trigger the workflow from the Actions tab in GitHub, with optional debug logging enabled.

## Output

Results are saved as:
- `news_results_latest.json` - Latest search results
- `news_results_YYYYMMDD_HHMMSS.json` - Timestamped results
- Workflow artifacts for easy download

## Configuration

The workflow searches for positive Norwegian news using:
- Location: Trondheim, Norway
- Search context: Low (for efficiency)
- Text verbosity: Low
- Reasoning effort: Minimal