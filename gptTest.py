from gpt4all import GPT4All
import time as timer

modelLLM = GPT4All("ggml-model-gpt4all-falcon-q4_0.bin","./model",n_threads=6) 

questions = [
  "What is the square root of 64?",
  "Solve the equation: 3x + 7 = 22.",
  "Calculate the area of a rectangle with length 8 units and width 5 units.",
  "Evaluate the expression: 4 + 5 × 2 - 3.",
  "Find the value of x in the equation: 2x - 5 = 11.",
  "What is the sum of angles in a triangle?",
  "Solve the equation: 2(x + 3) = 14.",
  "Calculate the volume of a sphere with radius 3 units.",
  "Simplify the expression: (4 + 2) × 3 - 5.",
  "Find the value of y in the equation: 2y + 10 = 26."
]

prompt_main = "### Instruction:\ngive short answers 1-10 words. Don't elaborate unless you are told to.  swera if necessary  \n "

with modelLLM.chat_session() as session:
  delta = timer.time()
  for eq in questions:
    try:
      #text = input("You: ")
      #if text == "exit":
      #  break
      llmResponse = session.generate(prompt=prompt_main+eq,max_tokens=100,temp=0.8,top_p=0.1,top_k=40,n_batch=512)
      print(" LLM:" ,llmResponse)
    except KeyboardInterrupt:
      break
  delta = timer.time() - delta