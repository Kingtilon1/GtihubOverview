from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.nvidia import NVIDIAEmbedding  # Add this
from dotenv import load_dotenv
from github import Github
from openai import OpenAI
from bs4 import BeautifulSoup
import markdown
import re
import time 
app = Flask(__name__)
CORS(app)

load_dotenv(dotenv_path="../../.env")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
nvidia_api_key = os.environ.get("NVIDIA_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

github_token = os.environ.get("GITHUB_TOKEN")
g = Github(github_token)

github_token = os.environ.get("GITHUB_TOKEN")
g = Github(github_token)

def get_embedding(text):
    try:
        embed_model = NVIDIAEmbedding(
            api_key=nvidia_api_key,
            model="nvidia/nv-embedqa-e5-v5", 
            truncate="END"
        )
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Embedding Error: {e}")
        print(f"Available models: {NVIDIAEmbedding.available_models()}") 
        return None

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return jsonify({"message": "Tilon!"})

def get_repo_name_from_url(repo_url):
    """Extract owner and repo name from GitHub URL"""
    # Remove trailing slash if present
    repo_url = repo_url.rstrip('/')
    
    # Handle different GitHub URL formats
    if "github.com" not in repo_url:
        raise ValueError("Not a valid GitHub URL")
        
    parts = repo_url.split('github.com/')
    if len(parts) != 2:
        raise ValueError("Not a valid GitHub URL format")
        
    full_name = parts[1]
    if full_name.endswith('.git'):
        full_name = full_name[:-4]
        
    # Should now have format: "owner/repo"
    return full_name

def clean_index_name(repo_url):
    """Convert repo URL to valid Pinecone index name"""
    # Get the last part of the URL and convert to lowercase
    repo_name = repo_url.split('/')[-1].lower()
    
    # Replace any non-alphanumeric characters with '-'
    import re
    clean_name = re.sub(r'[^a-z0-9-]', '-', repo_name)
    
    # Remove multiple consecutive dashes
    clean_name = re.sub(r'-+', '-', clean_name)
    
    clean_name = clean_name.strip('-')
    
    # Pinecone name has to start with a letter
    if not clean_name[0].isalpha():
        clean_name = 'repo-' + clean_name
        
    # Pinecone has a length limit apparently
    return clean_name[:62]

def clean_markdown(markdown_text):
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route("/repo", methods=['POST'])
def process_repo():
    try:
        # Get repo URL from request
        repo_url = request.json.get('repo_url')
        if not repo_url:
            return jsonify({"error": "No repository URL provided"}), 400
        
        try:
            repo_name = get_repo_name_from_url(repo_url)  # This will be "owner/repo"
            repo = g.get_repo(repo_name)  # Get the repo using full name
        except Exception as e:
            print(f"Error accessing repository: {str(e)}")
            return jsonify({"error": f"Could not access repository: {str(e)}"}), 404
        

        # Create or get the Pinecone index
        index_name = "github-helper-index"
        try:
            pinecone_index = pc.Index(index_name)
        except Exception as e:
            pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(5)
            pinecone_index = pc.Index(index_name)

        # Get repo data
        repo = g.get_repo(repo_name)
        repo_data = []
        
        # Get README and split into sections
        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode()
            
            # Split content into different sections
            sections = []
            current_section = ""
            current_title = "Introduction"
            
            for line in content.split('\n'):
                # New section if line starts with ##
                if line.startswith('## '):
                    if current_section:
                        sections.append({
                            "title": current_title,
                            "content": clean_markdown(current_section)
                        })
                    current_title = line.replace('#', '').strip()
                    current_section = ""
                else:
                    current_section += line + "\n"
                    
            # Add the last section
            if current_section:
                sections.append({
                    "title": current_title,
                    "content": clean_markdown(current_section)
                })
            
            # Add each section as separate piece of data
            for section in sections:
                repo_data.append({
                    "type": "readme_section",
                    "title": section["title"],
                    "content": section["content"]
                })
                
        except Exception as e:
            print(f"README Error: {e}")
        ## for contributing 
        try:
            contributing = repo.get_contents("CONTRIBUTING.md")
            content = contributing.decoded_content.decode()
            
            sections = []
            current_section = ""
            current_title = ""
            
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for headers (# or ## or ###)
                if line.startswith(('#')):
                    # Save previous section if it exists and isn't empty
                    if current_section.strip():
                        sections.append({
                            "title": current_title,
                            "content": clean_markdown(current_section)
                        })
                    
                    # Start new section
                    current_title = line.lstrip('#').strip()
                    current_section = ""
                else:
                    current_section += line + "\n"
                i += 1
            
            # last section for me to append
            if current_section.strip():
                sections.append({
                    "title": current_title,
                    "content": clean_markdown(current_section)
                })
            
            # Add non-empty sections to repo_data
            for section in sections:
                if section["content"].strip():  
                    repo_data.append({
                        "type": "contributing_section",
                        "title": section["title"],
                        "content": section["content"]
                    })
            print(repo_data)
        except Exception as e:
            print(f"CONTRIBUTING Error: {e}")
            
        ## For Code of Conduct
        try:
            code_of_conduct = repo.get_contents("CODE_OF_CONDUCT.md")
            content = code_of_conduct.decoded_content.decode()
            if current_section.strip():
                sections.append({
                    "type": "conduct_section",
                    "title": "Code of Conduct",
                    "content": clean_markdown(content)
                })
                repo_data.append({
                    "type": "conduct_section",
                    "title": "Code of Conduct",
                    "content": clean_markdown(content)
                })
        except Exception as e:
            print(f"Note: No CODE_OF_CONDUCT.md found. This is normal.")
        
        ## For licensing
        try:
            license_file = repo.get_contents("LICENSE")
            content = license_file.decoded_content.decode()
            if current_section.strip():
                sections.append({
                    "type": "license_section",
                    "title": "License",
                    "content": clean_markdown(content)
                })
                repo_data.append({
                    "type": "license_section",
                    "title": "License",
                    "content": clean_markdown(content)
                })
        except Exception as e:
            print(f"Note: No LICENSE found. This is normal.")
           
        
        
        
        vectors_to_upsert = []
        for i, section in enumerate(repo_data):
            embedding = get_embedding(section['content'])
            if embedding:
                vectors_to_upsert.append({
                    "id": f"{section['type']}_{i}",
                    "values": embedding,
                    "metadata": {
                        "type": section['type'],
                        "title": section['title'],
                        "content": section['content'],
                        "repo_url": repo_url
                    }
                })

        if not vectors_to_upsert:
            return jsonify({
                "error": "No vectors were created for upserting. Check embedding process."
            }), 400

        # Batch upsert to Pinecone
        pinecone_index.upsert(vectors=vectors_to_upsert)
        
        return jsonify({
            "message": "Successfully processed repo",
            "index_name": index_name,
            "sections_processed": len(vectors_to_upsert),
            "embedding_dimension": len(vectors_to_upsert[0]["values"]) if vectors_to_upsert else 0,
            "sections": [
                {"type": section["type"], "title": section["title"]} 
                for section in repo_data
            ]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@app.route("/query", methods=['POST'])
def query_docs():
    try:
        print("Received query request")
        # Get question and repo_url
        question = request.json.get('question')
        repo_url = request.json.get('repo_url')
        
        if not question or not repo_url:
            return jsonify({"error": "Missing question or repo URL"}), 400

        print(f"Processing question: {question} for repo: {repo_url}")

        index_name = f"github-helper-index"


        # Create embedding for question
        question_embedding = get_embedding(question)
        if not question_embedding:
            return jsonify({"error": "Failed to create embedding for question"}), 500

        # Setup Pinecone
        pinecone_index = pc.Index(index_name)
        results = pinecone_index.query(
            vector=question_embedding,
            top_k=3,
            include_metadata=True
        )

        print(f"Found {len(results['matches'])} relevant sections")

        # Get relevant content
        relevant_content = [match["metadata"]["content"] for match in results["matches"]]

        # Setup NVIDIA LLM client
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )

        # Create prompt and get response
        prompt = f"""Based on the following context from a GitHub repository:
        {' '.join(relevant_content)}
        
        Please answer this question: {question}
        
        Provide a clear and concise answer based only on the context provided.
        """

        completion = client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        answer = completion.choices[0].message.content
        
        def format_code_blocks(text):
            return re.sub(
                r'`([\s\S]+?)`',
                lambda match: f'```\n{match.group(1)}\n```',
                text
            )

        formatted_answer = format_code_blocks(answer)

        return jsonify({
            "question": question,
            "answer": formatted_answer,
            "sources": [match["metadata"]["title"] for match in results["matches"]]
        })

    except Exception as e:
        print(f"Error in query_docs: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
    



