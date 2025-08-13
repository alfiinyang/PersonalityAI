import random # Needed for random.random() if used implicitly or for reproducibility tests
from personalityai.Person import Person
from personalityai.persona import Persona # Although Person imports Persona, explicit import can be useful if these functions ever directly interact with Persona objects.

class MissingAttributeError(Exception):
    """Custom exception for missing required attributes."""
    pass

def response_collector(prompts: list, person: Person, collect: [str, list] = "anthro", chat_history: str = '', persist: bool = False):
    """
    Function for collecting anthropomorphic agents' responses.
    Sets `referee` temperature to medium (0.5), generates responses, and restores original `referee` temperature.
    Returns a `list` of `tuples` of equal length as `prompts`, containing bi-directional responses from each anthropomorphic agent. E.g.: `[("angel", "devil"), ("angel", "devil")]`.

    Args:
    `prompts`: `list` of `str` containing user's successive prompts. Used when `chat_history` is empty.
    `person`: `Person` object to be prompted. Used with `prompts` arg.
    `collect`: `str` or `list` of `str` containing agents to collect responses from.
               - "anthro" for persona agents (returns list of tuples).
               - "user" for user prompts (returns list of strings).
               - ["user", "anthro"] for both (returns a tuple with "user" in index 0).
               Used with `chat_history` arg.
    `chat_history`: `str` containing a conversation between user and `Person` object;
                    can also contain persona agents responses. E.g. `chat_history = Person.thoughts()`.
                    Used with `collect` arg.
    `persist`: `bool`; True to enable Person object maintain history of conversation. Used with `prompts` and `person`.
    """

    angelic_responses = []
    devilish_responses = []
    user_prompt_list = [] # Renamed to avoid conflict with function parameter `user_prompt` in ref_response_collector

    ### use user defined prompts to generate responses if no chat history is provided
    if not chat_history: # Checks if chat_history is empty string
        if not prompts or not isinstance(prompts, list):
            raise TypeError("`prompts` must be of `list` type and contain at least one `str` value when `chat_history` is empty.")

        org_temp = person.referee.temperature # save original temperature for later
        person.referee.temperature = 0.5      # set referee response temperature to medium (0.5)
        person.clear_history()                # clear existing history to prevent yanking conversation

        ### prompt model and collect responses from individual anthropomorph
        for prompt in prompts:
            person.answer(prompt)

        ### collect each anthropomorph's responses
        responses = person.thoughts().split('\n')

        for item in responses:
            if item.startswith('Angel'):
                angelic_responses.append(item.split('Angel: ')[1].strip()) # .strip() to remove leading/trailing whitespace
            elif item.startswith('Devil'): # Use elif to ensure an item is only processed once
                devilish_responses.append(item.split('Devil: ')[1].strip())

        ### clear_history and restore original temperature if `persist` is set to False
        if not persist:
            person.clear_history()
            person.referee.temperature = org_temp     # restore originally set temperature

        # Ensure lists are of equal length before zipping, handle potential mismatches gracefully
        min_len = min(len(angelic_responses), len(devilish_responses))
        return list(zip(angelic_responses[:min_len], devilish_responses[:min_len]))

    ### extract responses if chat_history is provided
    elif isinstance(chat_history, str) and len(chat_history) > 0:
        ### raise TypeErrors and MissingAttributesErrors
        if not isinstance(collect, (list, str)):
            raise TypeError("`collect` must be of `list` or `str` type.")

        if isinstance(collect, list):
            if "anthro" not in collect or "user" not in collect or len(collect) != 2:
                raise ValueError("`collect` list must contain exactly 'anthro' and 'user'.")
            else:
                ### collect both user prompts and anthropomorph responses from chat_history
                for item in chat_history.split('\n'):
                    if item.startswith('Angel:'):
                        angelic_responses.append(item.split('Angel: ')[1].strip())
                    elif item.startswith('Devil:'):
                        devilish_responses.append(item.split('Devil: ')[1].strip())
                    elif item.startswith('user:'):
                        user_prompt_list.append(item.split('user: ')[1].strip())
                min_len = min(len(angelic_responses), len(devilish_responses))
                return user_prompt_list, list(zip(angelic_responses[:min_len], devilish_responses[:min_len]))

        elif isinstance(collect, str):
            ### collect only anthropomorphs responses from chat_history
            if collect == "anthro":
                for item in chat_history.split('\n'):
                    if item.startswith('Angel:'):
                        angelic_responses.append(item.split('Angel: ')[1].strip())
                    elif item.startswith('Devil:'):
                        devilish_responses.append(item.split('Devil: ')[1].strip())
                min_len = min(len(angelic_responses), len(devilish_responses))
                return list(zip(angelic_responses[:min_len], devilish_responses[:min_len]))

            ### collect only user prompts from chat_history
            elif collect == "user":
                for item in chat_history.split('\n'):
                    if item.startswith('user:'):
                        user_prompt_list.append(item.split('user: ')[1].strip())
                return user_prompt_list
            else:
                raise ValueError("`collect` string must be 'anthro' or 'user'.")
    else:
        raise TypeError("`chat_history` must be a non-empty `str` when provided.")


def ref_response_collector(person: Person, user_prompt: list, choices: list, temp: dict = None, rp: dict = None, printout: bool = False, chat_history: dict = None, bypass: bool = False, cdisplay: bool = False):
    """
    Function for collecting responses of `referee` `Persona` object of a `Person` instance at different temperatures.
    Iterates over `temp` (or `rp`), which is a `dict` containing various `float` temperatures (or repeat penalties).
    Returns a `dict` of `lists` of responses at each defined temperature/rp. E.g.: `{'lo': ["x", "y"], 'hi': ["v", "w"]}`.

    N/B: `user_prompt` and `choices` must be same length when provided.

    Args:
    `person`: `Person` object to be prompted.
    `user_prompt`: `list` of `str` containing user defined prompts. Must be same as defined for `response_collector()`.
    `choices`: `list` of `tuple` containing bi-directional responses of anthropomorphic agents or personas.
               Each tuple corresponds to the choices for one user prompt.
    `temp`: `dict` containing temperatures to iterate over (e.g., `{'Low': 0.2, 'Mid': 0.5, 'High': 0.8}`).
    `rp`: `dict` containing repeat penalties to iterate over. (Currently not used in Persona.respond, but kept for future use if needed).
    `printout`: `bool`; optional; If True, prints out generated responses during collection.
    `bypass`: `bool`; optional; `True` to use external `choices` instead of generating internal anthropomorph responses.
    `cdisplay`: `bool`; optional; `True` to display internal cognitive processes during `person.answer()` calls.
    `chat_history`: `dict`; optional; contains `Person` object name as key and `Person.thoughts()` string
                    (or `str` containing anthropomorphs' responses) as value.
                    Key must match anthropomorph name in `Person.thoughts()` (e.g., `{'Alex': '...'}`).
    """
    if temp is None:
        temp = {}
    if rp is None:
        rp = {}
    if chat_history is None:
        chat_history = {}

    ### collect `Person` object name if chat_history is provided
    agent_name = list(chat_history.keys())[0] if chat_history else None

    ### if no chat_history, generate referee responses with user_prompt and choices provided
    if not chat_history:
        if not user_prompt or not choices or len(user_prompt) != len(choices):
            raise ValueError("`user_prompt` and `choices` must be non-empty lists of the same length when `chat_history` is not provided.")

        person.clear_history()
        ref_collector = temp.copy() # Use temp if available, otherwise rp.copy()
        org_temp = person.referee.temperature
        # org_rp = person.referee.rp # uncomment if rp is actively used

        ### generate referee responses for each temperature level
        for lvl in ref_collector:
            person.referee.temperature = ref_collector[lvl]
            # person.referee.rp = ref_collector[lvl] # uncomment if rp is actively used

            print(f'Generating responses for Referee at temperature of {person.referee.temperature}...')

            current_lvl_responses = [] # Store responses for the current temperature level

            for index, prompt in enumerate(user_prompt):
                if printout and bypass:
                    print(f"user: {prompt}")
                    print(f"Angel: {choices[index][0]}")
                    print(f"Devil: {choices[index][1]}")
                    # Capture the answer to store it
                    ans = person.answer(prompt=prompt, bypass=bypass, choices=choices[index], cdisplay=cdisplay)
                    print(f"{person.name}: {ans}")
                    current_lvl_responses.append(ans) # Add the answer to the list
                elif not printout and bypass:
                    # Capture the answer to store it
                    ans = person.answer(prompt=prompt, bypass=bypass, choices=choices[index], cdisplay=cdisplay)
                    current_lvl_responses.append(ans) # Add the answer to the list
                elif not bypass: # generate responses internally
                    print(f'prompting...: {index} with "{prompt}"')
                    # Capture the answer to store it
                    ans = person.answer(prompt=prompt, bypass=bypass, cdisplay=cdisplay)
                    current_lvl_responses.append(ans) # Add the answer to the list

            # Collect and store generated referee responses
            if cdisplay:
                print('collecting final responses for this temperature level...')

            # The current_lvl_responses already contains the direct answers from person.answer()
            # No need to parse person.thoughts() if we directly captured the answer from person.answer()
            # However, if Person.answer() internally clears history before returning,
            # we might need person.thoughts() right after each call if we want all internal thoughts.
            # Assuming person.answer() returns the final answer directly as implemented in Person.py,
            # we can just use the captured `ans` for `final_responses`.

            # If the intent is to capture the *referee's* specific output from `person.thoughts()`
            # after all prompts for a given temp level:
            # responses_from_thoughts = person.thoughts().split('\n')
            # final_responses_parsed = []
            # for item in responses_from_thoughts:
            #     if item.startswith(person.name):
            #         final_responses_parsed.append(item.split(f'{person.name}: ')[1].strip())
            # ref_collector[lvl] = final_responses_parsed
            # Simpler: if `person.answer` returns the final referee answer, use `current_lvl_responses` directly.
            ref_collector[lvl] = current_lvl_responses


            person.clear_history() # Clear history for the next temperature level
            if cdisplay:
                print('final responses collected for this temperature level!')

        person.referee.temperature = org_temp
        # person.referee.rp = org_rp # uncomment if rp is actively used
        return ref_collector

    ### if chat_history is provided, collect referee responses from provided chat history
    elif agent_name and isinstance(chat_history.get(agent_name), str):
        referee_responses = []
        for item in chat_history[agent_name].split('\n'):
            if item.startswith(f'{agent_name}:'):
                referee_responses.append(item.split(f'{agent_name}: ')[1].strip())
        return referee_responses
    else:
        raise TypeError("`chat_history` must be a `dict` with the `Person` object's name as a key and a `str` containing thoughts as its value.")

