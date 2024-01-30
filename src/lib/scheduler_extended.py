from lib import scheduler_base 


class SchedulderExtended(scheduler_base.SchedulerBase):
    
    
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