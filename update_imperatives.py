import os
import yaml
from openai import OpenAI
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
print(model)

class ImperativeForms(BaseModel):
    simple_negation_imperative_singular: str
    simple_negation_imperative_plural: str


def get_imperative_negation(verb):
    """Query OpenAI for imperative negation forms of the verb"""
    prompt = f"Make simple negative subjunctive (prohibition) forms of verb {verb}"

    try:
        response = client.beta.chat.completions.parse(
            model=model, 
            messages=[{"role": "user", "content": prompt}],
            response_format=ImperativeForms,
        )
        # Parse the JSON response
        message = response.choices[0].message
        result = message.parsed
        return result
    except Exception as e:
        print(f"Error processing verb {verb}: {str(e)}")
        return None


def process_verb_file(filepath):
    """Process a single verb YAML file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        verb = data[0]['verb']
        print(f"Processing verb: {verb}")

        if data[0]['tenses']["imperative_negation_singular"] is None:
            print("Skipping...")
            return True

        # Get imperative negation forms from OpenAI
        result = get_imperative_negation(verb)
        if not result:
            return False

        simple_negation_imperative_singular = result.simple_negation_imperative_singular.lower()
        simple_negation_imperative_plural = result.simple_negation_imperative_plural.lower()
        # Update the YAML data
        if data[0]['tenses']['imperative_negation_singular'][0]['greek'] != simple_negation_imperative_singular:
            print(f"Changed from {data[0]['tenses']['imperative_negation_singular'][0]['greek']} to {simple_negation_imperative_singular}")
            data[0]['tenses']['imperative_negation_singular'][0]['greek'] = simple_negation_imperative_singular

        if data[0]['tenses']['imperative_negation_plural'][0]['greek'] != simple_negation_imperative_plural:
            print(f"Changed from {data[0]['tenses']['imperative_negation_plural'][0]['greek']} to {simple_negation_imperative_plural}")
            data[0]['tenses']['imperative_negation_plural'][0]['greek'] = simple_negation_imperative_plural

        
        # Save the updated YAML back to file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        return True

    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return False


def main():
    verbs_dir = Path("verbs")
    processed = 0
    errors = 0

    for yaml_file in sorted(verbs_dir.glob("*.yaml")):
        if process_verb_file(yaml_file):
            processed += 1
        else:
            errors += 1
        time.sleep(5)

    print(f"\nProcessing complete. Success: {processed}, Skipped: {errors}")


if __name__ == "__main__":
    main()
