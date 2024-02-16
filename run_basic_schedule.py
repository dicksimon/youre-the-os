
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):



    def update_ram_schedule(self, new_ram_schedule):

        pages_to_swap = self.pages_ram.difference(new_ram_schedule)
        pages_to_ram = new_ram_schedule.difference(self.pages_ram)

        pages_to_ram_list = list(pages_to_ram)
        if len(pages_to_swap) <= len(pages_to_ram):
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

    
    def schedule(self):
    
        self.clean_io_queue()
        #Create list with all processes in descending starvation level
        sched_order = list() 
        for starvation_level, process_list in self.starvation.items():
            sched_order = sched_order + process_list


        sched_order_new = sched_order.copy() 
        
        ##remove processes that are waiting for io-events   
        for process in sched_order:
            if self.is_process_waiting_for_io(process):
                sched_order_new.remove(process)
                    
        ##trim sched_order to available cpu slots
        sched_order_new = sched_order_new[:self.cpu_count] 
        new_cpus_active = set()
        new_cpus_active.update(sched_order_new)
        self.update_cpu_schedule(new_cpus_active)
            
        
        pages_order = list()
        for entry in self.cpus_active:
            process = self.processes.get(entry)
            for page in process.pages:
                if (page.key in self.pages_used):
                    pages_order.append(page.key)

        pages_order = pages_order[:self.ram_limit]
        new_pages_in_ram = set()
        new_pages_in_ram.update(pages_order)
        self.update_ram_schedule(new_pages_in_ram);
        


run_os = RunBasicSchedule()
