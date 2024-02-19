from lib import scheduler_base 


class SchedulderExtended(scheduler_base.SchedulerBase):
    
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

    def update_ram_schedule(self, new_ram_schedule):

        pages_to_swap = self.pages_ram.difference(new_ram_schedule)
        pages_to_ram = new_ram_schedule.difference(self.pages_ram)

        pages_to_ram_list = list(pages_to_ram)
        if len(pages_to_swap) <= len(pages_to_ram):

            #create empty slot in swap if all slots are blocked, in this case there should be an available slot in the ram
            if len(self.pages_swap) == self.swap_limit:
                if pages_to_ram_list:
                    self.move_page_to_ram(pages_to_ram_list.pop(0))

            for page in pages_to_swap:
                self.exchange_pages(page,pages_to_ram_list.pop(0))
            if pages_to_ram_list:
                for page in pages_to_ram_list:
                    self.move_page_to_ram(page)
        else:
            for page in pages_to_swap:
                if pages_to_ram_list:
                    self.exchange_pages(page,pages_to_ram_list.pop(0))
                else:
                    self.move_page_to_swap(page)

    def update_cpu_schedule(self, new_cpu_schedule):

        processes_to_release = self.cpus_active.difference(new_cpu_schedule)
        processes_to_add = new_cpu_schedule.difference(self.cpus_active) 

        processes_to_add_list = list(processes_to_add)
        if len(processes_to_release) <= len(processes_to_add):


            #create empty slot in cpu_inactive area if all slots are blocked, in this case there should be an available cpu-slot
            if len(self.cpus_inactive) == self.cpus_inactive_limit:
                if processes_to_add_list:
                    self.move_process_to_cpu(processes_to_add_list.pop(0))

            for process in processes_to_release:
                self.exchange_processes(process,processes_to_add_list.pop(0))
            if processes_to_add_list:
                for process in processes_to_add_list:
                    self.move_process_to_cpu(process)
        else:
            for process in processes_to_release:
                if processes_to_add_list:
                    self.exchange_processes(process,processes_to_add_list.pop(0))
                else:
                    self.release_process_from_cpu(process)

    def cleanup_processes(self):
        for process in self.terminated_processes:
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