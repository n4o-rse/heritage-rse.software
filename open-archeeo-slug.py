import pandas as pd
import re
from collections import defaultdict

# R-nahe Slug-Funktion
def clean_slug(text):
    text = text.lower()
    text = re.sub(r'\.r$', '', text)            # Entferne .r am Ende
    text = text.replace(" ", "-")
    text = text.replace("_", "-")
    text = text.replace(".", "-")
    text = text.replace("/", "-")
    text = re.sub(r'--+', '-', text)            # Mehrere -- → -
    return text

# Eindeutige Slugs erzeugen
def generate_unique_slugs(slugs):
    slug_counts = defaultdict(int)
    unique_slugs = []
    for slug in slugs:
        count = slug_counts[slug]
        if count == 0:
            unique_slugs.append(slug)
        else:
            unique_slugs.append(f"{slug}-{count}")
        slug_counts[slug] += 1
    return unique_slugs

# CSV einlesen
url = "https://raw.githubusercontent.com/zackbatist/open-archaeo/refs/heads/master/open-archaeo.csv"
df = pd.read_csv(url)

# Slugs berechnen
df['slug_base'] = df['item_name'].apply(clean_slug)
df['slug'] = generate_unique_slugs(df['slug_base'])

# Interne ID (1-basiert)
df['internal_id'] = df.index + 1

# Ergebnis-DataFrame
base_uri = "https://open-archaeo.info/post/"
output_df = pd.DataFrame({
    "internal_id": df["internal_id"],
    "id": df["slug"],
    "name": df["item_name"],
    "URI": base_uri + df["slug"]
})

# Als CSV speichern
output_df.to_csv("open-archaeo-slugs.csv", index=False)

# Vorschau
print(output_df.head(10))
