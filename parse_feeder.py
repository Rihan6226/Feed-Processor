import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
import feedparser
from datetime import datetime
import torch
from transformers import DistilBertTokenizer, DistilBertModel

# Check for GPU availability and set the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Load the DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertModel.from_pretrained("distilbert-base-uncased").to(device)

# Define a padding token if it doesn't exist
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Set the padding token to the end-of-sequence token


# Categories and words needed to be analysed for each categories
categories = [
    "Terrorism / Protest / Political Unrest / Riot",
    "Positive / Uplifting",
    "Natural Disasters"
]
categories_embedd = {
    "Terrorism / Protest / Political Unrest / Riot": "terrorism, protest, political unrest, riot, civil disorder, revolution, coup, insurgency, extremism, militancy, violence, radicalization, clashes, demonstratio, Judiciary, vote, president ",
    "Positive / Uplifting": "happy, positive, uplifting, joyful, optimistic, inspiring, encouraging, motivational, hopeful, celebration, achievement, success, triumph, gratitude, love, kindness, compassion",
    "Natural Disasters": "earthquake, natural disaster, tsunami, flood, hurricane, wildfire, landslide, volcano, drought, storm, cyclone, typhoon, tornado, avalanche, blizzard, heatwave"
}


# Function to generate embeddings
def get_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)  # Move inputs to GPU
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Average pooling over the last hidden state
    return embeddings



# Generate embeddings for categories
category_embeddings = [get_embeddings(categories_embedd[category]) for category in categories]





# Function to classify articles
def classify_article(article):
    full_text = f"{article['title']}: {article['description']}"
    article_embedding = get_embeddings(full_text)

    # Calculate cosine similarity
    similarities = []
    for category_embedding in category_embeddings:
        sim = torch.nn.functional.cosine_similarity(article_embedding, category_embedding)
        similarities.append(sim.item())
    
    # Get the category with the highest similarity
    max_index = similarities.index(max(similarities))
    max_sim = max(similarities)
    if max_sim>0.7:
        return categories[max_index]
    else :
        return "Others"


def parse_feed(url):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        # Extract the media content (if available)
        media_content = None
        if 'media_content' in entry:
            media_content = entry.media_content[0]['url'] if entry.media_content else None
        
        # Extract published date
        published_date = None
        if hasattr(entry, 'published_parsed'):
            published_date = datetime(*entry.published_parsed[:6])
        
        article = {
            'title': entry.title,
            'content': entry.summary if 'summary' in entry else '', 
            'published': published_date,
            'url': entry.link,
            'media_url': media_content , 
            'category':""
        }
        articles_required = {
            'title': entry.title,
            'description': entry.summary if 'summary' in entry else '',
        }
        article_category = classify_article(articles_required)
        article['category'] = article_category
        articles.append(article)
    return articles

if __name__ == "__main__":
    categorised_article = parse_feed('http://rss.cnn.com/rss/cnn_topstories.rss')
    for article in categorised_article:
        print(f"Title : {article['title']}" )
        print(f"Media : {article['media_url']}" )
        print(f"Category : {article['category']}\n" )