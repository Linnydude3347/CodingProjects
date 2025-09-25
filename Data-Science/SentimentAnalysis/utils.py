import re
import emoji

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)")  # capture word after #
WHITESPACE_RE = re.compile(r"\s+")

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove URLs and mentions
    text = URL_RE.sub("", text)
    text = MENTION_RE.sub("", text)
    # Convert emojis to text (optional, helps lexical analyzers)
    text = emoji.replace_emoji(text, replace=lambda c, data_dict: f" {data_dict['en']} ")
    # Replace hashtags with the word (e.g., #Python -> Python)
    text = HASHTAG_RE.sub(lambda m: f" {m.group(1)} ", text)
    # Normalize whitespace
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text