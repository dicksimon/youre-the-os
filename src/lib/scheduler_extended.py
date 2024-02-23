from lib import scheduler_base 


class SchedulderExtended(scheduler_base.SchedulerBase):
    
    def trim_process_list(self, processes):
        return processes[:self.cpu_count] 

    def calculate_ram_from_cpu_schedule(self, cpu_schedule):
        pages_order = list()
        for entry in cpu_schedule:
            process = self.processes.get(entry)
            for page in process.pages:
                if (page.key in self.pages_used):
                    pages_order.append(page.key)

        pages_order = pages_order[:self.ram_limit]
        new_pages_in_ram = set()
        new_pages_in_ram.update(pages_order)
        return new_pages_in_ram

    def update_cpu_schedule(self, new_cpu_schedule_list):

        new_cpu_schedule = set()
        new_cpu_schedule.update(new_cpu_schedule_list)

        processes_to_release = self.cpus_active.difference(new_cpu_schedule)
        processes_to_add = new_cpu_schedule.difference(self.cpus_active) 
        processes_to_add_list = list(processes_to_add)

        #create empty slot in cpu_inactive area if all slots are blocked, in this case there should be an available cpu-slot
        if len(self.cpus_inactive) == self.cpus_inactive_limit:
            if processes_to_add_list:
                if len(self.cpus_active) == self.cpus_active_limit:
                    print("error")
                else:
                    self.move_process_to_cpu(processes_to_add_list.pop(0))

        for process in processes_to_release:
            if processes_to_add_list:
                self.exchange_processes(process,processes_to_add_list.pop(0))
            else: 
                self.release_process_from_cpu(process)

        remaining_processes = processes_to_add_list.copy()
        for process in remaining_processes:
            self.move_process_to_cpu(processes_to_add_list.pop(0))

    def update_ram_schedule(self, new_pages_in_ram):
        pages_to_swap = self.pages_ram.difference(new_pages_in_ram)
        pages_to_ram = new_pages_in_ram.difference(self.pages_ram)
        pages_to_ram_list = list(pages_to_ram)
        if len(self.pages_swap) == self.swap_limit:
            if pages_to_ram_list :
                if len(self.pages_ram) == self.ram_limit:
                    print("error")
                else:
                    self.move_page_to_ram(pages_to_ram_list.pop(0))
        #toDo handle pages_to_swap >> pages_to_ram
        for page in pages_to_swap:
            if pages_to_ram_list :
                self.exchange_pages(page,pages_to_ram_list.pop(0))
            else: 
                self.move_page_to_swap(page)
        remaining_pages = pages_to_ram_list.copy()
        for page in remaining_pages:
            self.move_page_to_ram(pages_to_ram_list.pop(0)) 

    def remove_io_blocked_processes(self, processes):
        ##remove processes that are waiting for io-events
        sched_order_new = processes.copy()    
        for process in processes:
            if self.is_process_waiting_for_io(process):
                sched_order_new.remove(process)
        return sched_order_new

    def cleanup_processes(self):
        terminated_copy = self.terminated_processes.copy()
        for process in terminated_copy:
            self.release_process_from_cpu(process)    
            self.terminated_processes.remove(process)
       
    def is_process_executable(self, pid):
        return not (self.processes[pid].waiting_for_io or self.processes[pid].waiting_for_page)
     
    def is_process_waiting_for_io(self, pid):
        return self.processes[pid].waiting_for_io
    
    def is_process_waiting_for_page(self, pid):
        return self.processes[pid].waiting_for_page
    
    def clean_io_queue(self):
        x = range(self.io_queue.io_count)
        for n in  x:
            self.do_io()