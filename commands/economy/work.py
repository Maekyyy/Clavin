import random
from database import update_balance, check_cooldown, get_inventory

WORK_DATA = {
    "name": "work",
    "description": "Work to earn money (1 hour cooldown)",
    "type": 1
}

JOBS = [("washed cars", 100), ("walked a dog", 50), ("fixed a PC", 200), ("sold lemonade", 30), ("wrote code", 500)]

def cmd_work(data):
    user_id = data["member"]["user"]["id"]
    
    can_work, time_left = check_cooldown(user_id, "work", 3600)
    if not can_work:
        minutes = int(time_left // 60)
        return {"type": 4, "data": {"content": f"⏳ Rest for **{minutes} minutes**."}}

    job_name, salary = random.choice(JOBS)
    final_salary = int(salary * random.uniform(1.0, 1.2))
    
    # --- BONUS ZA WITAMINY ---
    inventory = get_inventory(user_id)
    bonus_msg = ""
    
    if "vitamins" in inventory:
        final_salary = int(final_salary * 1.5) # +50%
        bonus_msg = "\n💊 **Vitamins Boost:** +50% cash!"

    update_balance(user_id, final_salary)
    
    return {"type": 4, "data": {"content": f"💼 You **{job_name}** and earned **${final_salary}**!{bonus_msg}"}}