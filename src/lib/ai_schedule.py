from lib import scheduler_base 


class AiSchedule(scheduler_base.SchedulerBase):

    def handle_events(self, events: list):
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        


    def schedule(self):
        cpu_owner = []
        for key in self.processes:
            cpu_owner.append(key)
        cpu_owner = self.trim_process_list(cpu_owner)
        #clean io_queue
        self.clean_io_queue()
        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(cpu_owner))
        #update cpu schedule
        self.update_cpu_schedule(cpu_owner)
        return self._event_queue

    def clear_sched_events(self):
        self._event_queue.clear()
