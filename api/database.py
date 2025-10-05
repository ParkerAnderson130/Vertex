from dotenv import load_dotenv
import glob
import json
import os
from neo4j import GraphDatabase
from openai import OpenAI
from string import Template
from time import sleep

from prompts import publications_prompt

# Connect to the .env file and read the contents
load_dotenv()

# Connects to the OpenAI project
client = OpenAI()

# Connects to the Neo4j instance
neo4j_url = os.getenv("NEO4J_CONNECTION_URL")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

def process_gpt(file_prompt, system_msg):
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": file_prompt},
        ],
        max_completion_tokens=15_000,
        response_format={"type": "json_object"}
    )

    output = json.loads(response.choices[0].message.content)
    return output

# Function to take in the NASA Space Biology publication papers and label them
def extract_entities_relationships(folder, prompt_template):
    files = glob.glob(f"./data/{folder}/*")
    system_msg = """You are an expert NASA Space Biology data annotator who extracts information from publications."""

    results = []
    for i, file in enumerate(files):
        print(f"({i+1}/{len(files)}) | Extracting entities and relationships for {file}")

        try:
            with open(file, "r") as f:
                text = f.read().rstrip()
                prompt = Template(prompt_template).substitute(pub_text=text)

                result = process_gpt(prompt, system_msg=system_msg)
                results.append(result)
        except Exception as e:
            print(f"Error processing {file}: {e}")

    return results

# Function to take a json-object of entitites and relationships and generate cypher query for creating those entities
def generate_cypher(json_obj):
    entity_statements = []
    relation_statements = []

    entity_label_map = {}

    # Loop through the labeled entities
    for i, obj in enumerate(json_obj):
        print(f"({i+1}/{len(json_obj)}) | Generating cypher for file ")

        for entity in obj["entities"]:
            label = entity["label"]
            id = entity["id"]

            if not label or not id:
                print(f"Error processing {entity}")
                continue

            id = id.replace("-", "").replace("_", "") # Make variable safe
            properties = {k: v for k, v in entity.items() if k not in ["label", "id"]}

            cypher = f'MERGE (n:{label} {{id: "{id}"}})'
            if properties:
                props_str = ", ".join(
                    [f'n.{key} = "{val}"' for key, val in properties.items()]
                )
                cypher += f" ON CREATE SET {props_str}"
            entity_statements.append(cypher)
            entity_label_map[id] = label

        for relation in obj["relationships"]:
            source_id, relation_type, target_id = relation.split("|")
            source_id = source_id.replace("-", "").replace("_", "") # Make variable safe
            target_id = target_id.replace("-", "").replace("_", "")

            if source_id not in entity_label_map or target_id not in entity_label_map:
                print(f"Error processing {relation}")
                continue

            src_label = entity_label_map[source_id]
            target_label = entity_label_map[target_id]

            cypher = f'MERGE (a:{src_label} {{id: "{source_id}"}}) MERGE (b:{target_label} {{id: "{target_id}"}}) MERGE (a)-[:{relation_type}]->(b)'
            relation_statements.append(cypher)

    with open("cyphers.txt", "w") as outfile:
        outfile.write("\n".join(entity_statements + relation_statements))

    return entity_statements + relation_statements

# Loop over all steps to load the database
def ingestion_pipeline(folders):
    # Extract the entites and relationships
    entities_relationships = []
    for key, value in folders.items():
        entities_relationships.extend(extract_entities_relationships(key, value))

    # Generate and execute cypher statements
    cypher_statements = generate_cypher(entities_relationships)
    for i, stmt in enumerate(cypher_statements):
        print(f"({i+1}/{len(cypher_statements)}) | Executing cypher statement")

        try:
            driver.execute_query(stmt)
        except Exception as e:
            with open("failed_statements.txt", "w") as f:
                f.write(f"{stmt} - Exception: {e}\n")

if __name__ == "__main__":
    folders = {
        "publications": publications_prompt,
    }
    ingestion_pipeline(folders)