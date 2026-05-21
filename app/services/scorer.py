from app.services.slot_engine import get_slot_info
import datetime

def calculate_score(timetable):
    """
    score =
    +10 for top priority professor (priority 1)
    +5 for second priority (priority 2)
    -5 for gaps > 2 hours
    -10 for late evening overload (not implemented in sample slot data yet but concept is there)
    +5 for compact day
    """
    score = 0
    
    # Priority Score
    for entry in timetable:
        if entry['priority'] == 1:
            score += 10
        elif entry['priority'] == 2:
            score += 5
            
    # Gap Analysis & Compactness
    day_schedules = {} # day -> list of (start, end)
    
    for entry in timetable:
        slots = []
        if entry.get('theory_slot'): slots.append(entry['theory_slot'])
        if entry.get('lab_slot'): slots.append(entry['lab_slot'])
        
        for s_code in slots:
            info = get_slot_info(s_code)
            for day, start, end in info:
                if day not in day_schedules:
                    day_schedules[day] = []
                day_schedules[day].append((
                    datetime.datetime.strptime(start, "%H:%M"),
                    datetime.datetime.strptime(end, "%H:%M")
                ))
                
    for day, times in day_schedules.items():
        times.sort()
        # Compactness: if multiple classes in a day, check gaps
        if len(times) > 1:
            score += 5 # Reward for having a "day with classes" (compactness check is better below)
            for i in range(len(times) - 1):
                gap = (times[i+1][0] - times[i][1]).total_seconds() / 3600.0
                if gap > 2.0:
                    score -= 5
                elif gap <= 1.0:
                    score += 2 # Small gap is good for compactness
                    
    return score
