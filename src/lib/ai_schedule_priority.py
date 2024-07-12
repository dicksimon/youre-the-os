from lib import scheduler_base 
from lib.constants import MAX_CPU_COUNT

class AiSchedulePriority(scheduler_base.SchedulerBase):

    def __init__(self,strategy):
        self.latest_cpu_owner = []
        self.cpu_owner = []
        self.schedule_reward = 0
        self.proc_satisfied_count = 0
        self.proc_term_count = 0
        self.strategy = strategy
        self.proc_end_count = 0
        self.proc_kill_count = 0
        super().__init__()

    def handle_events(self, events: list):
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        


    def on_PROC_STARV(self, pid, starvation_level):
        if pid in self.cpu_owner and starvation_level == 0:
            self.proc_satisfied_count += 1
        if pid in self.cpu_owner and not self.processes[pid].has_ended:
            self.cpu_owner.remove(pid)

    def on_PROC_TERM(self, pid):
        self.proc_term_count
        if pid in self.cpu_owner:
            self.cpu_owner.remove(pid)

    def on_PROC_END(self, pid):
        self.proc_end_count += 1

    def on_PROC_KILL(self, pid):
        self.proc_kill_count += 1
        if pid in self.cpu_owner:
            self.cpu_owner.remove(pid)




    def get_reward(self):
        return self.schedule_reward 


    def calc_reward(self):
        reward =  self.proc_satisfied_count + self.proc_end_count*(100) - self.proc_kill_count * (1000) 
        self.proc_end_count = 0
        self.proc_kill_count = 0
        self.proc_satisfied_count = 0
        self.schedule_reward = reward 


    def derive_cpu_owner_from_action(self, action):
        command = action.tolist()

        self.cpu_owner = self.remove_io_blocked_processes(self.cpu_owner)

        if len (self.cpu_owner) < self.cpu_count:
            num_cpu_free = self.cpu_count - len(self.cpu_owner)
            starvation_list = list() 
            for starvation_level, process_list_immutable in self.starvation.items():
                process_list = process_list_immutable.copy()

                #priority advanced
                if command == 0:
                    pass
                #ljf
                elif command == 1:
                    process_list.sort(key=lambda x: x[1], reverse=True)
                #sjf
                elif command == 2:
                    process_list.sort(key=lambda x: x[1])
                
                
                for process in process_list:
                    starvation_list.append(process[0])

            starvation_list_copy = starvation_list.copy()
            for process in starvation_list_copy:
                if process in self.cpu_owner:
                    starvation_list.remove(process)
            ##remove processes that are waiting for io-events
            sched_cpu = self.remove_io_blocked_processes(starvation_list)
            sched_cpu = sched_cpu[:num_cpu_free]
            self.cpu_owner = self.cpu_owner + sched_cpu


        return self.cpu_owner


    def schedule(self, action):

        self.clean_io_queue()

        #get new cpu owners
        self.cpu_owner = self.derive_cpu_owner_from_action(action)
        self.calc_reward()
        
        #update ram schedule
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(self.cpu_owner))
        
        #update cpu schedule
        self.update_cpu_schedule(self.cpu_owner)
        return self._event_queue

    def clear_sched_events(self):
        self._event_queue.clear()

    def calculate_ram_from_cpu_schedule(self, cpu_schedule):
        pages_order = list()
        for entry in cpu_schedule:
            process = self.processes.get(entry)
            for page in process.pages:
                if (page.key in self.pages_used):
                    pages_order.append(page.key)

        pages_order = pages_order[:self.ram_limit]
        return pages_order