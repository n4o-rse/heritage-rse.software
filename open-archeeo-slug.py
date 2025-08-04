import pandas as pd
import re

# R-like slug function following the transformation logic from the R script
def clean_slug(text):
    text = str(text).lower()
    text = re.sub(r'\.r$', '', text)             # Remove trailing ".r"
    text = text.replace(" ", "-")
    text = text.replace("_", "-")
    text = text.replace(".", "-")
    text = text.replace("/", "-")
    text = re.sub(r'--+', '-', text)             # Replace multiple hyphens with a single one
    return text

# Load the CSV file from GitHub
url = "https://raw.githubusercontent.com/zackbatist/open-archaeo/refs/heads/master/open-archaeo.csv"
df = pd.read_csv(url)

# Generate initial slug based on item_name
df['slug'] = df['item_name'].apply(clean_slug)
df['slug_base'] = df['slug']  # Keep original base for diagnostics/statistics

# Identify duplicated slugs
duplicated_slugs = df[df.duplicated("slug", keep=False)]

# If duplicates exist, disambiguate them by appending the author1_name
if not duplicated_slugs.empty:
    print(f"Disambiguation required for {len(duplicated_slugs)} entries with non-unique slugs.")
    for slug_base, group in duplicated_slugs.groupby("slug"):
        if len(group) > 1:
            for idx in group.index:
                author = str(df.loc[idx, "author1_name"])
                author_slug = clean_slug(author)
                df.at[idx, "slug"] = f"{slug_base}-{author_slug}"

    # Check again for uniqueness after author disambiguation
    if df["slug"].nunique() != len(df):
        raise ValueError("Could not generate unique slugs even after adding author1_name.")

# Add internal row ID (1-based)
df['internal_id'] = df.index + 1

# Define relevant software categories
software_categories = ["Packages and libraries", "Standalone software", "Scripts"]

# Base URI
base_uri = "https://open-archaeo.info/post/"

# Full output DataFrame
output_df = pd.DataFrame({
    "internal_id": df["internal_id"],
    "id": df["slug"],
    "name": df["item_name"],
    "category": df["category"],
    "URI": base_uri + df["slug"]
})

# Software-only subset
software_df = output_df[output_df["category"].isin(software_categories)]

# Export both CSV files
output_df.to_csv("open-archaeo-slugs.csv", index=False)
software_df.to_csv("open-archaeo-software-slugs.csv", index=False)

# Print preview of software entries
print("\n--- Software Entries Preview ---")
print(software_df.head(10))

# Generate slug statistics
total_items = len(df)
unique_slugs = df["slug"].nunique()
duplicate_slug_bases = df["slug_base"].duplicated().sum()

print("\n--- Slug Statistics ---")
print(f"Total number of entries: {total_items}")
print(f"Unique slugs:            {unique_slugs}")
print(f"Duplicate slug bases:    {duplicate_slug_bases}")
print("Examples of base slug collisions:")
print(df[df.duplicated("slug_base", keep=False)][["item_name", "author1_name", "slug_base", "slug"]])
