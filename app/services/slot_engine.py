import datetime
import re

# Standard FFCS Slot Mappings (Example for VIT-like system)
# Synchronized with results.html GRID_MAPPING
SLOT_DATA = {}

GRID_MAPPING = {
    'Monday': {
        'THEORY': ['A1', 'F1', 'D1', 'TB1', 'TG1', '-', '-', 'A2', 'F2', 'D2', 'TB2', 'TG2', '-', 'V3'],
        'LAB': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', '-', 'L31', 'L32', 'L33', 'L34', 'L35', 'L36', '-']
    },
    'Tuesday': {
        'THEORY': ['B1', 'G1', 'E1', 'TC1', 'TAA1', '-', '-', 'B2', 'G2', 'E2', 'TC2', 'TAA2', '-', 'V4'],
        'LAB': ['L7', 'L8', 'L9', 'L10', 'L11', 'L12', '-', 'L37', 'L38', 'L39', 'L40', 'L41', 'L42', '-']
    },
    'Wednesday': {
        'THEORY': ['C1', 'A1', 'F1', 'V1', 'V2', '-', '-', 'C2', 'A2', 'F2', 'TD2', 'TBB2', '-', 'V5'],
        'LAB': ['L13', 'L14', 'L15', 'L16', 'L17', 'L18', '-', 'L43', 'L44', 'L45', 'L46', 'L47', 'L48', '-']
    },
    'Thursday': {
        'THEORY': ['D1', 'B1', 'G1', 'TE1', 'TCC1', '-', '-', 'D2', 'B2', 'G2', 'TE2', 'TCC2', '-', 'V6'],
        'LAB': ['L19', 'L20', 'L21', 'L22', 'L23', 'L24', '-', 'L49', 'L50', 'L51', 'L52', 'L53', 'L54', '-']
    },
    'Friday': {
        'THEORY': ['E1', 'C1', 'TA1', 'TF1', 'TD1', '-', '-', 'E2', 'C2', 'TA2', 'TF2', 'TDD2', '-', 'V7'],
        'LAB': ['L25', 'L26', 'L27', 'L28', 'L29', 'L30', '-', 'L55', 'L56', 'L57', 'L58', 'L59', 'L60', '-']
    },
    'Saturday': {
        'THEORY': ['V8', 'X11', 'X12', 'Y11', 'Y12', '-', '-', 'X21', 'Z21', 'Y21', 'W21', 'W22', '-', 'V9'],
        'LAB': ['L71', 'L72', 'L73', 'L74', 'L75', 'L76', '-', 'L77', 'L78', 'L79', 'L80', 'L81', 'L82', '-']
    },
    'Sunday': {
        'THEORY': ['V10', 'Y11', 'Y12', 'X11', 'X12', '-', '-', 'Y21', 'Z21', 'X21', 'W21', 'W22', '-', 'V11'],
        'LAB': ['L83', 'L84', 'L85', 'L86', 'L87', 'L88', '-', 'L89', 'L90', 'L91', 'L92', 'L93', 'L94', '-']
    }
}

THEORY_START_TIMES = ['08:00', '09:00', '10:00', '11:00', '12:00', '-', '-', '14:00', '15:00', '16:00', '17:00', '18:00', '18:51', '19:01']
THEORY_END_TIMES = ['08:50', '09:50', '10:50', '11:50', '12:50', '-', '-', '14:50', '15:50', '16:50', '17:50', '18:50', '19:00', '19:50']
LAB_START_TIMES = ['08:00', '08:51', '09:51', '10:41', '11:40', '12:31', '-', '14:00', '14:51', '15:51', '16:41', '17:40', '18:31', '-']
LAB_END_TIMES = ['08:50', '09:40', '10:40', '11:30', '12:30', '13:20', '-', '14:50', '15:40', '16:40', '17:30', '18:30', '19:20', '-']

for day, types in GRID_MAPPING.items():
    # Populate Theory Slots
    for idx, slot in enumerate(types['THEORY']):
        if slot != '-':
            if slot not in SLOT_DATA:
                SLOT_DATA[slot] = []
            SLOT_DATA[slot].append((day, THEORY_START_TIMES[idx], THEORY_END_TIMES[idx]))
    
    # Populate Lab Slots
    for idx, slot in enumerate(types['LAB']):
        if slot != '-':
            if slot not in SLOT_DATA:
                SLOT_DATA[slot] = []
            SLOT_DATA[slot].append((day, LAB_START_TIMES[idx], LAB_END_TIMES[idx]))

def get_time_obj(t_str):
    return datetime.datetime.strptime(t_str, "%H:%M").time()

def split_slots(slot_code):
    if not slot_code:
        return []
    # Split by + or , and strip whitespace
    return [s.strip().upper() for s in re.split(r'[+,]', slot_code) if s.strip()]

def check_clash(slot1_str, slot2_str):
    if not slot1_str or not slot2_str:
        return False
    
    codes1 = split_slots(slot1_str)
    codes2 = split_slots(slot2_str)
    
    for c1 in codes1:
        for c2 in codes2:
            times1 = SLOT_DATA.get(c1, [])
            times2 = SLOT_DATA.get(c2, [])
            
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
    # Support combined slots by merging their times
    codes = split_slots(slot_code)
    all_times = []
    for c in codes:
        all_times.extend(SLOT_DATA.get(c, []))
    return all_times

def get_all_slots():
    return list(SLOT_DATA.keys())

def is_valid_slot(slot_str):
    if not slot_str: return True
    codes = split_slots(slot_str)
    valid_keys = get_all_slots()
    return all(c in valid_keys for c in codes)
