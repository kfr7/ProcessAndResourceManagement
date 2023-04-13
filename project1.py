# project1.py

# Process and Resource Management

# data structures
from collections import deque, defaultdict
# deque left side = head/front of list and right side = tail/end of list

# for some function type annotations
from typing import Tuple    

PCB = [0] * 16  # max 16 processes
RCB = [0] * 4   # 4 resources
RL = [0] * 3    # 3 level ready list
new_set_of_commands_flag = True     # helps print correct spacing

class ProcessControlBlock:
    """
    A class to represent a Process Control Block (PCB).

    Attributes
    ----------
    priority : int
        which priority queue this PCB will reside in externally
    state : int
        whether it is blocked or ready
    parent : int
        parent process of this PCB
    children : set
        all children this PCB is parent of
    resources : dictionary
        <resource type>: amount of units being used/held
    """
    def __init__(self, priority: int = -1, state: int = -1, parent: int = -1):
        # if priority is invalid, the index in the PCB list would be considered free
        self.priority = priority    # -1 = invalid, valid levels = {0, 1, 2}
        self.state = state  # -1 = invalid, 0 = "blocked", 1 = "ready"
        self.parent = parent # process id of parent
        self.children = set()   # contains the direct children it owns
        self.resources = defaultdict(int) # <key> resource type: <value> instances held/using
    
    def get_priority(self):
        return self.priority

    def get_state(self):
        return self.state
    
    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_resources(self):
        return self.resources

    def set_state(self, new_state: int):
        """
        Change the state of the process to the specified argument.
        
        :param new_state: new state
        """
        self.state = new_state

    def add_child(self, child_pid: int):
        """
        Add child passed through to set of children this process is parent of.
        
        :param child_pid: child to be added
        """
        self.children.add(child_pid)

    def remove_child(self, child_pid: int):
        """
        Remove child passed through from set of children.
        
        :param child_pid: child to be removed
        """
        self.children.remove(child_pid)
    

    def add_resources(self, resource_type: int, amt_instances: int):
        """
        Add resource type and amount of units this process is now holding
        to its dictionary of resources.
        
        :param resource_type: resource type acquired
        :param amt_instances: amount of units for resource type acquired
        """
        self.resources[resource_type] += amt_instances

    def rem_resources(self, resource_type: int, amt_instances: int):
        """
        Remove resource type and amount of units this process is holding
        from its dictionary of resources.
        
        :param resource_type: resource type being released
        :param amt_instances: amount of units for resource type being released
        """
        self.resources[resource_type] -= amt_instances

    def __str__(self):
        return f"Priority={self.priority} | State={self.state} | Parent={self.parent} | Children={self.children} | Resources={self.resources}"

class ResourceControlBlock:
    """
    A class to represent a Resource Control Block (RCB).

    Attributes
    ----------
    inventory : int
        total amount of units this resource has (available or being used),
        value does not change once RCB is created
    state : int
        how many units are currently available
    waitlist : deque
        queue of processes requesting some amount of units for this
        resource that may not be avaialable yet
    """
    def __init__(self, inventory: int):
        self.inventory = inventory  # amount of total units initially available
        self.state = inventory  # how many units are still LEFT
        self.waitlist = deque() # contains tuple(pid, num_units_requested)

    def get_inventory(self):
        return self.inventory

    def get_state(self):
        return self.state

    def get_front_waiting(self):
        """
        Get the front tuple in the waiting list.

        :return: Tuple(process ID, number of units) requested 
        of the tuple in the front of the line
        """
        if len(self.waitlist) != 0:
            return self.waitlist[0]
        else:
            return (-1, -1) # treat as (nothing in waitlist)

    def decrease_state(self, num_units_used: int):
        """
        Decrease the state of the resource by amount specified.

        :param num_units_used: amount of units that were allocated to some process
        """
        self.state -= num_units_used

    def increase_state(self, num_units_released: int):
        """
        Increase the state of the resource by amount specified.

        :param num_units_released: amount of units that were released by some process
        """
        self.state += num_units_released

    def remove_front_waiting(self):
        """
        Remove the front in line process tuple from the waitlist.
        """
        if len(self.waitlist) != 0:
            # state is dealt with externally
            self.waitlist.popleft()

    def try_and_remove_from_waiting(self, pid: int):
        """
        Check if process ID's tuple exists in this waitlist,
        and if so, remove the tuple of the process ID given from the waitlist
        no matter where it is in the queue.

        :param pid: process id of process we want to remove from the waiting list 
        :return: 0 on success, -1 on no hit
        """
        for tuple_element in self.waitlist:
            if tuple_element[0] == pid:
                self.waitlist.remove(tuple_element)
                return 0
        return -1

    # call anytime some new request is given
    def add_back_waiting(self, pid_and_num_units: Tuple[int, int]):
        """
        Add the tuple of the process ID and the number of units requested
        to the back of the waitlist/queue for this resource.

        :param pid_and_num_units: Tuple of process id, and number of units requested
        """ 
        self.waitlist.append(pid_and_num_units)

    def __str__(self):
        return f"Inventory={self.inventory} | State={self.state} | Waitlist={self.waitlist}"


def init():
    """
    Initializes all data structures (PCB, RCB, RL) 
    with correct initial state.
    """
    # create 16 spots for PCB'S
    for i in range(len(PCB)):
        if i == 0:
            PCB[i] = ProcessControlBlock(priority=0, state=1)
        else:
            PCB[i] = ProcessControlBlock()  # erase any content that was previously in it
    # create 4 different resource types with different unit amounts
    for i in range(len(RCB)):
        if i <= 1:
            RCB[i] = ResourceControlBlock(1)
        elif i == 2:
            RCB[i] = ResourceControlBlock(2)
        else:
            RCB[i] = ResourceControlBlock(3)
    # create three different ready lists (one per priority) and insert process 0 into priority 0
    for i in range(len(RL)):
        RL[i] = deque()
        if i == 0:
            RL[i].append(0) # process 0 is the one "running" / head of the ready list

def scheduler():
    """
    Prints out the currently running process.
    """
    for i in range(len(RL)-1, -1, -1):
        # go in reverse order of priority
        if len(RL[i]) != 0:
            print(RL[i][0], end="")
            break

def timeout():
    """
    Moves the currently running process to the back of the
    priority queue in which it resides which may change
    the current running process if more than 1 process exists
    in that specified priority queue.
    """

    # cannot throw error
    for i in range(len(RL)-1, -1, -1):
        # go in reverse order of priority
        if len(RL[i]) != 0:
            RL[i].append(RL[i][0]) # append the head to the tail of the queue
            RL[i].popleft() # remove the element at the head since it is now in the back
            break

def create(priority_given: int):
    """
    Moves the currently running process to the back of the
    priority queue in which it resides which may change
    the current running process if more than 1 process exists
    in that specified priority queue.

    :param priority_given: specifies which queue process should be placed in
    :return: -1 for error, None for success
    """

    # checks with priority_given
    if priority_given < 0 or priority_given >= 3:
        # invalid priority_given value passed so we need to throw some indication of an error
        return -1
    
    # find which process is currently running
    currently_running = -1  # dummy value until assigned in for loop
    for i in range(len(RL)-1, -1, -1):
        # go in reverse order of priority
        if len(RL[i]) != 0:
            currently_running = RL[i][0]   # store the running process into parent variable
            break

    enough_space_flag = False
    for i in range(len(PCB)):
        if PCB[i].get_priority() < 0:   
            # allocate new PCB into first invalid priority value which is lowest free PCB index (process ID)
            PCB[i] = ProcessControlBlock(priority=priority_given, state=1, parent=currently_running)
            # add this new process id into list of children of currently_running process
            PCB[currently_running].add_child(i) 
            # insert new process PCB[i] into RL
            RL[priority_given].append(i)
            # found empty PCB flag
            enough_space_flag = True
            # break out of loop
            break
    
    if not enough_space_flag:
        return -1

def request(resource_index: int, num_units: int):
    """
    Grants resource and number of units requested to 
    currently running process if available. 
    If not, then places the process on a waiting list.

    :param resource_index: which resource type is being requested
    :param num_units: amount of units requested for the resource_index
    :return: -1 for error, None for success
    """
    # error checks
    # 1) resource_index exists
    if resource_index not in {0, 1, 2, 3}:
        return -1

    # 2) num_units is not negative
    if num_units < 0:
        return -1
    
    # 3) num_units requested + num_units_already_held must be <= initial inventory
    # get num_units_already_held by getting current running process in RL
    currently_running = -1  # dummy value until assigned in for loop
    num_units_already_held = 0
    for i in range(len(RL)-1, -1, -1):
        # go in reverse order of priority
        if len(RL[i]) != 0:
            currently_running = RL[i][0]
            if resource_index in PCB[currently_running].get_resources():
                num_units_already_held = (PCB[currently_running].get_resources())[resource_index]
            break
    if (num_units + num_units_already_held) > RCB[resource_index].get_inventory():
        return -1
    
    # 4) if currently_running is process 0, we cannot allow it
    if currently_running == 0:
        return -1
    
    # 5) cannot request 0 units of anything
    if num_units == 0:
        return -1    # illegal to request 0 units

    # now can implement actual functionality (2 Possible Paths)
    if num_units <= RCB[resource_index].get_state():
        # then we can grant this request
        RCB[resource_index].decrease_state(num_units)
        PCB[currently_running].add_resources(resource_index, num_units)
    else:
        # CANNOT grant request
        # set state to blocked
        PCB[currently_running].set_state(0) # 0 = blocked state indicator
        # remove process from ready list
        RL[PCB[currently_running].get_priority()].remove(currently_running)
        # insert (pid, num_units) requested into waitlist
        RCB[resource_index].add_back_waiting((currently_running, num_units))

def grant_possible_waiting_requests(resource_index: int):
    """
    After some resource state is increased, it will 
    go through the waitlist in order of arrival for 
    that particular resource index and
    moves processes to the ready list if it can
    satisfy the waiting requests. Breaks out of the loop
    once the process in front of the line cannot be granted
    its request.
    

    :param resource_index:  resource type of waiting list to go through
    """
    # while loop
    while (RCB[resource_index].get_front_waiting() != (-1, -1) and RCB[resource_index].get_state() > 0):
        # get the next waiting process and amount tuple for the resource
        front_in_line = RCB[resource_index].get_front_waiting()
        # if we have enough resources to satisfy the request of a waiting process, enter
        if RCB[resource_index].get_state() >= front_in_line[1]:
            # decrease amount of available units for that resource
            RCB[resource_index].decrease_state(front_in_line[1])
            # add resource into PCB
            PCB[front_in_line[0]].add_resources(resource_index, front_in_line[1])
            # set the state to ready in the PCB
            PCB[front_in_line[0]].set_state(1)  # 1 == ready state
            # remove this process from the waiting list
            RCB[resource_index].remove_front_waiting()
            # put this process back into the ready lists
            RL[PCB[front_in_line[0]].get_priority()].append(front_in_line[0])
        else:
            break

def release(resource_index: int, num_units: int):
    """
    Releases resource and number of units held by currently
    running process.

    :param resource_index: which resource type is being released
    :param num_units: amount of units released for the resource_index
    :return: -1 for error, None for success
    """
    # error checks
    # 1) resource_index exists
    if resource_index not in {0, 1, 2, 3}:
        return -1

    # 2) num_units is not negative
    if num_units < 0:
        return -1
    
    # 3) num_units released must be <= num_units_already_held
    # get num_units_already_held by getting current running process in RL
    currently_running = -1  # dummy value until assigned in for loop
    num_units_already_held = 0
    for i in range(len(RL)-1, -1, -1):
        # go in reverse order of priority
        if len(RL[i]) != 0:
            currently_running = RL[i][0]
            if resource_index in PCB[currently_running].get_resources():
                num_units_already_held = (PCB[currently_running].get_resources())[resource_index]
            break
    if num_units > num_units_already_held:
        return -1
    
    # 4) cannot release 0 units
    if num_units == 0:
        return -1 # illegal to release 0 units

    # decrement resources in PCB tracker
    PCB[currently_running].rem_resources(resource_index, num_units)
    # increment state of RCB by amount released
    RCB[resource_index].increase_state(num_units)
    # go through waiting list of resource and try moving processes to RL
    grant_possible_waiting_requests(resource_index)

def destroy(child_id: int, initial_call: bool = True):
    """
    Recursively destroys process passed through and all descendants
    of the process. this includes freeing index from PCB, all resources,
    removing from RL or waitlist, and some more things.

    :param child_id: process ID of process that will be destroyed (and descendants)
    :param initial_call: if True, must do error checks, else, destroy
    :return: -1 for error, None for success
    """
    if initial_call:
        currently_running = -1  # dummy value until assigned in for loop
        # only get currently running process for the initial error check
        for i in range(len(RL)-1, -1, -1):
            # go in reverse order of priority
            if len(RL[i]) != 0:
                currently_running = RL[i][0]
                break
        if child_id != currently_running and child_id not in PCB[currently_running].get_children():
            # not allowed to destroy process if not itself or not direct child (includes cases with invalid PID's)
            return -1
        elif child_id == 0:
            # not allowed to destroy init process (process 0)
            return -1
        
    # recursively destroy all the children
    all_children = set(PCB[child_id].get_children())
    for direct_child in all_children:
        destroy(direct_child, False)
    # remove the process being destroyed from the parents' children list
    PCB[PCB[child_id].get_parent()].remove_child(child_id)
    # remove the process from either the ready list / waiting list of some resource
    if PCB[child_id].get_state() == 1:
        # then get it off the ready list
        RL[PCB[child_id].get_priority()].remove(child_id)
    else:
        # then the process is blocked
        # find which resource and try removing it
        for i in range(4):
            if RCB[i].try_and_remove_from_waiting(child_id) == 0:
                break   # found what it was blocked on and removed, so move on
    # now release all resources child_id is currently holding
    resources = PCB[child_id].get_resources()
    for resource_index, num_units in resources.items():
        # increment state of RCB by amount released
        RCB[resource_index].increase_state(num_units)
        # possibly move any processes that were waiting for 
        # that resource to the ready list
        grant_possible_waiting_requests(resource_index)
    # free PCB of j
    PCB[child_id] = ProcessControlBlock()

def print_formatted_error():
    """
    Checks global variable to see how to format
    and print -1 to terminal.
    """
    global new_set_of_commands_flag
    if new_set_of_commands_flag:
        print(-1, end="")
        new_set_of_commands_flag = False
    else:
        print(" -1", end="")

def debug_data_structures():
    """
    Prints all datastructures for debugging.
    """
    print("-------START DEBUG-------")
    # print the 16 PCB'S
    print("All Processes...")
    for i in range(len(PCB)):
        print(f"\tProcess {i}: {PCB[i]}")
       
    # print 4 different resource types with different unit amounts
    print("All resources...")
    for i in range(len(RCB)):
        print(f"\tResource {i}")
        print(f"\t{RCB[i]}")
        
    # print 3 different ready lists (one per priority)
    print("Ready lists...")
    for i in range(len(RL)):
        print(f"\tPriority {i}")
        print(f"\t{RL[i]}")
    
    print("-------END DEBUG---------")



if __name__ == "__main__":
    with open("commands1.txt", "r") as command_shell:
        for command in command_shell:
            # get command without extra spaces
            command = command.strip()
            # parse commands into list of strings
            separated_command = command.split()
            # check which command was given
            if command == "":
                print() # serve as the newline on current line
                new_set_of_commands_flag = True
                continue 
            elif command == "in":
                init()
            elif command == "to":
                timeout()
            elif separated_command[0] == "cr":
                # separated_command[1] has priority level
                if create(int(separated_command[1])) == -1:
                    print_formatted_error()
                    continue # don't want to call scheduler again
            elif separated_command[0] == "de":
                # separated_command[1] is the process id
                if destroy(int(separated_command[1])) == -1:
                    print_formatted_error()
                    continue # don't want to call scheduler again

            elif separated_command[0] == "rq":
                if request(int(separated_command[1]), int(separated_command[2])) == -1:
                    print_formatted_error()
                    continue # don't want to call scheduler again
            elif separated_command[0] == "rl":
                if release(int(separated_command[1]), int(separated_command[2])) == -1:
                    print_formatted_error()
                    continue # don't want to call scheduler again
            
            # after every command,
            if new_set_of_commands_flag:
                scheduler()
                new_set_of_commands_flag = False
            else:
                print(" ", end="")
                scheduler()

    