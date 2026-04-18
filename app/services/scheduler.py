from app.services.slot_engine import check_clash
import json

class Scheduler:
    def __init__(self, courses_data):
        """
        courses_data: [
            {
                'id': 1,
                'name': 'Math',
                'type': 'embedded',
                'options': [
                    {'prof_id': 10, 'prof_name': 'Dr. X', 'theory_slot': 'A1', 'lab_slot': 'L1', 'priority': 1},
                    ...
                ]
            },
            ...
        ]
        """
        self.courses = courses_data
        self.all_timetables = []
        self.max_limit = 1000

    def generate(self):
        self.all_timetables = []
        self._backtrack(0, [])
        return self.all_timetables

    def _backtrack(self, course_idx, current_schedule):
        if len(self.all_timetables) >= self.max_limit:
            return

        if course_idx == len(self.courses):
            self.all_timetables.append(list(current_schedule))
            return

        course = self.courses[course_idx]
        for option in course['options']:
            if not self._has_clash(option, current_schedule):
                current_schedule.append({
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'course_type': course['type'],
                    'prof_id': option['prof_id'],
                    'prof_name': option['prof_name'],
                    'theory_slot': option['theory_slot'],
                    'lab_slot': option['lab_slot'],
                    'priority': option['priority']
                })
                self._backtrack(course_idx + 1, current_schedule)
                current_schedule.pop()

    def _has_clash(self, new_option, current_schedule):
        new_slots = []
        if new_option.get('theory_slot'):
            new_slots.append(new_option['theory_slot'])
        if new_option.get('lab_slot'):
            new_slots.append(new_option['lab_slot'])

        for existing in current_schedule:
            existing_slots = []
            if existing.get('theory_slot'):
                existing_slots.append(existing['theory_slot'])
            if existing.get('lab_slot'):
                existing_slots.append(existing['lab_slot'])

            for ns in new_slots:
                for es in existing_slots:
                    if check_clash(ns, es):
                        return True
        return False
