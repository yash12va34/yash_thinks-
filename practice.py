"""
mini_agents.py
Pure-Python mini agent framework showing structure, not libraries.
Run: python mini_agents.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, List, Dict, Any, Optional, Callable
import time
import logging
import json
import uuid

# -----------------------------
# 0) logging config (debuggable output)
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# -----------------------------
# 1) domain objects
# -----------------------------
@dataclass
class Task:
    id: str
    goal: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"   # pending | running | done | failed
    result: Optional[str] = None
    error: Optional[str] = None

@dataclass
class Message:
    sender: str
    content: str
    ts: float = field(default_factory=time.time)

# -----------------------------
# 2) memory (append-only log + simple recall)
# -----------------------------
class Memory:
    def __init__(self):
        self.messages: List[Message] = []

    def add(self, sender: str, content: str) -> None:
        self.messages.append(Message(sender, content))

    def recall(self, query: str = "") -> List[Message]:
        if not query:
            return self.messages[-10:]  # last 10
        q = query.lower()
        return [m for m in self.messages if q in m.content.lower()]

# -----------------------------
# 3) tools (simple Protocol interface)
# -----------------------------
class Tool(Protocol):
    name: str
    def __call__(self, **kwargs) -> str: ...

class EchoTool:
    name = "echo"
    def __call__(self, **kwargs) -> str:
        return f"echo: {kwargs.get('text','')}"

class CounterTool:
    name = "counter"
    def __init__(self): self.n = 0 
    def __call__ (self , **kwargs)
       self.n = +1
       return f"count = {self.n}"
   
# base agent 

class agent:
    def __init___(self , name: str , role: str , memory: str , tools: dict[str , tools]| None = none )
        self.name =  name 
        self.role = role 
        self.memory = memory 
        self.tools = tools or {}
        
#reaasoning 

    def plan(self , task: Task) :
         """"Return a tiny plan (list of steps) for the task."""
        steps = [] 
        if "analyze" in task.goal.lower():
            steps = ["recall context " , "run counter" , " summanrize findings" ]
        if "reply" in task.goal.lower():
            steps = [ "echo message" , "finalize reply"] 
        else:
            steps = [ "recall context" , " do generic work " , "save resuilt"]
            logging.debug(f"{self.name}.plan {steps}")
            return steps          
        
        def act(self , steps: str , task: Task)
           """excute one sstep at a time keep deterministic + manageble """
           if step == "recall context":
               past = self.memory.recall(task.conext.get("query" , ""))
               return f"recalled {len(past)} messages"
            if step == "run couter":
                return self.tools["counter"]() if "counter" in self.tool else "no conter"
            if step = "summarize findings":
                return f"smmary of task:{task.id}"
            if step == "echo message":
                return self.tools["echo"](text=task.context.get("text" , "")) if "echo" in self.tools else "ehco"
            if step == "fianlize reply":
                return f"reply ready"
            if step == "work done":
                return f"do generic work"
            if step == "save result":
                return f"saved "
            else:
                return f"unknown step:{step}"
            
# public run 
def run(self, task: Task):
    self.memory.add(self.name, f"start task {task.id } goal:{task.goal}")
    task.status = "running"
    try:
        for step in           bdfsbsdfGS                                                           
                                                                  
                                                                          