import yaml
from jinja2 import Template
import os
from pathlib import Path

# HTML template using Jinja2 for flexible rendering
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: white;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            padding: 10px;
            gap: 10px;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            width: 235px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .card-header {
            background-color: #1C5D99;
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .card-content {
            padding: 5px;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2px;
            margin-bottom: 10px;
            align-items: center;
        }
        .greek-text {
            font-size: 0.9em;
            font-weight: 500;
        }
        .english-text {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
            text-align: right;
        }

        @media print {
            @page {
                margin: 1cm;
                size: A4 landscape;
            }

            body {
                margin: 0;
            }

            .card {
                break-inside: avoid;
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    {% for verb in verbs %}
    <div class="card">
        <div class="card-header">{{ verb.verb }}</div>
        <div class="card-content">
            {% for tense_name, forms in verb.tenses.items() %}
            <div class="row">
                <div class="greek-text">{{ forms[0].greek }}</div>
                <div class="english-text">{% if language != 'english' or tense_name not in ["imperative_negation_plural", "imperative_simple_plural"] %}{{ forms[0][language] | replace(" (singular)", "") | replace(" (plural)", "") }}{% endif %}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""


def load_yaml_files(verbs_dir):
    """
    Load and merge all YAML files from the verbs directory

    :param verbs_dir: Path to the directory containing verb YAML files
    :return: List of verb dictionaries
    """
    verbs = []
    verbs_path = Path(verbs_dir)

    # Iterate through all YAML files in the verbs directory
    for yaml_file in sorted(verbs_path.glob("*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            verb_data = yaml.safe_load(f)
            if isinstance(verb_data, list):
                verbs.extend(verb_data)
            else:
                verbs.append(verb_data)

    return verbs


def generate_html_from_yaml(
    verbs_dir="verbs", output_file="verbs.html", page_title="Greek Verb Conjugations", language='english'
):
    """
    Generate HTML page from all YAML files in the verbs directory

    :param verbs_dir: Directory containing the YAML files
    :param output_file: Path to save the generated HTML file
    :param page_title: Title of the HTML page
    """
    # Load all verb data from YAML files
    verb_data = load_yaml_files(verbs_dir)

    # Filter out specified tenses
    filtered_tenses = [
        "imperfect_past_tense",
        "future_continuous_tense",
        "continuous_subjunctive_mood",
        "simple_subjunctive_mood",
        "imperative_continuous_singular",
        "imperative_continuous_plural",
    ]

    # Create a new verbs list with filtered tenses
    filtered_verbs = []
    for verb in verb_data:
        filtered_verb = verb.copy()
        filtered_verb["tenses"] = {
            k: v for k, v in verb["tenses"].items() if k not in filtered_tenses
        }
        filtered_verbs.append(filtered_verb)

    # Create Jinja2 template
    template = Template(HTML_TEMPLATE)

    # Render the template
    html_output = template.render(language=language, verbs=filtered_verbs, page_title=page_title)

    # Write the HTML file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"HTML file generated: {output_file}")


# Example usage
if __name__ == "__main__":
    Path("pages").mkdir(parents=True, exist_ok=True)
    generate_html_from_yaml(output_file='pages/verbs_en.html', language='english')
    generate_html_from_yaml(output_file='pages/verbs_ru.html', language='russian')
