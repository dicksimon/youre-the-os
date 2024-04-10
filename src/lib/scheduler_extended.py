from lib import scheduler_base 


class SchedulderExtended(scheduler_base.SchedulerBase):
    
    # entrypoint
    def __call__(self, events: list):
        """Entrypoint from game

        will dispatch each event to the respective handler,
        collecting action events to send back to the game,
        if a handler doesn't exist, will ignore that event.
        """
        self._event_queue.clear()
        # update the status of process/memory
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        # run the scheduler
        self.schedule()
        return self._event_queue


    def schedule(self):
        pass