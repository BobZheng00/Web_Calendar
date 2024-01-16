import datetime

from dateutil.rrule import DAILY, WEEKLY, MONTHLY, rrule

from .models import UserEvents


class InputEvents:
    repeat_rules = {
        'daily': DAILY,
        'weekly': WEEKLY,
        'monthly': MONTHLY
    }

    def __init__(self, user_id: int = None, event: str = None, date: datetime.date = None, begin_hr: int = None,
                 begin_min: int = None, end_hr: int = None, end_min: int = None, description: str = "",
                 is_private: bool = False, hex_color: str = "#000000", repeated_rule: str = "once",
                 repeated_end: datetime.date = None):
        self.user_id = user_id
        self.event = event
        self.date = date
        self.description = description
        self.is_private = is_private
        self.hex_color = hex_color
        self.repeated_rule = repeated_rule
        self.repeated_end = repeated_end

        if any(key is None for key in [begin_hr, begin_min, end_hr, end_min]):
            self.beginning = None
            self.end = None
        else:
            self.beginning = begin_hr * 100 + begin_min
            self.end = end_hr * 100 + end_min

        self.valid, self.error_message = self.is_valid()

    def is_valid(self) -> [bool, str]:
        if any(key is None for key in [self.user_id, self.event, self.date, self.beginning, self.end]):
            return False, "Missing required fields"

        if self.beginning >= self.end:
            return False, "Event end time is before or equal to event start time"

        if self.repeated_rule != "once" and self.repeated_end is None:
            return False, "Missing repeated end date"

        if self.repeated_rule != "once" and self.repeated_end < self.date:
            return False, "Repeated end date is before the event date"

        return True, ""

    def __str__(self):
        return f"InputEvents(user_id={self.user_id}, event={self.event}, date={self.date}, " \
               f"beginning={self.beginning}, end={self.end}, description={self.description}, " \
               f"is_private={self.is_private}, hex_color={self.hex_color}, repeated_rule={self.repeated_rule}, " \
               f"repeated_end={self.repeated_end})"

    def is_exist(self) -> bool:
        return UserEvents.objects.filter(user_id=self.user_id, event=self.event, date=self.date,
                                         beginning=self.beginning, end=self.end).exists()

    def create_event(self) -> [bool, str]:
        if not self.valid:
            return self.valid, self.error_message

        # Create a single event
        if self.repeated_rule == "once":
            UserEvents.objects.create(user_id=self.user_id, event=self.event, date=self.date, beginning=self.beginning,
                                      end=self.end, description=self.description, is_private=self.is_private,
                                      hex_color=self.hex_color)
            return True, "Event is successfully created"

        # Create repeated events
        if self.repeated_rule in InputEvents.repeat_rules:
            for date in rrule(InputEvents.repeat_rules[self.repeated_rule], dtstart=self.date, until=self.repeated_end):
                UserEvents.objects.create(user_id=self.user_id, event=self.event, date=date, beginning=self.beginning,
                                          end=self.end, description=self.description, is_private=self.is_private,
                                          hex_color=self.hex_color)
            return True, "Events are successfully created"
        else:
            return False, "Invalid event creation"

    def delete_event(self) ->[bool, str]:
        if not self.valid:
            return self.valid, self.error_message

        if not self.is_exist():
            return False, "Event does not exist"

        # Delete a single event
        UserEvents.objects.filter(user_id=self.user_id, event=self.event, date=self.date,
                                  beginning=self.beginning, end=self.end).delete()
        return True, "Event is successfully deleted"

