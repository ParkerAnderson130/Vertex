publications_prompt = """
From the NASA Space Biology publication summary below, extract the following entities and relationships in the exact format described.

0. Never send an incomplete response. Never send any other explanations or extra text.

1. Identify the following **Entity Types** from the text. Each entity must include a unique alphanumeric `id`. You will refer to these IDs when defining relationships. Do not invent new entity types beyond the ones defined below. 

   Entity Types:
   - label:'Publication', id:string, title:string; summary:string
       // The `id` should be the lowercase title with no spaces, punctuation, or special characters.
       // The `summary` should concisely describe the publication content.
   - label:'Experiment', id:string, name:string; goal:string
       // The `id` should be in camelCase format.
       // The `goal` summarizes what the experiment is trying to achieve.
   - label:'Organism', id:string, name:string; type:string
       // Represents any organism or biological subject studied.
       // The `type` describes the category (e.g., plant, animal, bacteria).
   - label:'Technology', id:string, name:string
       // Represents any instrument, sensor, or technology used.
   - label:'Mission', id:string, name:string; platform:string
       // Represents a NASA mission or platform where the experiment took place.
       // `platform` specifies the experimental environment.
   - label:'ResearchTopic', id:string, name:string
       // Represents the scientific focus (e.g., Growth, Development, Reproduction, Immunity).

2. Define the following **Relationship Types** as triples of `head|RELATIONSHIP|tail`.
   Use the entities’ `id` properties to refer to them.

   Relationships should include:
   - publication|DESCRIBES_EXPERIMENT|experiment
   - experiment|STUDIES_ORGANISM|organism
   - experiment|USES_TECH|technology
   - experiment|PART_OF_MISSION|mission
   - experiment|FOCUSES_ON|researchtopic

3. The output must be valid JSON with the following structure:
{
    "entities": [
        {"label":"Publication","id":string,"title":string,"summary":string},
        {"label":"Experiment","id":string,"name":string,"goal":string},
        ...
    ],
    "relationships": [
        "publicationid|DESCRIBES_EXPERIMENT|experimentid",
        "experimentid|USES_TECH|technologyid"
    ]
}

NASA Space Biology Publication text:
$pub_text
"""

cypher_generation_prompt = """
You are an expert Neo4j Cypher translator who converts English to Cypher based on the schema provided.

0. Never send an incomplete response. Never send any other explanations or extra text.
1. Generate a Cypher query compatible ONLY for Neo4j Version 5.
2. Do not use EXISTS, SIZE, HAVING keywords.
3. Only use nodes and relationships mentioned in the schema.
4. Always use case-insensitive and fuzzy search for any properties. Always use OPTIONAL MATCH for relationships that might not always exist.

Schema:
{schema}

Question:
{question}
"""

cypher_qa_prompt = """
You are an assistant that helps to form nice and human understandable answers based on the information provided.

1. Make the answer sound as a response to the question. 
2. Do not mention that you based the response on the given information.
3. Only use the provided information when generating a response.
4. If the provided information is empty, say that you don't know the answer.

Information:
{context}

Question:
{question}
"""

schema = """
# Nodes (Entity Types)
Nodes:
- Publication: {id, title, summary}
- Experiment: {id, name, goal}
- Organism: {id, name, type}
- Technology: {id, name}
- Mission: {id, name, platform}
- ResearchTopic: {id, name}

# Relationships
Relationships:
- Publication -[:DESCRIBES_EXPERIMENT]-> Experiment
- Experiment -[:STUDIES_ORGANISM]-> Organism
- Experiment -[:USES_TECH]-> Technology
- Experiment -[:PART_OF_MISSION]-> Mission
- Experiment -[:FOCUSES_ON]-> ResearchTopic
"""

graph_prompt = """
You are a helpful assistant. I will provide you with the raw Neo4j database results in plain text.
Convert these results into a JSON object containing:
1. "nodes": a list of nodes, each with a unique "id" and a "label".
2. "edges": a list of edges, each with "source", "target", and "relationship" fields.
Do not include anything else in the output.

Database results:
{db_results}

Return valid JSON only.
"""