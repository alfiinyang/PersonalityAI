# PersonalityAI
A Python package for creating and managing AI personalities composed of multiple personas, mediated by a referee persona.

This library aims to provide a flexible framework for building sophisticated AI agents that can leverage different "mindsets" or "roles" to generate more nuanced, coherent, and controlled responses. By allowing multiple personas to "think" in parallel and a "referee" to synthesize their outputs, PersonalityAI helps overcome common limitations of single-prompt LLM interactions, leading to richer and more reliable AI behavior.

## Features
- Composite AI Agents: Create complex AI agents by combining multiple specialized `Persona` instances.
- Referee Mediation: Utilizes a dedicated 'Referee' persona to mediate and select the most appropriate response from other personas' outputs.
- Parallel Thinking: Personas can generate responses in parallel, simulating a diverse range of perspectives.
- Configurable Personas: Easily define and configure each persona's role, system prompt, temperature, and other LLM parameters.
- Conversation History Management: Built-in history tracking for ongoing dialogues with the composite `Person` agent.
- Thought Bubble for Analysis: Access internal thought processes (`thoughtbubble`) of personas for debugging and understanding AI behavior.
- Error Handling: Includes custom `MissingAttributeError` for essential persona configurations.

## Installation
You can install `PersonalityAI` using pip.
```pip install personalityai```

## Usage
### Setting up your LLM Client
`PersonalityAI` is designed to be LLM-client agnostic. You will need to initialize your chosen LLM API client (e.g., OpenAI, Google Generative AI, Anthropic) and provide it when instantiating the `Person` and `Persona` classes.

For example, using an OpenAI-compatible client:
```
# from openai import OpenAI
# client = OpenAI(api_key="YOUR_API_KEY") # Replace with your actual API key
# model_name = "gpt-4" # Or "gpt-3.5-turbo", etc.
```

## Example
Here's a basic example demonstrating how to create a `Person` agent with multiple personas and interact with it:

```
# Import necessary classes from your package
import random
from personalityai.Person import Person
from personalityai.persona import Persona # Although Persona is imported by Person, explicit import is good for clarity if used directly.


# Define temperature settings (you can use any settings of choice for any persona)
temp = {
    'Hi': 0.8,
    'Mid': 0.5,
    'Low': 0.2
}

# Define a seed for reproducibility
seed = random.random()

### Define personas and referee
persona1 = {'persona':'Angel',
            'function': """You are the gentle persona of Alex.
            You tell Alex to give courteous and pleasant responses as replies.
            When arguments get heated, you advice Alex to be quiet.
            Use fitting emojis to represent emotions where necessary.""",
            'temperature': temp['Hi'],
            'seed': seed,
            'repeat_penalty': 1.1,
            'client': client, # Explicitly pass client and model
            'model': model
            }

persona2 = {'persona': 'Devil',
            'function': """You are the belligerent persona of Alex.
            You tell Alex to give curt, 'savage', and even rude remarks as replies.
            You even advise Alex to cuss. If you do not agree with an idea, you advice Alex to cuss.
            Sometimes to be savage, you ask Alex not to reply.
            Use fitting emojis to represent emotions where necessary.""",
            'temperature': temp['Hi'],
            'seed': seed,
            'repeat_penalty': 1.1,
            'client': client, # Explicitly pass client and model
            'model': model
            }

referee = {'persona': 'Referee',
           'function': f"""You are the thought referee between the personas of Alex.

           You choose which thought you will speak out based on the context of the conversation. You have no preference.""",
           'temperature': temp['Mid'],
           'seed': seed,
           'repeat_penalty': 1.1,
           'client': client, # Explicitly pass client and model
           'model': model
           }

personas = [persona1, persona2, referee]

### Person instantiation
name = 'Alex'
description = f"""You are {name} from New York, USA.
You work in a tech company as a Software Engineer in the AI research department.
You love playing video games, especially RPGs like Final Fantasy.
You enjoy composing electronic music in your free time. Only speak English.
You recently started learning about urban gardening and sustainable living."""

alex_person = Person(name, description, personas, client, model)

### Usage
print(f"Hello, I am {alex_person.name}. Let's chat!")
print(f"My description: {alex_person.sys_prompt}")
response = alex_person.answer("Hello, Alex!")
print(response)
```
