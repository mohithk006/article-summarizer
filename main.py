import tkinter as tk
import nltk
from textblob import TextBlob
from newspaper import Article
import re


# Function to validate and fix the URL format
def validate_url(url):
    url = url.strip()
    if not url:
        return None  # No URL provided
    if not re.match(r"^https?://", url):
        url = "https://" + url  # Add https if missing
    return url


# Summarization functionality
def summarize():
    # Get URL from input box
    url = utext.get("1.0", "end").strip()
    url = validate_url(url)

    if not url:
        title.config(state="normal")
        title.delete("1.0", "end")
        title.insert("1.0", "Error: Please enter a valid URL")
        title.config(state="disabled")
        return

    try:
        # Passing URL into the Article object
        article = Article(url)
        article.download()
        if not article.html:
            raise Exception("Failed to download the article")

        article.parse()
        article.nlp()  # Apply NLP processing

        # Enable text fields for modification
        title.config(state="normal")
        author.config(state="normal")
        publication.config(state="normal")
        summary.config(state="normal")
        sentiment.config(state="normal")

        # Insert extracted data into text fields
        title.delete("1.0", "end")
        title.insert("1.0", article.title if article.title else "No Title Found")

        author.delete("1.0", "end")
        author.insert("1.0", ", ".join(article.authors) if article.authors else "No Author Found")

        publication.delete("1.0", "end")
        publication.insert("1.0", str(article.publish_date) if article.publish_date else "No Date Available")

        summary.delete("1.0", "end")
        summary.insert("1.0", article.summary if article.summary else "No Summary Available")

        # Sentiment analysis
        analysis = TextBlob(article.text)
        sentiment.delete("1.0", "end")
        sentiment.insert("1.0", f"Polarity: {analysis.polarity}, Sentiment: {'Positive' if analysis.polarity > 0 else 'Negative' if analysis.polarity < 0 else 'Neutral'}")

        # Disable text fields again
        title.config(state="disabled")
        author.config(state="disabled")
        publication.config(state="disabled")
        summary.config(state="disabled")
        sentiment.config(state="disabled")

    except Exception as e:
        title.config(state="normal")
        title.delete("1.0", "end")
        title.insert("1.0", f"Error: {str(e)}")
        title.config(state="disabled")


# Building GUI
root = tk.Tk()
root.title("Summarify")
root.geometry("750x650")

# Title
tlabel = tk.Label(root, text="Title")
tlabel.pack()
title = tk.Text(root, height=1.5, width=100, bg="#dddddd", state="disabled")
title.pack()

# Author
alabel = tk.Label(root, text="Author")
alabel.pack()
author = tk.Text(root, height=1.5, width=100, bg="#dddddd", state="disabled")
author.pack()

# Publication Date
plabel = tk.Label(root, text="Publication Date")
plabel.pack()
publication = tk.Text(root, height=1.5, width=100, bg="#dddddd", state="disabled")
publication.pack()

# Summary
slabel = tk.Label(root, text="Summary")
slabel.pack()
summary = tk.Text(root, height=20, width=100, bg="#dddddd", state="disabled")
summary.pack()

# Sentiment Analysis
selabel = tk.Label(root, text="Sentiment Analysis")
selabel.pack()
sentiment = tk.Text(root, height=1.5, width=100, bg="#dddddd", state="disabled")
sentiment.pack()

# URL Input
ulabel = tk.Label(root, text="URL")
ulabel.pack()
utext = tk.Text(root, height=1.5, width=100)
utext.pack()  # Enabled for user input

# Summarize Button
btn = tk.Button(root, text="Summarize", command=summarize)
btn.pack(pady=10)  # Added spacing

# Run the Tkinter event loop
root.mainloop()
