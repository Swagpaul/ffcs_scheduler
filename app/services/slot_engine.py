import datetime

# Standard FFCS Slot Mappings (Example for VIT-like system)
# A1 -> Mon 8:00-8:50, Tue 9:00-9:50, Thu 10:00-10:50 etc.
# For simplicity, I will define a more manageable set or a flexible config.

SLOT_DATA = {
    "A1": [("Monday", "08:00", "08:50"), ("Tuesday", "09:00", "09:50"), ("Thursday", "10:00", "10:50")],
    "B1": [("Monday", "09:00", "09:50"), ("Wednesday", "08:00", "08:50"), ("Friday", "10:00", "10:50")],
    "C1": [("Monday", "10:00", "10:50"), ("Wednesday", "09:00", "09:50"), ("Friday", "08:00", "08:50")],
    "D1": [("Tuesday", "08:00", "08:50"), ("Wednesday", "10:00", "10:50"), ("Thursday", "09:00", "09:50")],
    "E1": [("Tuesday", "10:00", "10:50"), ("Thursday", "08:00", "08:50"), ("Friday", "09:00", "09:50")],
    
    "A2": [("Monday", "14:00", "14:50"), ("Tuesday", "15:00", "15:50"), ("Thursday", "16:00", "16:50")],
    "B2": [("Monday", "15:00", "15:50"), ("Wednesday", "14:00", "14:50"), ("Friday", "16:00", "16:50")],
    "C2": [("Monday", "16:00", "16:50"), ("Wednesday", "15:00", "15:50"), ("Friday", "14:00", "14:50")],
    "D2": [("Tuesday", "14:00", "14:50"), ("Wednesday", "16:00", "16:50"), ("Thursday", "15:00", "15:50")],
    "E2": [("Tuesday", "16:00", "16:50"), ("Thursday", "14:00", "14:50"), ("Friday", "15:00", "15:50")],

    # Lab Slots
    "L1": [("Monday", "08:00", "09:40")],
    "L2": [("Monday", "10:00", "11:40")],
    "L31": [("Tuesday", "08:00", "09:40")],
    "L32": [("Tuesday", "10:00", "11:40")],
    "L45": [("Wednesday", "08:00", "09:40")],
    "L46": [("Wednesday", "10:00", "11:40")],
}

def get_time_obj(t_str):
    return datetime.datetime.strptime(t_str, "%H:%M").time()

def check_clash(slot1_code, slot2_code):
    if not slot1_code or not slot2_code:
        return False
    
    times1 = SLOT_DATA.get(slot1_code, [])
    times2 = SLOT_DATA.get(slot2_code, [])
    
    for day1, start1, end1 in times1:
        for day2, start2, end2 in times2:
            if day1 == day2:
                s1 = get_time_obj(start1)
                e1 = get_time_obj(end1)
                s2 = get_time_obj(start2)
                e2 = get_time_obj(end2)
                
                # Check overlap: (StartA < EndB) and (EndA > StartB)
                if s1 < e2 and e1 > s2:
                    return True
    return False

def get_slot_info(slot_code):
    return SLOT_DATA.get(slot_code, [])

def get_all_slots():
    return list(SLOT_DATA.keys())
