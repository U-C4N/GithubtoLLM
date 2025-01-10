# PDF to Markdown Token Counter

A sophisticated Python web application for extracting, analyzing, and rendering GitHub repository content with advanced multi-model token counting capabilities.

## Features

- Real-time repository content analysis
- Comprehensive token counting and cost estimation
- Support for multiple AI model pricing:
  - o1 ($15.00 per 1M input tokens)
  - o1-mini ($3.00 per 1M input tokens)
  - Claude 3.5 Sonnet ($3.00 per 1M input tokens)
  - GPT-4o ($2.50 per 1M input tokens)
  - Gemini 1.5 Pro ($1.25 per 1M input tokens)
  - Gemini 1.5 Flash ($0.075 per 1M input tokens)
- Clean markdown output with file structure
- Color-coded pricing display
- Easy-to-use web interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/U-C4N/pdftomarkdown.git
cd pdftomarkdown
```

2. Install dependencies:
```bash
pip install flask gitpython
```

3. Run the application:
```bash
python app.py
```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Enter a GitHub repository URL
3. Click "Clone Repository" to analyze
4. View the generated markdown and token costs

## Technology Stack

- Python 3.x
- Flask
- GitPython
- JavaScript
- HTML/CSS

## Author

<p align="left"> <b>Umutcan Edizaslan:</b> <a href="https://github.com/U-C4N" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Github-Dark.svg" alt="TutTrue" height="30" width="40" /></a> <a href="https://x.com/UEdizaslan" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Twitter.svg" height="30" width="40" /></a> <a href="https://discord.gg/2Tutcj6u" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Discord.svg" height="30" width="40" /></a> </p>

## License

This project is licensed under the MIT License - see the LICENSE file for details.
