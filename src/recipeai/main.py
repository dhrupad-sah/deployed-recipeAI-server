from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_recipe")
async def get_recipe(
    ingredients: str = Body(...),
    instructions: str = Body(default=None)
):
    try:
        recipe = get_recipe_from_llm(ingredients, instructions)
        return {"recipe": recipe}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_recipe_from_llm(ingredients, instructions):
    url = "https://gemma.us.gaianet.network/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    system_content = "You are a trained chef that knows about recipes with any ingredients given. Provide a recipe name, ingredients list, and step-by-step instructions."
    
    user_content = f"I have these ingredients: {ingredients}. What recipe can I make? Please provide the recipe name, ingredients list, and step-by-step instructions."
    
    if instructions:
        user_content += f" Also, please consider these special instructions: {instructions}."
    else:
        user_content += " There are no special instructions to consider."

    data = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        "model": "gemma"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: Unable to fetch recipe from LLM. Status code: {response.status_code}")
