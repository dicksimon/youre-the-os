from lib import scheduler_base 
from lib.constants import MAX_CPU_COUNT

class AiSchedule(scheduler_base.SchedulerBase):

    def __init__(self):
        self.latest_cpu_owner = []
        self.cpu_owner = []
        self.schedule_reward = 0
        self.proc_satisfied_count = 0
        self.proc_term_count = 0
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

        #reward_proc_events = 1 - 200 * (self.proc_kill_count)
        #reward = reward_proc_events + self.calc_schedule_reward()
#
        #punishment_not_removed = 0
        #for pid in self.cpu_owner:
        #    if self.processes[pid].has_ended:
        #        punishment_not_removed += 100
#
        #self.proc_term_count = 0
        #self.proc_end_count = 0
        #self.proc_kill_count = 0
        #self.proc_satisfied_count = 0

        #return reward - punishment_not_removed
    
        return self.schedule_reward


    def derive_cpu_owner_from_action(self, action):
        self.cpu_owner = action.tolist()

        self.calc_schedule_reward_v4(self.latest_cpu_owner, self.cpu_owner)
        self.cpu_owner[:] = [process for process in self.cpu_owner if process in self.processes]
        
        self.latest_cpu_owner = self.cpu_owner
        return self.cpu_owner



    def calc_schedule_reward_v2(self, latest_schedule, new_schedule):

        reward = 0
        procs_out = list(set(latest_schedule) - set(new_schedule))
        procs_in =  list(set(new_schedule) - set(latest_schedule))       
        
        #have removed processes terminated?
        for proc in procs_out:
            if proc in self.processes:
                if not self.processes[proc].starvation_level == 0:
                    reward -= 10
                else:
                    reward += 10
        
        #are processes with the highest starvation level selected?
            #Create list with all processes in descending starvation level
        starvation_list = list() 
        for starvation_level, process_list in self.starvation.items():
            for process in process_list:
                starvation_list.append(process[0])


        len_starvation = len(starvation_list)
             
        if len_starvation:    

            if len_starvation >= MAX_CPU_COUNT:
                proc_min_starv = starvation_list[MAX_CPU_COUNT-1]
            else:
                proc_min_starv = starvation_list[len(starvation_list)-1]
        
            min_starv_level = self.processes[proc_min_starv].starvation_level
            for proc in new_schedule:
                starvation_level = self.processes[proc].starvation_level
                if starvation_level < min_starv_level:
                    reward -= 10
                elif starvation_level > min_starv_level:
                    reward += 10

        self.schedule_reward = reward


    def calc_schedule_reward_v5(self, latest_schedule, new_schedule):

        reward = 0


        reward_proc_events = self.proc_satisfied_count * (100) + self.proc_end_count * (100) - self.proc_kill_count * (200)
 
        self.proc_end_count = 0
        self.proc_kill_count = 0
        self.proc_satisfied_count = 0


        procs_out = list(set(latest_schedule) - set(new_schedule))      
        #have removed processes terminated?
        for proc in procs_out:
            if proc in self.processes:
                if not self.processes[proc].starvation_level == 0:
                    reward -= 10
                else:
                    reward += 10
        
        starvation_list = list() 
        for starvation_level, process_list in self.starvation.items():
            for process in process_list:
                starvation_list.append(process[0])


        len_starvation = len(starvation_list)
             
        if len_starvation:    

            if len_starvation >= MAX_CPU_COUNT:
                proc_min_starv = starvation_list[MAX_CPU_COUNT-1]
            else:
                proc_min_starv = starvation_list[len(starvation_list)-1]
        
            min_starv_level = self.processes[proc_min_starv].starvation_level
            for proc in new_schedule:

                if proc in self.processes:
                    starvation_level = self.processes[proc].starvation_level
                    if starvation_level < min_starv_level:
                        reward -= 10
                    elif starvation_level >= min_starv_level:
                        reward += 10
                else:
                    reward -= 10

        self.schedule_reward = reward + reward_proc_events


    def calc_schedule_reward_v4(self, latest_schedule, new_schedule):

        reward = 0
        
        starvation_list = list() 
        for starvation_level, process_list in self.starvation.items():
            for process in process_list:
                starvation_list.append(process[0])


        len_starvation = len(starvation_list)
             
        if len_starvation:    

            if len_starvation >= MAX_CPU_COUNT:
                proc_min_starv = starvation_list[MAX_CPU_COUNT-1]
            else:
                proc_min_starv = starvation_list[len(starvation_list)-1]
        
            min_starv_level = self.processes[proc_min_starv].starvation_level
            for proc in new_schedule:

                if proc in self.processes:
                    starvation_level = self.processes[proc].starvation_level
                    if starvation_level < min_starv_level:
                        reward -= 10
                    elif starvation_level >= min_starv_level:
                        reward += 10
                else:
                    reward -= 10

        self.schedule_reward = reward



    def schedule(self, action):

        self.clean_io_queue()

        #get new cpu owners
        self.cpu_owner = self.derive_cpu_owner_from_action(action)
        
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