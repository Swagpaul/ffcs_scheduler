from app.services.slot_engine import check_clash


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
        self._seen_signatures = set()
        self._backtrack(0, [])
        return self.all_timetables

    def _backtrack(self, course_idx, current_schedule):
        if len(self.all_timetables) >= self.max_limit:
            return

        if course_idx == len(self.courses):
            if current_schedule:
                sig = self._signature(current_schedule)
                if sig not in self._seen_signatures:
                    self._seen_signatures.add(sig)
                    self.all_timetables.append(list(current_schedule))
            return

        course = self.courses[course_idx]
        placed = False

        # Try each slot option for this course
        for option in course['options']:
            if not self._has_clash(option, current_schedule):
                placed = True
                current_schedule.append({
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'course_type': course['type'],
                    'credits': course.get('credits', 3),
                    'prof_id': option['prof_id'],
                    'prof_name': option['prof_name'],
                    'theory_slot': option['theory_slot'],
                    'lab_slot': option['lab_slot'],
                    'priority': option['priority']
                })
                self._backtrack(course_idx + 1, current_schedule)
                current_schedule.pop()

        # If NONE of this course's options fit without clashing,
        # generate a branch where this course is simply omitted.
        # This creates separate timetables for each side of a clash.
        if not placed:
            self._backtrack(course_idx + 1, current_schedule)

    def _has_clash(self, new_option, current_schedule):
        """Strict clash check — any slot overlap (theory or lab) is a clash."""
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

    def _signature(self, schedule):
        """Unique fingerprint for a timetable to deduplicate results."""
        parts = sorted(
            f"{item['course_id']}:{item['prof_id']}:{item['theory_slot']}:{item['lab_slot']}"
            for item in schedule
        )
        return ",".join(parts)

    def get_clash_reasons(self):
        reasons = []
        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                c1 = self.courses[i]
                c2 = self.courses[j]

                all_clash = True
                for o1 in c1['options']:
                    for o2 in c2['options']:
                        temp_item = {
                            'theory_slot': o2.get('theory_slot'),
                            'lab_slot': o2.get('lab_slot')
                        }
                        if not self._has_clash(o1, [temp_item]):
                            all_clash = False
                            break
                    if not all_clash:
                        break

                if all_clash:
                    reasons.append(f"'{c1['name']}' clashes with '{c2['name']}'")

        if reasons:
            return "Unresolvable conflicts: " + ", ".join(reasons)
        return "Could not generate any error-free timetables due to scheduling constraints."
