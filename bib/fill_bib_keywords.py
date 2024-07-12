# this code uses the .bib file from zotero export as well as a .csv file created for another vis tool: https://github.com/richardwolfmayr/visual-image-set-summarization
# it reads the .bib file and the .csv file and fills the keywords field in the .bib file with the keywords from the .csv file
# the keywords are structured like this: category1:tag1, category1:tag2, category2:tag1, etc
# it stores the new .bib file in the "references.bib" file which is used by the survis tool
# problem: The .csv references the papers with and id that is not the same as the id in the .bib file but works with a .json file exported from zotero.
# so the a matching between the json and the bib export from zotero must be done ==> they are in the same order, which will be used for matching

# idea: create a dictonary in this structure:
#{id: {category1: [tag1, tag2], category2: [tag1, tag2]}}
# this dictonary is ordered in the same way as the .bib file and the .json file
# it is filled with category and tags from the .csv file
# then iterate over the .bib file and fill the keywords field with the tags from the dictionary

# so to use this:
# export bib from zotero
# export json from zotero
# create a .csv file with the keywords from the other vis tool
# run this script

import json
import csv

def parse_csv(csv_filename):
    keywords = {}
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            id = row['Paper#Ref'].split('#')[-1]  # Extract the ID after the #
            categories = {}
            for key, value in row.items():
                if key != 'Paper#Ref' and not key.startswith('Unnamed') and value != '0':  # Exclude 'Unnamed' and zero values
                    category, tag = key.split(' > ')
                    # convert the category and the tag to lowercase, otherwise the tool cannot deal with it
                    category = category.lower()
                    tag = tag.lower()
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(tag)
            keywords[id] = categories
    return keywords

# Check if the keywords are parsed correctly:
csv_input_filename = "table2-combCite.csv"
keywords = parse_csv(csv_input_filename)
print(keywords)

def parse_json(json_filename):
    with open(json_filename, 'r') as jsonfile:
        data = json.load(jsonfile)
    return data

def fill_keywords(bib_filename, keywords, json_data):
    with open(bib_filename, 'r') as bibfile:
        bib_content = bibfile.readlines()

    new_bib_content = []
    json_index = 0
    ids = list(keywords.keys())

    current_key = None
    entry_keywords_added = False

    for line in bib_content:
        if line.startswith('@'):
            current_key = json_data[json_index]['id'] # this is the id from the json file
            new_bib_content.append(line)
            json_index += 1
            entry_keywords_added = False
        elif 'keywords' in line:
            existing_keywords = line.split('=', 1)[1].strip()[1:-2].strip()
            if current_key in keywords:
                new_keywords = ', '.join([f"{cat}:{tag}" for cat, tags in keywords[current_key].items() for tag in tags])
                # Combine the existing and new keywords
                # combined_keywords = f"{new_keywords}, {existing_keywords}" if existing_keywords else new_keywords
                combined_keywords = new_keywords # ONLY new keywords, since I do not care about the existing ones right now
                new_line = f'  keywords = {{{combined_keywords}}},\n'
                new_bib_content.append(new_line)
            else:
                new_bib_content.append(line)
            entry_keywords_added = True
        elif line.strip() == '}' and not entry_keywords_added and current_key in keywords:
            new_keywords = ', '.join([f"{cat}:{tag}" for cat, tags in keywords[current_key].items() for tag in tags])
            new_bib_content.append(f'  keywords = {{{new_keywords}}},\n')
            new_bib_content.append(line)
            entry_keywords_added = True
        else:
            new_bib_content.append(line)

    with open('references.bib', 'w') as new_bibfile:
        new_bibfile.writelines(new_bib_content)

def main():
    csv_input_filename = "table2-combCite.csv"
    bib_input_filename = "exploratory.bib"
    json_input_filename = "exploratory.json"

    keywords = parse_csv(csv_input_filename)
    json_data = parse_json(json_input_filename)
    fill_keywords(bib_input_filename, keywords, json_data)

if __name__ == "__main__":
    main()

