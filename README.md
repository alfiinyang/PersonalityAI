# PersonalityAI

A Python package for creating and managing AI personalities composed of multiple personas, mediated by a referee persona.

This library aims to provide a flexible framework for building sophisticated AI agents that can leverage different "mindsets" or "roles" to generate more nuanced, coherent, and controlled responses.

By allowing multiple personas to "think" in parallel and a "referee" to synthesize their outputs, PersonalityAI helps overcome common limitations of single-prompt LLM interactions, leading to richer and more reliable AI behavior.

## Features
- **Composite AI Agents**: Create complex AI agents by combining multiple specialized Persona instances.
- **Referee Mediation**: Utilizes a dedicated 'Referee' persona to mediate and select the most appropriate response from other personas' outputs.
- **Parallel Thinking**: Personas can generate responses in parallel, simulating a diverse range of perspectives.
- **Configurable Personas**: Easily define and configure each persona's role, system prompt, temperature, and other LLM parameters.
- **Conversation History Management**: Built-in history tracking for ongoing dialogues with the composite Person agent.
- **Thought Bubble for Analysis**: Access internal thought processes (thoughtbubble) of personas for debugging and understanding AI behavior.
- **Error Handling**: Includes custom `MissingAttributeError` for essential persona configurations.
- **Installation**: You can install PersonalityAI using pip `pip install personalityai`

## Usage
### Setting up your LLM Client
PersonalityAI is designed to be LLM-client agnostic.

You will need to initialize your chosen LLM API client (e.g., OpenAI, Google Generative AI, Anthropic) and provide it when instantiating the Person and Persona classes.

For example, using an OpenAI-compatible client:

```
from openai import OpenAI
client = OpenAI(api_key="YOUR_API_KEY") # Replace with your actual API key
model_name = "gpt-4" # Or "gpt-3.5-turbo", etc.
```

### Example
Here's a basic example demonstrating how to create a Person agent with multiple personas and interact with it:
```
# Import necessary classes from your package
from personality import Person
from personality import Persona # Although Persona is imported by Person, explicit import is good for clarity if used directly.


# Define temperature settings (you can use any settings of choice for any persona)
temp = {
    'Hi': 0.8,
    'Mid': 0.5,
    'Low': 0.2
}

# Define a seed for reproducibility
seed = random.random()

### Define personas (a minimum of 2) and referee
persona1 = {'persona':'Angel',
            'function': """You are the gentle persona of Alex.
            You tell Alex to give courteous and pleasant responses as replies.
            When arguments get heated, you advice Alex to be quiet.
            Use fitting emojis to represent emotions where necessary.""",
            'temperature': temp['Hi'],
            'seed': seed,
            'client': client, # optional
            'model': model # optional
            }

persona2 = {'persona': 'Devil',
            'function': """You are the belligerent persona of Alex.
            You tell Alex to give curt, 'savage', and even rude remarks as replies.
            You even advise Alex to cuss. If you do not agree with an idea, you advice Alex to cuss.
            Sometimes to be savage, you ask Alex not to reply.
            Use fitting emojis to represent emotions where necessary.""",
            'temperature': temp['Hi'],
            'seed': seed,
            'client': client, # optional
            'model': # optional
            }

referee = {'persona': 'Referee',
           'function': f"""You are the thought referee between the personas of Alex.
           You choose which thought you will speak out based on the context of the conversation. You have no preference.""",
           'temperature': temp['Mid'],
           'seed': seed,
           'client': client, # optional
           'model': model # optional
           }

personas = [persona1, persona2, referee]

### Person instantiation
name = 'Alex'
description = f"""You are {name} from New York, USA.
You work in a tech company as a Software Engineer in the AI research department.
You love playing video games, especially RPGs like Final Fantasy.
You enjoy composing electronic music in your free time. Only speak English.
You recently started learning about urban gardening and sustainable living."""

alex_person = Person(name=name, description=description, personas=personas, client=client, model=model) # only specifiy client and model if not already passed in persona dictionaries

### Usage
response = alex_person.answer("Hello, Alex!")
print(response)
```


---

## Experimental Utilities

The `experiments/` directory contains utility functions designed to help you conduct experiments and analyze the behavior of your `Person` and `Persona` agents.

### `response_collector`

This function helps in collecting responses from individual personas (e.g., Angel, Devil) either by prompting a `Person` agent or by parsing its existing thought history.

**Usage:**

```python
from personality import Person
from experiments import response_collector

# Assuming 'alex_person' is an initialized Person object as in the Usage example
# And 'client' and 'model' are your LLM client and model
```
#### Example 1: Generate and collect responses for new prompts
```
prompts = [
    "What's the best way to approach a difficult conversation?",
    "Should one always tell the truth, even if it hurts?"
]

individual_persona_responses = response_collector(
    prompts=prompts,
    person=alex_person,
    persist=False # Clear history after collection
)

print("Individual Persona Responses (Angel, Devil):")

for angel_res, devil_res in individual_persona_responses:
    print(f"  Angel: {angel_res}")
    print(f"  Devil: {devil_res}")
```

#### Example 2: Collect responses from an existing chat history
```
# Gather existing thoughts
existing_thoughts = alex_person.thoughts()
```
- Collect only anthropomorphic responses from the history
```
anthro_responses_from_history = response_collector(
    chat_history=existing_thoughts,
    collect="anthro"
)

print("\nAnthropomorphic Responses from History:")

for angel_res, devil_res in anthro_responses_from_history:
    print(f"  Angel: {angel_res}")
    print(f"  Devil: {devil_res}")
```

- Collect user prompts from the history
```
user_prompts_from_history = response_collector(
    chat_history=existing_thoughts,
    collect="user"
)

print("\nUser Prompts from History:")
for prompt in user_prompts_from_history:
    print(f"  - {prompt}")
```

- Collect both user prompts and anthropomorphic responses
```
user_anthro_from_history = response_collector(
    chat_history=existing_thoughts,
    collect=["user", "anthro"]
)

user_prompts, anthro_responses = user_anthro_from_history

print("\nUser Prompts and Anthropomorphic Responses from History:")

for i, prompt in enumerate(user_prompts):
    print(f"  User: {prompt}")
    print(f"  Angel: {anthro_responses[i][0]}")
    print(f"  Devil: {anthro_responses[i][1]}")
```

```
alex_person.clear_history() # Clear history for future experiments
```


### **`ref_response_collector`**
This function helps in collecting referee responses at different temperatures.

**Usage**
```
from experiments import ref_response_collector

# Assuming Person already exists
```

#### Example 1: Generate referee responses at different temperatures
- Define prompts and persona responses (choices)
```
prompts = [
    "What's the best way to handle criticism?",
    "Should I always tell the truth, even if it hurts?"
]

choices = [
    ("Be kind and listen calmly.", "Ignore them, they don’t matter."), # Angel, Devil
    ("Yes, honesty builds trust.", "No, sometimes lies are better.")
]
```

- Define temperature levels for referee to iterate over
```
temp_levels = {
    'low': 0.2,
    'mid': 0.5,
    'high': 0.9
}
```

- Collect referee responses at multiple temperatures
```
ref_responses = ref_response_collector(
    person=alex,
    user_prompt=prompts,
    choices=choices,
    temp=temp_levels,
    printout=True,
    bypass=True # Use choices. Do not generate anthropomorphic response internally
)

print("\nCollected Referee Responses:")

for lvl, responses in ref_responses.items():
    print(f"\nTemperature: {lvl}")

    for r in responses:
        print(f"  - {r}")
```

#### Example 2: Extract referee responses from existing chat history
```
# Collect responses from chat history instead of regenerating

chat_history = {alex.name: alex.thoughts()}
ref_responses_from_history = ref_response_collector(chat_history=chat_history)

print("\nReferee Responses from Chat History:")

for r in ref_responses_from_history:
    print(f"  - {r}")
```