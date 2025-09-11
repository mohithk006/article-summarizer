# Summarify: AI Article Summarizer & Analyzer

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)
[![NLTK](https://img.shields.io/badge/NLP-NLTK_&_TextBlob-blueviolet.svg)](https://www.nltk.org/)

**Summarify** is a simple yet powerful desktop application that instantly summarizes any online article. Just provide a URL, and this tool will fetch, analyze, and present the key information—including a summary and sentiment analysis—in a clean graphical user interface (GUI).

---

## 📋 Table of Contents
- [✨ Key Features](#-key-features)
- [🧠 How It Works](#-how-it-works)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
- [📖 How to Use](#-how-to-use)
- [💡 Potential Improvements](#-potential-improvements)

---

## Key Features

-   **One-Click Summarization**: Automatically generates a concise summary of any online news article or blog post from its URL.
-   **Key Information Extraction**: Instantly pulls the article's **Title**, **Authors**, and **Publication Date**.
-   **Sentiment Analysis**: Analyzes the article's content to determine its overall sentiment (Positive, Negative, or Neutral).
-   **Simple Desktop GUI**: A clean and user-friendly interface built with Python's native `tkinter` library.
-   **Smart URL Handling**: Automatically validates and formats URLs to ensure they are correct before processing.

---

## How It Works

The application follows a straightforward process:

1.  **URL Input**: The user pastes a URL into the input field.
2.  **Article Fetching**: The `newspaper3k` library downloads the HTML content of the article from the provided URL.
3.  **Content Parsing**: The library then parses the downloaded content to extract the main text, title, authors, and publication date.
4.  **NLP Summarization**: `newspaper3k` applies its built-in Natural Language Processing (NLP) algorithms to generate a concise summary of the article.
5.  **Sentiment Analysis**: The full text of the article is analyzed by the `TextBlob` library to calculate its polarity score, which determines if the sentiment is positive, negative, or neutral.
6.  **Display**: All the extracted information is neatly displayed in the read-only fields of the `tkinter` GUI. Error handling is included to manage cases where an article cannot be downloaded or parsed.

---

## Tech Stack

This project is built entirely in Python, relying on a few key libraries for its functionality:

| Category                | Technology / Library                                       |
| ----------------------- | ---------------------------------------------------------- |
| **GUI Framework** | `tkinter` (Python's standard GUI package)                  |
| **Web Scraping & NLP** | `newspaper3k` (for article extraction and summarization)   |
| **Sentiment Analysis** | `TextBlob`                                                 |
| **Language Processing** | `NLTK` (Natural Language Toolkit) - a dependency for TextBlob |

---

## Getting Started

Follow these instructions to get the application running on your local machine.

### Prerequisites

-   Python 3.x
-   `pip` (Python package installer)

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/summarify.git](https://github.com/your-username/summarify.git)
    cd summarify
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    You will need to install a few packages. You can create a `requirements.txt` file with the following content:
    ```
    newspaper3k
    nltk
    textblob
    ```
    Then, run the following command to install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK Data**
    The `TextBlob` library requires specific data packages from NLTK to function correctly. Run Python from your terminal and download the necessary data.
    ```bash
    python
    ```
    Then, inside the Python interpreter, run:
    ```python
    import nltk
    nltk.download('punkt')
    exit()
    ```
    This only needs to be done once.

5.  **Run the Application**
    Execute your Python script to launch the GUI.
    ```bash
    python your_script_name.py  # Replace with the actual name of your script
    ```

---

## How to Use

1.  Run the application to open the **Summarify** window.
2.  Find an online article you want to summarize and copy its URL.
3.  Paste the URL into the "URL" input box at the bottom of the window.
4.  Click the **"Summarize"** button.
5.  Within a few seconds, the Title, Author, Publication Date, Summary, and Sentiment Analysis fields will be populated with the extracted information.
