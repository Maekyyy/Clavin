import random
from database import update_balance, check_cooldown

WORK_DATA = {
    "name": "work",
    "description": "Work to earn money (1 hour cooldown)",
    "type": 1
}

JOBS = [
    ("washed cars", 100),
    ("walked a dog", 50),
    ("fixed a computer", 200),
    ("sold lemonade", 30),
    ("wrote code for Clavin", 500)
]

def cmd_work(data):
    user_id = data["member"]["user"]["id"]
    
    # Sprawdź czas (3600 sekund = 1 godzina)
    can_work, time_left = check_cooldown(user_id, "work", 3600)
    
    if not can_work:
        minutes = int(time_left // 60)
        return {"type": 4, "data": {"content": f"⏳ You are tired! Rest for **{minutes} minutes**."}}

    # Praca
    job_name, salary = random.choice(JOBS)
    # Dodaj losową premię (0-20%)
    final_salary = int(salary * random.uniform(1.0, 1.2))
    
    update_balance(user_id, final_salary)
    
    return {
        "type": 4,
        "data": {
            "content": f"💼 You **{job_name}** and earned **${final_salary}**!"
        }
    }