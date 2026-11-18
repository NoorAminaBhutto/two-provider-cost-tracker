# Two Provider Cost Tracker

## Project Overview

This project compares two AI providers:
- Google Gemini
- Groq

It sends the same prompt to both providers and tracks their token usage and estimated API costs.

## Features

- Gemini API integration
- Groq API integration
- Input token tracking
- Output token tracking
- Total token calculation
- API cost calculation
- JSON result storage
- Error handling for failed requests

## Technologies Used

- Python
- Google GenAI SDK
- Groq SDK
- python-dotenv
- UV package manager

## Project Setup

### 1. Install Dependencies

Run:

```bash
uv sync
```

### 2. Configure API Keys

Create a `.env` file in the project directory.

Add your API keys and model names:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model
```

Add the provider pricing per million tokens:

```env
GEMINI_INPUT_PRICE=0
GEMINI_OUTPUT_PRICE=0
GROQ_INPUT_PRICE=0
GROQ_OUTPUT_PRICE=0
```

Replace the zero values with the actual pricing.

### 3. Run the Project

```bash
uv run tracker.py "What is Artificial Intelligence?"
```

## Output

The program displays:

- AI responses from both providers
- Input tokens
- Output tokens
- Total tokens
- Estimated API cost

The results are saved in `results.json`.

## Project Structure

- tracker.py - Main application
- .env - API keys and configuration
- .env.example - Environment variable template
- .gitignore - Ignored files
- pyproject.toml - Project dependencies
- README.md - Project documentation
- results.json - Generated results

## Security

Never share or upload API keys.
The `.env` file should remain private.

## Conclusion

This project demonstrates how to compare two AI providers using the same prompt while tracking token usage and estimated API costs.