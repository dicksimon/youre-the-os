from lib import scheduler_base 


class AiSchedule(scheduler_base.SchedulerBase):

    proc_term_count = 0
    proc_end_count = 0
    proc_kill_count = 0
    

    def handle_events(self, events: list):
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        
    def on_PROC_TERM(self, pid):
        self.proc_term_count

    def on_PROC_END(self, pid):
        self.proc_end_count += 1

    def on_PROC_KILL(self, pid):
        self.proc_kill_count += 1

    def get_average_starvation_level(self):
        culminated_starvation_level = 0
        processes = 0
        for starvation_level in self.starvation.keys():
            for process in self.starvation[starvation_level]:
                culminated_starvation_level += starvation_level
                processes += 1
        if processes > 0:
            average =  (culminated_starvation_level/processes)
        else: 
            average = 0
        return average

    def calc_reward(self):
        reward_proc_events = 10 * self.proc_term_count + 20 * self.proc_end_count - 200 * (self.proc_kill_count)

        reward_starvation_level = (-10) * self.get_average_starvation_level()

        self.proc_term_count = 0
        self.proc_end_count = 0
        self.proc_kill_count = 0

        reward = reward_proc_events + reward_starvation_level + self.schedule_reward
        self.schedule_reward = 0
        return reward

    def derive_cpu_owner_from_action(self, action):
        calc_reward = False
        cpu_owner = action.tolist()
        if len(self.processes) > len(cpu_owner):
            calc_reward = True
        cpu_owner[:] = [process for process in cpu_owner if process in self.processes]
        
        if calc_reward:
            self.schedule_reward = (len(cpu_owner) - 16) * 10 
        return cpu_owner

    def schedule(self, action):

        self.clean_io_queue()

        #get new cpu owners
        cpu_owner = self.derive_cpu_owner_from_action(action)
        
        #update ram schedule
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(cpu_owner))
        
        #update cpu schedule
        self.update_cpu_schedule(cpu_owner)
        return self._event_queue

    def clear_sched_events(self):
        self._event_queue.clear()

    def calculate_ram_from_cpu_schedule(self, cpu_schedule):
        schedule_reward = 0
        pages_order = list()
        for entry in cpu_schedule:
            process = self.processes.get(entry)
            for page in process.pages:
                if (page.key in self.pages_used):
                    pages_order.append(page.key)

        pages_order = pages_order[:self.ram_limit]
        self.schedule_reward = schedule_reward
        return pages_order