class Persona:
  """
    A persona-based language model agent that interacts with an LLM API client
    using a predefined system prompt and maintains conversation history.

    Attributes:
        llm: The language model client used to generate responses.
        model (str): The model name (e.g., 'gpt-4').
        persona (str): The name or label for this agent's persona.
        sys_prompt (str): The system prompt guiding the agent's behavior.
        history_ (list): Chat history including system, user, and assistant messages.
        temperature (float): Temperature for randomness in responses.
        seed (float): Seed value to make responses reproducible.
        rp (float): Placeholder for top-p sampling (currently unused).
  """

  import re
  import random
  #from tenacity import (retry, stop_after_attempt, wait_fixed)

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
    self.llm = client
    self.model = model
    self.persona = persona
    self.sys_prompt = function
    self.history_ = [{'role':'system', 'content':self.sys_prompt}]
    self.temperature = temp
    self.seed = round(seed)
    self.rp = rp

  # retry after 3 mins if token limit exceeded; stop retrying after 6 attempts
  @retry(wait=wait_fixed(3*60), stop=stop_after_attempt(6))
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
    output = self.llm.chat.completions.create(
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