import langchain_ollama
import llm

academic = llm.LLM(langchain_ollama.OllamaLLM, "deepseek-r1:7b", num_thread = 1, temperature = 0.0)
examiner = ...
support = ...

print(academic.ask_about(""))