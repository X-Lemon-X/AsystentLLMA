from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


template = """Question: {question}

Answer: give short answer 1-10 words. don't elaborate unless you are told to. answer if necessary"""

prompt = PromptTemplate(template=template, input_variables=["question"])

local_path = (
    "./model/nous-hermes-13b.ggmlv3.q4_0.bin"  # replace with your desired local file path
)

callbacks = [StreamingStdOutCallbackHandler()]

# Verbose is required to pass to the callback manager
llm = GPT4All(model=local_path, callbacks=callbacks, verbose=True)

# If you want to use a custom model add the backend parameter
# Check https://docs.gpt4all.io/gpt4all_python.html for supported backends
llm = GPT4All(model=local_path, backend="gptj", callbacks=callbacks, verbose=True)

llm_chain = LLMChain(prompt=prompt, llm=llm)

while True:
  try:
    question = input("You: ")
    if question == "exit":
      break
    print(llm_chain.run(question))
  except KeyboardInterrupt:
    break
  except BaseException as e:
    break
