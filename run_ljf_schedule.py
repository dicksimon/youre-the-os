
from lib import scheduler_extended 
from lib import constants


class RunSjfSchedule(scheduler_extended.SchedulderExtended):

    cpu_owner = []
    waiting_processes = []
    satisfied_processes = []
    temporary_processes = []

    def on_PROC_STARV(self, pid, starvation_level):
        if pid in self.cpu_owner and not self.processes[pid].has_ended:
            if pid not in self.satisfied_processes:
                self.satisfied_processes.append(pid)
            if pid in self.waiting_processes:
                self.waiting_processes.remove(pid)
            if pid in self.temporary_processes:
                self.temporary_processes.remove(pid)


    def on_PROC_NEW(self, pid):
        self.waiting_processes.append(pid)

    def on_PROC_KILL(self, pid):
        if pid in self.waiting_processes:
            self.waiting_processes.remove(pid)
        if pid in self.satisfied_processes:
            self.satisfied_processes.remove(pid)
        if pid in self.temporary_processes:
            self.temporary_processes.remove(pid)

    def on_PROC_END(self, pid):
        pass


    def on_PROC_TERM(self, pid):
        if pid in self.waiting_processes:
            self.waiting_processes.remove(pid)
        if pid in self.satisfied_processes:
            self.satisfied_processes.remove(pid)
        if pid in self.temporary_processes:
            self.temporary_processes.remove(pid)



    def schedule(self):


        if len(self.waiting_processes) < self.cpu_count:
            num_cpu_free = self.cpu_count - len(self.waiting_processes)
            self.waiting_processes = self.waiting_processes + self.satisfied_processes[:num_cpu_free]
            del self.satisfied_processes[:num_cpu_free]
    
        #Create list with all processes in descending job duration
        job_time_list = list() 
        for time, process_list in self.job_times.items():
            job_time_list = process_list +job_time_list  

        #remove processes that already have satisfied
        job_time_list_copy = job_time_list.copy()
        for process in job_time_list_copy:
            if process not in self.waiting_processes:
                job_time_list.remove(process)


        ##remove processes that are waiting for io-events
        sched_cpu = self.remove_io_blocked_processes(job_time_list)

        #clean io_queue
        self.clean_io_queue()

        ##trim sched_order to available cpu slots
        sched_cpu = self.trim_process_list(sched_cpu)

        #check if all slots are used
        if len(sched_cpu) < self.cpu_count:
            num_cpu_free = self.cpu_count - len(sched_cpu)

            ##find currently non blocked processes 
            self.temporary_processes = self.remove_io_blocked_processes(self.satisfied_processes)
            self.temporary_processes = self.temporary_processes[:num_cpu_free]
            for process in self.temporary_processes:
                #toDo update temporary_processes
                if process in sched_cpu:
                    print("error")
                sched_cpu.append(process)    
            
        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(sched_cpu))
            
        #update cpu schedule
        self.update_cpu_schedule(sched_cpu)
        self.cpu_owner = sched_cpu

run_os = RunSjfSchedule()
