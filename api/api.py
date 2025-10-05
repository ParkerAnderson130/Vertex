import dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage
from pydantic import BaseModel
import os

from prompts import cypher_generation_prompt, cypher_qa_prompt, schema, graph_prompt

# Connect to the .env file and read the contents
dotenv.load_dotenv()

# Instantiates GPT
llm = ChatOpenAI(
    model_name="gpt-5-nano",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# Connects to the Neo4j instance
graph = Neo4jGraph(
    url=os.getenv("NEO4J_CONNECTION_URL"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Prompt templates
cypher_prompt = PromptTemplate(
    template=cypher_generation_prompt,
    input_variables=["schema", "question"]
)
qa_prompt = PromptTemplate(
    template=cypher_qa_prompt,
    input_variables=["context", "question"]
)


# Instantiates FastAPI
app = FastAPI(title="Neo4j Conversational API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

chat_history = []
@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        # Create the LangChain Cypher + QA chain
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            input_key="question",
            allow_dangerous_requests=True
        )

        # Pass natural language question and schema; chain will generate 'query' internally
        result = chain.invoke({
            "question": request.question,
        })

        # Extract intermediate steps
        intermediate_steps = result.get("intermediate_steps", [])
        cypher_query = intermediate_steps[0]["query"] if len(intermediate_steps) > 0 else ""
        database_results = intermediate_steps[1]["context"] if len(intermediate_steps) > 1 else ""
        answer = result.get("result", "")

        graph_json = format_graph_for_frontend(database_results)

        # Save to chat history
        chat_history.append({
            "question": request.question,
            "answer": answer,
            "cypher": cypher_query,
            "db_results": database_results
        })

        return {
            "answer": answer,
            "cypher_query": cypher_query,
            "db_results": database_results,
            "graph": graph_json
        }  

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
def format_graph_for_frontend(db_results: str):
    try:
        llm_output = llm.invoke(graph_prompt.format(db_results=db_results))
        
        if isinstance(llm_output, AIMessage):
            graph_json_text = llm_output.content
        else:
            graph_json_text = str(llm_output)

        graph_data = json.loads(graph_json_text)
        return graph_data

    except json.JSONDecodeError:
        print("Failed to parse JSON from GPT output:", graph_json_text)
        return {"nodes": [], "edges": []}
    except Exception as e:
        print("Error formatting graph:", e)
        return {"nodes": [], "edges": []}
