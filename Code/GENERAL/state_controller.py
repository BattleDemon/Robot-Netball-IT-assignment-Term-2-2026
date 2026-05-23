

# States
class State():
    IDLE = 1
    FOUL = 2
    PASSING = 3
    RETRIEVING = 4
    LOCATING = 5
    POSITIONING = 6

# State Machine
class State_Controller():
    def __init__(self):
        self.state = State.IDLE