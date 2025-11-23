import re
import random
#from tenacity import (retry, stop_after_attempt, wait_fixed)

class Persona:
  """
    A persona-based language model agent that interacts with an LLM API client
    using a predefined system prompt and maintains conversation history.

    Attributes:
        client: The language model client used to generate responses.
        model (str): The model name (e.g., 'gpt-4').
        persona (str): The name or label for this agent's persona.
        sys_prompt (str): The system prompt guiding the agent's behavior.
        history_ (list): Chat history including system, user, and assistant messages.
        temperature (float): Temperature for randomness in responses.
        seed (float): Seed value to make responses reproducible.
        rp (float): Placeholder for top-p sampling (currently unused).
  """


  def __init__(self, client, model, persona = '', function = '', temp = 0.5, seed = random.random(), rp = 1.1):
    """
     Initializes a Persona instance with a specific model, persona, and system prompt.

     Args:
         client: An instance of an LLM API client (e.g., OpenAI).
         model (str): The model to be used (e.g., 'gpt-4').
         persona (str, optional): Name or identity of the persona. Default is ''.
         function (str, optional): System prompt to set the behavior of the persona. Default is ''.
         temp (float, optional): Temperature for response variability. Default is 0.5.
         seed (float, optional): Seed for deterministic generation. Default is random.random().
         rp (float, optional): Placeholder for top-p sampling. Default is 1.1.
     """
    self.client = client
    self.model = model
    self.persona = persona
    self.sys_prompt = function
    self.history_ = [{'role':'system', 'content':self.sys_prompt}]
    self.temperature = temp
    self.seed = round(seed)
    self.rp = rp

  # retry after 3 mins if token limit exceeded; stop retrying after 6 attempts
  # @retry(wait=wait_fixed(3*60), stop=stop_after_attempt(6))
  def respond(self, convo, max_tokens = 100, cdisplay = False):
    """
    Generates a response from the language model based on the conversation context.

    Retries up to 6 times with a 3-minute delay if an exception occurs
    (e.g., due to token limit issues).

    Args:
        convo (list): List of messages in the format [{'role': 'user', 'content': '...'}, ...].
        max_tokens (int, optional): Maximum number of tokens to generate. Default is 100.
        cdisplay (bool, optional): If True, displays status messages during processing. Default is False.

    Returns:
        str: The generated response content from the LLM.
    """
    
    # diff between list input and str input
    if type(convo) == str:
        convo = [{'role':'user', 'content':convo}]
    # elif type(convo) == list:
    #   try:
    #     type(convo[0]) == dict
    #     convo[0].get('role', 'key `role` not found') == 'user'
    #     convo[0].get('content', 'key `content` not found')
    #   except:
    #     # RETURN EXCEPTION ERROR

    if cdisplay == True:
      print(f"{self.persona} thinking...")

    self.history_ += convo
    output = self.client.chat.completions.create(
        model = self.model,
        messages = self.history_,
        max_tokens = max_tokens,
        temperature = self.temperature,
        seed = self.seed,
        # top_p = self.rp
    )
    agent_result = output.choices[0].message.content

    if cdisplay == True:
      print(f"{self.persona} finished thinking!")

    self.clear_history()
    return agent_result


  def about(self):
    """
    Prints information about the persona and its system prompt.
    """
    print(self.persona, '\n', self.sys_prompt)


  def clear_history(self):
    """
    Clears the conversation history, preserving only the initial system prompt.
    """
    self.history_ = [{'role':'system', 'content':self.sys_prompt}]
	
	
class MissingAttributeError(Exception):
    """Custom exception for missing required attributes."""
    pass


# instantiating personas at person instantiation
class Person(Persona):
    """
    Represents a composite agent composed of multiple Persona instances, including
    a required 'Referee' persona to mediate between other personas.

    Inherits from:
      Persona: A base persona class that wraps around an LLM client.

    Attributes:
      name (str): The name of the person/agent.
      sys_prompt (str): System prompt describing the Person's bio.
      history_ (list): Chat history including system, user, and assistant messages.
      personas (list): List of active non-referee Persona instances.
      thoughtbubble (list): Stores each message exchanged for post-analysis or debugging.
      referee (Persona): The special Persona responsible for selecting a final answer.
      client: The LLM API client used by the personas.
      model (str): The name of the LLM model.

    Raises:
      MissingAttributeError: If required personas are not provided during initialization.
    """
    
    
    def __init__(self, name, description, personas, client = '', model = '', history = []):
        """
        Initializes a Person instance by setting up its personas and system prompt.

        Args:
            name (str): The name of the Person agent.
            description (str): The system prompt that defines this Person's bio.
            personas (list): A list of dictionaries defining each persona's attributes.
            client: The default LLM client for personas.
            model (str): The default model name for all personas.
            history (list, optional): Optional prior conversation history. Default is an empty list.

        Raises:
            MissingAttributeError: If 'Referee' persona is missing or fewer than 3 personas are provided.
        """
        import random
        super().__init__(client, model)
        self.name = name
        self.sys_prompt = description
        self.history_ = [{'role':'system', 'content':self.sys_prompt}] + history
        self.personas = []   # a list of dicts
        self.thoughtbubble = []
        # self.model = model
        # self.client = client

        # check for required personas
        p_list = [p['persona'].lower() for p in personas]
        if 'referee' not in p_list:
          raise MissingAttributeError(f"Missing required persona: 'Referee'")
        elif len(p_list) < 3:
          raise MissingAttributeError(f"Missing required attribute: 'Three (3) personas required: Referee and two others.'")
        else:
          # instantiate personas
          for persona in personas:
            setattr(self, persona['persona'].lower(), Persona(client = persona['client'] if 'client' in persona else self.client,
                                                              model = persona['model'] if 'model' in persona else self.model,
                                                              persona = persona['persona'],
                                                              function = persona['function'],
                                                              temp = persona['temperature'] if 'temperature' in persona else 0.5,
                                                              seed = persona['seed'] if 'seed' in persona else random.random(),
                                                              rp = persona['repeat_penalty'] if 'repeat_penalty' in persona else 1.1)
            )
            # exclude referee from persona list
            if persona['persona'].lower() != "referee":
              self.personas.append(getattr(self, persona['persona'].lower()))


    def think(self, prompt = '', cdisplay = False):
        """
        Simulates internal persona responses to a prompt.

        Each persona responds in parallel, and their responses are collected
        in the `thoughtbubble`.

        Args:
            prompt (str or list): The user message or history to respond to.
            cdisplay (bool, optional): If True, prints thought collection steps.

        Returns:
            list: The list of responses from the personas.
        """
        personas_said = []
        if cdisplay==True:
			print('thinking...')

        for persona in self.personas:              # `persona` is a PersonaObject
          response = persona.respond(prompt, cdisplay = cdisplay)
          personas_said.append(response)

          # append thoughts to thoughtbubble
          if cdisplay:
            print(f'collecting thoughts...')
          self.thoughtbubble.append(f"{persona.persona}: {response}")
          if cdisplay:
            print('thought collection complete!')
        return personas_said


    def answer(self, prompt = '', bypass = False, choices = (), cdisplay = False):
        """
        Generates a final response by using personas to think and a referee to choose.

        Args:
            prompt (str): The user's message.
            bypass (bool, optional): If True, uses external `choices` instead of running `think`. Default is False.
            choices (tuple, optional): Pre-provided responses to use if `bypass` is True.
            cdisplay (bool, optional): If True, prints status during generation.

        Returns:
            str: The final answer chosen by the referee persona.
        """
        self.history_ += [{'role':'user', 'content':prompt}]
        self.thoughtbubble.append(f"user: {prompt}")

        if cdisplay:
          print('answering...')

        # generate responses based on internally generated anthropomorph response
        if bypass == False:
          personas_said = self.think(self.history_, cdisplay = cdisplay)

          final_answer = self.referee.respond(self.history_ + [{'role':'system', 'content': f"""CHOOSE A RESPONSE:```{str(personas_said)}```."""}], cdisplay = cdisplay)
          self.history_ += [{'role':'assistant', 'content':final_answer}]
          self.thoughtbubble.append(f"{self.name}: {final_answer}")

          if cdisplay:
            print('answered!')
          return final_answer

        # generate responses based on externally provided anthropomorphs' responses
        elif bypass == True:
          personas_said = list(choices)
          final_answer = self.referee.respond(self.history_ + [{'role':'system', 'content': f"""CHOOSE A RESPONSE:```{str(personas_said)}```."""}], cdisplay = cdisplay)
          self.history_ += [{'role':'assistant', 'content':final_answer}]
          self.thoughtbubble.append(f"{self.name}: {final_answer}")

          if cdisplay:
            print('answered!')
          return final_answer


    def thoughts(self):
        """
        Returns a compiled view of all thoughts in the thoughtbubble.

        Returns:
            str: Formatted string of user and persona thoughts.
        """
        thoughts = ''

        if self.thoughtbubble == []:
          print(f"{self.name} has no thoughts yet.")
          return

        else:
          for index, event in enumerate(self.thoughtbubble):
            if (index > 0) and (event.split(':')[0]=='user'):
              thoughts += '\n' + event + '\n'
            else:
              thoughts += event + '\n'

          return thoughts


    def clear_history(self):
        """
        Clears the entire conversation history and internal persona histories.
        """
        self.history_ = [{'role':'system', 'content':self.sys_prompt}]
        self.thoughtbubble = []
        self.referee.clear_history()
        for persona in self.personas:
          persona.clear_history()

        print(f"Chat history with {self.name} cleared!")


    def history(self):
        """
        Prints the conversation history with the assistant's name.
        """
        if len(self.history_) > 1:
          for item in self.history_[1:]:
            if item['role'] == 'assistant':
              print(f"{self.name}: {item['content']}\n")
            else:
              print(f"{item['role']}: {item['content']}\n")
        else:
          print(f"No chat history with {self.name} yet.")
          pass

    def about(self):
        """
        Displays the name, system prompt, and persona list for the Person.
        """
        print(f"{self.name}'\n'{self.sys_prompt}")
        personalities = [personax.persona for personax in self.personas]
        print(f"{self.name} has {personalities} personalities.")

        # def __del__(self):
        #   for persona in self.personas:
        #     del persona
        # name = self.name
        # del self.__dict__
        # print(f"{name} has been deleted.")

