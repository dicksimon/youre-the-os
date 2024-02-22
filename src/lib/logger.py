
from enum import Enum
from collections import defaultdict

log_page = Enum('log_pages',['CREATED_SWAP','CREATED_RAM','MOVED_SWAP', 'MOVED_RAM', 'PAGE_USED', 'PAGE_UNUSED','FREED'])


class Logger:
    
    processes: dict[int,list] = {}
    pages =  defaultdict(dict[int,list])
    orders = []


    def create_page(self, key, ram):
       if ram:
           self.pages[key[0]][key[1]] = [log_page.CREATED_RAM]
       else:
           self.pages[key[0]][key[1]] = [log_page.CREATED_SWAP]

    def move_page(self, key, ram):
        if ram:
            self.pages[key[0]][key[1]].append(log_page.MOVED_RAM)
        else:
            if self.pages[key[0]][key[1]][-1] == log_page.PAGE_USED:
                pass
            self.pages[key[0]][key[1]].append(log_page.MOVED_SWAP)
        

    def free_page(self,key):
        self.pages[key[0]][key[1]].append(log_page.FREED)

    def page_use(self,key, use):
        if use:
            if len(self.pages[key[0]][key[1]]) > 3:
                testlist = self.pages[key[0]][key[1]][-6:]
                if  testlist == [log_page.MOVED_SWAP, log_page.PAGE_UNUSED, log_page.PAGE_USED, log_page.MOVED_RAM, log_page.MOVED_SWAP, log_page.PAGE_UNUSED]:
                    pass
            self.pages[key[0]][key[1]].append(log_page.PAGE_USED)
            
        else:
            self.pages[key[0]][key[1]].append(log_page.PAGE_UNUSED)