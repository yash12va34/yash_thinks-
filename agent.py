# agent_workflow.py — 100-line practice AI agent with API calls
import json,time,requests,re

# --- Tiny 'LLM' (rule-based) ---
def mini_llm(prompt):
    p=prompt.lower().strip()
    if 'weather' in p: return 'PLAN: get_weather(city=extract_city()); FORMAT: friendly'
    if 'wiki' in p or 'wikipedia' in p: return 'PLAN: wiki_summary(topic=extract_topic()); FORMAT: bullet'
    if 'todo' in p or 'task' in p: return 'PLAN: create_todo(text=extract_todo()); FORMAT: confirmation'
    return 'PLAN: chat(reply=short_help()); FORMAT: plain'

# --- Tools (external APIs) ---
def geocode_city(city):
    try:
        r=requests.get('https://nominatim.openstreetmap.org/search',
                     params={'q':city,'format':'json','limit':1},
                     headers={'User-Agent':'agent-practice/1.0'},timeout=10)
        j=r.json();
        if j: return {'lat':float(j[0]['lat']),'lon':float(j[0]['lon'])}
    except Exception: pass
    return None

def fetch_weather(city):
    pos=geocode_city(city)
    if not pos: return f"Sorry, couldn't find coordinates for '{city}'."
    r=requests.get('https://api.open-meteo.com/v1/forecast',
                  params={'latitude':pos['lat'],'longitude':pos['lon'],'current_weather':True},timeout=10)
    cw=r.json().get('current_weather',{})
    if not cw: return 'Weather data unavailable right now.'
    t,w,s=cw.get('temperature'),cw.get('weathercode'),cw.get('windspeed')
    return f"Weather in {city.title()}: {t}°C, wind {s} km/h, code {w}."

def wiki_summary(topic):
    slug=topic.strip().replace(' ','_'); url=f'https://en.wikipedia.org/api/rest_v1/page/summary/{slug}'
    r=requests.get(url,headers={'User-Agent':'agent-practice/1.0'},timeout=10); j=r.json()
    return j.get('extract','No summary found on Wikipedia.')

def create_todo(text):
    r=requests.post('https://jsonplaceholder.typicode.com/todos',
                   json={'title':text,'completed':False,'userId':1},timeout=10); j=r.json()
    return f"Created TODO (fake): id={j.get('id')} title='{j.get('title')}'."

# --- Agent + Router ---
class Toolbelt:
    def run(self,action,args):
        if action=='get_weather': return fetch_weather(args.get('city',''))
        if action=='wiki_summary': return wiki_summary(args.get('topic',''))
        if action=='create_todo': return create_todo(args.get('text',''))
        if action=='chat': return args.get('reply','I can fetch weather, wiki, or create todos.')
        return 'Unknown action.'

class Memory:
    def __init__(self): self.events=[]
    def add(self,role,content): self.events.append({'role':role,'content':content,'ts':time.time()})
    def recall(self,n=6): return self.events[-n:]

class Agent:
    def __init__(self,name,tools,memory): self.name,self.tools,self.memory=name,tools,memory

    def plan(self,user):
        raw=mini_llm(user)
        m=re.search(r'PLAN:\s*(\w+)\((.*?)\).*FORMAT:\s*(\w+)',raw)
        plan={'action':'chat','args':{'reply':'Try: weather in Paris, wiki Python, or todo Buy milk.'},'format':'plain'}
        if m:
            action,argstr,fmt=m.group(1),m.group(2),m.group(3); args={}
            if 'extract_city' in argstr:
                m2=re.search(r'weather in ([\w\s,.-]+)',user.lower()); args['city']=(m2.group(1) if m2 else user).strip(' .')
            if 'extract_topic' in argstr:
                m3=re.search(r'(?:wiki|wikipedia)\s+(.+)',user.lower()); args['topic']=(m3.group(1) if m3 else user).strip(' .')
            if 'extract_todo' in argstr:
                m4=re.search(r'(?:todo|task)\s*[:=-]?\s*(.+)',user,re.I); args['text']=(m4.group(1) if m4 else user).strip()
            plan={'action':action,'args':args,'format':fmt}
        return plan

    def run(self,user):
        self.memory.add('user',user); plan=self.plan(user); self.memory.add('plan',json.dumps(plan))
        result=self.tools.run(plan['action'],plan['args'])
        styled=self.stylize(result,plan['format']); self.memory.add('result',styled); return styled

    def stylize(self,text,mode):
        if mode=='bullet': return '\n'.join(f'- {line}' for line in text.split('. ') if line.strip())
        if mode=='friendly': return f"Here you go!\n{text}"
        if mode=='confirmation': return f"Done. {text}"
        return text

# --- Orchestrator / CLI ---
def main():
    tb,mem=Toolbelt(),Memory(); agent=Agent('EvoHelper',tb,mem)
    print("Type: 'weather in <city>', 'wiki <topic>', or 'todo <text>'. 'history' shows memory, 'quit' exits.")
    while True:
        try:
            u=input('You> ').strip()
            if u.lower() in {'quit','exit'}: break
            if u.lower()=='history':
                for e in mem.recall(): print(f"[{e['role']}] {e['content']}"); continue
            print('Agent>',agent.run(u))
        except KeyboardInterrupt:
            print('\nGoodbye!'); break

if __name__=='__main__': main()
