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
    def __call__(self, **kwargs) -> str:
        self.n += 1
        return f"count={self.n}"

# -----------------------------
# 4) base agent
# -----------------------------
class Agent:
    def __init__(self, name: str, role: str, memory: Memory, tools: Dict[str, Tool] | None = None):
        self.name = name
        self.role = role
        self.memory = memory
        self.tools = tools or {}

    # ==== reasoning scaffolds (keep dumb/simple for now) ====
    def plan(self, task: Task) -> List[str]:
        """Return a tiny plan (list of steps) for the task."""
        steps = []
        if "analyze" in task.goal.lower():
            steps = ["recall context", "run counter", "summarize findings"]
        elif "reply" in task.goal.lower():
            steps = ["echo message", "finalize reply"]
        else:
            steps = ["recall context", "do generic work", "save result"]
        logging.debug(f"{self.name}.plan -> {steps}")
        return steps

    def act(self, step: str, task: Task) -> str:
        """Execute one step. Keep it deterministic + testable."""
        if step == "recall context":
            past = self.memory.recall(task.context.get("query",""))
            return f"recalled {len(past)} messages"
        if step == "run counter":
            return self.tools["counter"]() if "counter" in self.tools else "no counter tool"
        if step == "summarize findings":
            return f"summary for task:{task.id}"
        if step == "echo message":
            return self.tools["echo"](text=task.context.get("text","")) if "echo" in self.tools else "no echo tool"
        if step == "finalize reply":
            return "reply ready"
        if step == "do generic work":
            return "work done"
        if step == "save result":
            return "saved"
        return f"unknown step: {step}"

    # ==== public run ====
    def run(self, task: Task) -> Task:
        self.memory.add(self.name, f"start task:{task.id} goal:{task.goal}")
        task.status = "running"
        try:
            for step in self.plan(task):
                out = self.act(step, task)
                self.memory.add(self.name, f"{step} -> {out}")
            task.result = f"{self.name}({self.role}) finished: {task.goal}"
            task.status = "done"
            self.memory.add(self.name, f"done task:{task.id}")
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.memory.add(self.name, f"error task:{task.id} {e}")
        return task

# -----------------------------
# 5) specialized agents (override behavior minimally)
# -----------------------------
class ResearchAgent(Agent):
    def plan(self, task: Task) -> List[str]:
        base = super().plan(task)
        if "research" in task.goal.lower():
            base.insert(1, "annotate sources")
        return base

    def act(self, step: str, task: Task) -> str:
        if step == "annotate sources":
            # fake a “source list”
            task.context["sources"] = ["paper:A", "blog:B"]
            return "added 2 sources"
        return super().act(step, task)

class TaskAgent(Agent):
    def plan(self, task: Task) -> List[str]:
        # split a goal into subtasks (toy version)
        parts = [p.strip() for p in task.goal.split("&&")]
        if len(parts) > 1:
            task.context["subtasks"] = parts
            return ["recall context"] + [f"do:{p}" for p in parts] + ["save result"]
        return super().plan(task)

    def act(self, step: str, task: Task) -> str:
        if step.startswith("do:"):
            return f"completed subtask: {step[3:]}"
        return super().act(step, task)

# -----------------------------
# 6) orchestrator (routes tasks, gathers results, simple policies)
# -----------------------------
class Orchestrator:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.history: List[Task] = []

    def route(self, task: Task) -> Agent:
        goal = task.goal.lower()
        if any(k in goal for k in ["research", "analyze", "trend"]):
            return self._get("researcher")
        if "reply" in goal or "message" in goal:
            return self._get("assistant")
        return self._get("manager")

    def _get(self, role_contains: str) -> Agent:
        for a in self.agents:
            if role_contains in a.role.lower():
                return a
        return self.agents[0]

    def submit(self, goal: str, context: Dict[str, Any] | None = None) -> Task:
        task = Task(id=str(uuid.uuid4())[:8], goal=goal, context=context or {})
        agent = self.route(task)
        logging.info(f"routing task:{task.id} -> {agent.name} ({agent.role})")
        done = agent.run(task)
        self.history.append(done)
        return done

    def summary(self) -> str:
        return json.dumps(
            [{"id": t.id, "goal": t.goal, "status": t.status, "by": self.route(t).name} for t in self.history],
            indent=2
        )

# -----------------------------
# 7) demo
# -----------------------------
def bootstrap() -> Orchestrator:
    mem = Memory()
    tools = {"echo": EchoTool(), "counter": CounterTool()}
    agents = [
        ResearchAgent("Alice", "Researcher", mem, tools),
        TaskAgent("Bob", "Manager", mem, tools),
        Agent("Charlie", "Assistant", mem, tools),
    ]
    return Orchestrator(agents)

if __name__ == "__main__":
    orch = bootstrap()
    orch.submit("Research latest agent trends", {"query": "agent"})
    orch.submit("reply to user", {"text": "Hey! Your draft is ready."})
    orch.submit("setup && write docs && publish", {})
    print("\n== HISTORY ==")
    print(orch.summary())
