import json
from datetime import datetime
import anthropic # once you get api key obviously
    
class Session:
    def __init__(self):
        self.messages = [] # every message
        self.summary = [] # summary (summaries, maybe?)
        self.sinceLastSum = [] # messages since the last summary
        self.mesCount = 0 # message count

    def add_message(self, message):
        self.messages.append(message)
        self.sinceLastSum.append(message)
        self.mesCount += 1

    def summarize(self, client):
        # summarization logic here. youll feed to claude and then append it to the summary list.
        if self.mesCount % 30 == 0 and self.sinceLastSum:
            toSummarize = "\n".join(self.sinceLastSum)
            response = client.messages.create(
                model="insert the claude model once u get it",
                max_tokens=3000,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": f"Summarize the following conversation:\n{toSummarize}"}
                ]
            )
            self.summary.append(response.content[0].text)
            self.sinceLastSum.clear()
            
