
from lib import scheduler_extended 
from lib import constants


class RunFifoSchedule(scheduler_extended.SchedulderExtended):

    process_list = []
    fifo_active_processes = []
    satisfied_processes = []

    def on_PROC_STARV(self, pid, starvation_level):
        if pid in self.fifo_active_processes and not self.processes[pid].has_ended:
            #maybe unused
            if starvation_level != constants.DEAD_STARVATION_LEVEL:
                self.satisfied_processes.append(pid)

    def on_PROC_NEW(self, pid):
        self.process_list.append(pid)

    def on_PROC_KILL(self, pid):
        self.process_list.remove(pid)

    def on_PROC_END(self, pid):
        #self.process_list.remove(pid)
        pass

    def on_PROC_TERM(self, pid):
        self.process_list.remove(pid)
        if pid in self.satisfied_processes:
            self.satisfied_processes.remove(pid)




    def schedule(self):
    

        #clean io_queue
        self.clean_io_queue()

        #reorder fifo
        for process in self.satisfied_processes:
            self.process_list.remove(process)
            self.process_list.append(process)

        ##remove processes that are waiting for io-events
        sched_cpu = self.remove_io_blocked_processes(self.process_list)


        ##trim sched_order to available cpu slots
        self.fifo_active_processes = self.trim_process_list(sched_cpu)
        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(self.fifo_active_processes))
        #update cpu schedule
        self.update_cpu_schedule(self.fifo_active_processes)
 
        self.satisfied_processes.clear()

#
# the main entrypoint to run the scheduler
#
# it expects a callable `run_os`
#
# it receives a list of events generated from processes/pages
# see `src/lib/event_manager` for generated events
#
# it should return a list of events to happen
#

run_os = RunFifoSchedule()
