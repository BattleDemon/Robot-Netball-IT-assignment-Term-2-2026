# Robotic Netball

## Preplanning 

#### Game Play Strategy 

The strategy for game play we set out to follow, used two robots one whose primary function was that of the attacker / shooter, and that of the defender / retriever, who together would work to find the ball, position the attacker near the hoop, pass the ball to the attacker, which would then shoot and hopefully score. With this process hopefully been completed without foul or flaw until the game is called, although methods will be implemented to deal with such situations.

#### General Design and Plan for Robots

###### Initial Meeting

The initial meeting was surprisingly productive, resulting in a general plan for both robots and several early design decisions.

**The Two Robots**

*Defending Robot*

- Locates and retrieves the ball.
    
- Passes the ball to the attacking robot.
    
- Prevents opponents from shooting by using a shield wall.
    
- Acts as the primary robot, sending requests and signals to the attacking robot.
    

*Attacking Robot*

- Receives the ball from the defending robot.
    
- Shoots the ball into the hoop.
    
- Responds to requests from the defending robot.
    

Additionally, we considered using another communicating EV3 as a static navigation system. This EV3 would remain in the middle of the field and contain an IR detector and several ultrasonic sensors. Its purpose would be to provide a secondary reference point for locating the ball and tracking the movement of the robots. However, this idea was later rejected as it was overly complex, would likely obstruct gameplay, and exceeded the number of communicating EV3 units available to us.

This meeting also produced the first concept for the defending robot's ball-handling system. The design used two counter-rotating motors to create a flywheel-like intake effect that would pull the ball into a holding chamber. Once the ball entered the chamber, a colour sensor would detect it and trigger the chamber to close while simultaneously reversing the flywheels. After the robot positioned itself for a pass, the chamber would open and the ball would be propelled outward by the flywheels.

We also considered an alternative design. Rather than physically blocking the chamber, the ball would simply remain within it until being pushed towards the flywheels. In the original concept, a ramp was blocked by a lid, which would then move to allow the ball to roll towards the flywheels. In the alternative design, the pushing mechanism itself would provide the initial motion required to feed the ball into the flywheels.

We also brainstormed methods for movement and aiming. Rather than using a separate aiming turret, aiming would be incorporated into the movement system itself, requiring the entire robot to rotate in order to aim.

Navigation would be performed using wheel rotations to calculate a theoretical position while also using a gyro sensor to verify the robot's heading. The gyro readings would be compared against the calculated position and orientation to improve the accuracy of the robot's estimated location.

We also decided that slower movement would be preferable, as it would increase the accuracy of sensor readings and reduce wheel slip and positional drift.

This meeting also generated some early ideas for the attacking robot. One concept involved a turret or trebuchet-style launcher, using a basket in which the ball would sit before being launched towards the hoop.

Additionally, we decided that, for the defending robot to perform all of its required functions, it would need to use two EV3 bricks. One EV3 would control movement, communication, and the shield mechanism, while the second EV3 would control the flywheel system.

Another system conceived during this meeting was the shield. This would consist of an arm attached to the defending robot that would remain perpendicular to the ground and could be raised or lowered to block an opponent's shot.

It is also clear that this early meeting placed considerably less emphasis on the attacking robot. Even at this stage, we did not envision it being capable of moving independently or calculating its own local ball position. Instead, it would remain near the hoop and wait for the defending robot to pass the ball to it.

###### Diagrams of Initial Designs

The initial meeting gave the first rough designs of our robot, which included the ball containment chamber, its release gate, the flywheel ball catcher and thrower, along with the recognition it would require two EV3's.

**Early Full Diagram**
![[PXL_20260430_020519027.jpg]]

**Ball Thrower Early Diagram**
![[PXL_20260430_198.jpg]]

**Early EV3 Port Map**
![[Documentation/Dexter Documetation Unique Images/PXL_20260430_015133398.jpg]]

Additionally this early meeting provided an early version of the Attackers design, and although that was not my focus It can still be shown here.

**Early Attacker Design**
![[_20260430_015133398.jpg]]

###### Initial Sensors and their Uses

The initial sensors designed for use on our two robots were as follows:

Attacker
    2 Motors - Used for movement and navigation.
    Colour Sensor - Used to observe the ground and check if the robot is in the foul zone and for additional navigattion checks.
    IR Sensor - Used to locate the ball.
    Unfortionatly i the Attacking robot wasn't as preplanned as the defending robot, causing many of its later sensors to not be planned at this point.

Defender
    2 EV3's - One Used as the main controller, communicator, and navigator, and the other purely dedicated to the flywheel system.
    2 Motors - Again used for movement and navigation.
    Another 2 Motors - Used for the ball retrieve and passing, as flywheels.
    A single motor - To release the ball from its container.
    2 Colour Sensors - Used to detect if a ball is within the container, one for each EV3.
    Another Colour sensor - Similar to the Attacker, this colour sensor is used for ground detection.
    A Gyro - Used as a secondary navigation checker.
    Lastly an IR Sensor - Also used to locate the ball.


#### Flowcharts of Gameplay


![[mermaid-diagram-2026-06-02-231645.png]]
#### Flowchart of Systems

The Systems we are planning to make can be roughly connected as shown.

![[mermaid-diagram-2026-06-02-211710.png]]

#### Division of Tasks and Systems

In order to fulfil the requirements of equally split work, we have split into two teams of two with each designing one robot, and their individual systems, and the shared systems were split to ensure a consistent split of work.

The two teams are the Attack, Gabe and Zen, and the Defence, Hugo and I. These groups primarily designed and developed their robots before moving on to programming their respective individual systems.

These systems might of changed during development or who is doing them, the final division of tasks will be covered in the dedicated collaboration system.

The individual systems done by each are as follows:
Hugo
	Communication between robots.
	Actioning on states (IE. Connecting everyone's systems and calling the function in the main file).
	Ball grabbing and throwing.
Gabe 
	Movement of the Robot (Large system and his only system)
	Attackers Turret
Zen 
	IR Detection and triangulation.
	Attack grabber.
with the remaining been my responsibility and covered in the next section.

#### My Features and Systems

To satisfy the division of labour, I was tasked with completing the sections of code which i will go into more detail below, of the State Controller and state system, ground detection and the foul controller, as well as the aiming and pushing for the defensive robot.

###### Overview of the State System and Controller

The State System and Controller is set to be my largest and most important feature in this assignment, it will control what `State` the robots will be in and decide the logic for transitioning between states. Along with just controlling the individual robots state, it is also going to connect with the other robot in order to decide on their states collaboratively.

###### State Transitions Flowchart

The transition of states I have envisioned can be summed up by the following flowchart, although this also had the potential to change during development. 

![[mermaid-diagram-2026-06-02-193220.png]]

###### Transfer of information flowchart

With the State controller acting as the central information storage, I though it necessary to display how these are spread and read.

![[mermaid-diagram-2026-06-05-181301.png]]

###### State System and Controller Psuedocode

To help me produce this system I devised the following psuedocode.

``` Psuedocode

Import Required Packages

Enum State
	IDLE
	FOUL
	PASSING
	RETRIEVING
	LOCATING
	POSITIONING
	RECEIVING
	SHOOTING
	WAITING

Enum Request
	PASS
	RECIEVE
	RETRIEVE
	REPOSITION
	DECLINE
	NONE
	
Class State_controller
	INIT
		Robot Role (Attacker / Defender)
		Current State
		Other Robot State
		Position 
		Other Position
		Ball
		Ball Possession
		Request
		Ground Colour
		Foul timer status
		
	Function UpdatePosisition
		Get movement new position
		
	Function UpdateBallPosition
		Get ball position
		
	Function ToggleBallPossession
		True or False Ball Possession
		
	Function SetFoulState
		State = Foul
		Set foul elapsed false
		
	Function SetIdleState
		State = IDLE
		
	Function recieveSnapshot
		Save communication data
		
	Function CreateSnapshot
		Make communication data
		
	Function DetermineState
		If State = Foul 
			Return
			
		If State = Waiting
			
			If incoming request = Decline 
				request = None
			
			If incoming request = request
				If request = Pass 
					state = Passing
					
				If request = Recieve
					state = Recieving
				
				Return
				
			Return
		
		If incoming request
			Case incoming request
				
				Pass
					If can recieve ball
						state = recieving 
						reply recieving'
					else
						reply Decline
						
				Retrieve
					If robot has ball or is fouled
						reply Decline
					else
						state = Retrieving
					
				Reposition
					If robot is free to move
						State = positioning
					else 
						reply Decline
						
		If robot has ball is attack and is near hoop
			
			state = shooting
			return
			
		If robot has ball
			request = pass
			state = waiting
			return
		
		If neither has ball 
			
			If ball location is known
				If this robot is closer Or other is occupied
					If robot is attack and near hoop
						State = positioning
						request = retrieve
						
					else
						state = retrieve
						clear request
						
				else
					state = waiting
					request = retrieve
			
			If neither robot knows where ball is 
				State = locating
				clear request
				return
				
		State = Idle
		clear request

```

###### Overview of Ground Detection and Foul Controller

My next important system is the ground detection and foul controller system, as it was another of the general systems. Luckily it seemed to connect with my other system, and just directly resolved the foul state. In addition to the foul controller, it is planned to also observe the ground and provide that as a signal for Gabe's movement code, and act as a secondary navigation system using the lines on the third of the field. 

###### Ground Detection and Foul Controller Psuedocode 

``` Psuedocode

Import required packages

Class Ground Observer
	Init
		state controller
		state
		
		colour sensor
		
		observed colour
		currently fouled
		
		Thread observed ground
		start thread
		
	Function observe ground
		loop
			observed colour = colour sensor colour
			
			if observed colour = foul colour and not currently fouled
				call foul detected
				
			if currently foul
				if state controller state is not foul
					current foul = false
					
			call state_controller set ground colour
			
			wait
			
	Function foul detected
		currently foul = true
		
		call state controller set foul state
		
		Thread foul timer
		start thread
		
	Function foul timer
		wait foul time
		
		call state controller toggle foul elapsed
		

```

###### Overview of Aiming and Pushing

My last section, and smallest is only a system used for the Defending robot. This system needs to aim towards the other robot, then push the ball out of its container with a motor. 

###### Aiming and Pushing Psuedocode 

``` Psuedocode

Import required packages

Class Push and Aim
	Init
		push motor
		
	Function get aim angle
		get difference in x
		get difference in y
		
		get angle towards target
		
		localise angle with our heading
		
		Return angle
		
	Function Push
		run motor to push ball
		
		wait 
		
		run motor to return it to its initial point

```

###### Aiming Calculation

The aiming angle was found, as shown in the following diagram. 

![[IMG20260605185123.jpg]]
(Sorry for image quality, this is the best my phone can do)
#### Additional Features Incase of Extra Time

Although due to the scale of this assignment and its limitation some of these might not be practical or cause too much extra work. Some additional features which were considered to make, were that of the team system where the robots would stop communication and each be attempting to win, use separate hoops and attempt to block each other.

## Prototyping

#### Designing the Defence Robot

The designing of the defence robot was a collaborative process between Hugo and I, where I primarily focused on its chassis, making sure it could hold the weight of the other equipment as well as have enough space, while remaining in the 30cm diameter circle we are allowed. In addition to this i attached the IR sensor, colour sensors, motors (exclusing flywheel) and EV3's. While Hugo focused on building the flywheels system, and did most of its attaching to the chassis.

One of the first things done during the designing was figuring out the rough layout of the wheels, to allow the fly wheel and the ball to pass through. This produced this initial layout:

![[IMG20260501113020.jpg]]

This was then expanded on with the first sections of the chassis,

![[IMG20260501114103.jpg]]

Then after, finally realising our robot needs to work with the IR ball instead of the squash, produced this next prototype.

![[IMG20260501125135.jpg]]

This idea of a ball container, was pushed more with the addition of sides to the ramp, walls on its plat form an a rough back stopper. Additionally, this section saw the continued design of the chassis, to allow support for the other sensors and motors. Notice the supporting beams going across, which were used to hold the weight of the future sections, along with provide a suspension. 

![[Construction/Defence Robot/IMG20260506150838.jpg]]

This is then where Hugo and my development aligned, with the attachment of the "ball thrower", to the chassis. 

![[Documentation/PicsandVids/baseAndThrower.jpg]]

This addition produced some issues with the sizing and staying within the 30 cm circle, and the additional weight. This meant we needed to shorten the front section and add increasing support to the overall chassis.
With the following been the result of that process.

![[IMG20260518141517.jpg]]

###### Problems During Production

One of the main problems during the building, was the throwing system when it spins, it bends outwards loosening its grip on the ball. This issue was rectified by adding the curved pieces that go from the axle to the main chassis, this prevented the majority of that moving and solved this issue.

Another issue was the chassis been larger than the maximum 30 cm circle, which required both the back end and front to be shortened.

##### Final Design

The final design used can be seen in its sizing circle, and from many angles.

![[sizephoto2.jpg]]

![[sizephoto4.jpg]]

![[sizephoto6.jpg]]

![[sizephoto8.jpg]]

![[sizephoto9.jpg]]

#### The State Controller

###### Overview of State controller

The state controller acts as the central system, connecting all other systems to each other, it connects heavily with the communication system, to allow the robots to collaboratively decide on what to do using the "Requests" feature, and Hugo's communication code. 

###### Justification for State Controller

The addition of this system was necessary to control, the activities of the robot and ensure it maintained priority when deciding its next function. It also provided the systems for the robots to work collaboratively using requests. It also because the central hub, where information was stored and could be accessed from. 

###### State Controller Code Snippets 

The initial commit where the state controller was made, showed what would later evolve into its final design, and included early steps of the features and variables that would be used later.

``` Python
# First set of the state enums
class State(Enum):
	IDLE = 0
    FOUL = 1
    PASSING = 2
    RETRIEVING = 3
    LOCATING = 4
    POSITIONING = 5

# Request began as only a yes, no, or none. But this was later changed to specify the request and allow.
class Request(Enum):
	YES = 0
	NO = 1
	NONE = 2
	
class State_Controller():
	def __init__(self):
		# Define our state and create a variable to house the other robot's
		self.state = State.IDLE
		self.other_state: State
		
		# local refrence to our position and heading
		self.x_pos: float
		self.y_pos: float
		self.angle: float
		
		# others position
		self.others_x_pos: float
		self.others_y_pos: float
		self.others_angle: float
		
		# Knows if us or the other robot has the ball
		self.has_ball: bool
		self.other_has_ball: bool
		
		# our request to the other robot and their request to us
		self.request: Request
		self.incoming_request: Request

```

The next update included much more of the substance of the State_controller and the addition of more locally stored variables, this is also where it became the defacto brain/controller for everyone else to share their data.

``` Python

class State(Enum):
	# Including prior mentioned states
	RECIEVING = 6
	SHOOTING = 7
	WAITING = 8
	
class Request(Enum):
	# Replacing the initial version of Request
	# This allowed the robot to specify the request been made instead of it been assumed based on their state, then it allows them to either echo that back or decline, with NONE been the default when no request is been made.
	PASS = 0
	RECIEVE = 1
	RETRIEVE = 2
	REPOSITION = 3
	DECLINE = 4
	NONE = 5
	
class State_Controller():
# Init now allowed initialisations 
	def __init__(self, owner, x_pos, y_pos, angle, ball_angle, ball_dist):
	# Only showing differences since last time
		self.owner = owner
		
		self.others_state: State = State.IDLE
		
		self.position: tuple = (x_pos, y_pos, angle)
		
		self.ball_angle: float = ball_angle
		self.ball_dist: float = ball_dist
		
		# Same for others ball and position
		
		# Start both requst and incoming request as Request.NONE
		
	# This commit also added the helper functions to get and update the variables other systems needed to know.
	
	# The snapeshot system which packages the information Hugo needs to send to the other robot
	def get_snapshot(self):
		snapshot = {
			"state" : self.state,
			"position": self.position,
			"ball_angle": self.ball_angle,
			"ball_distance": self.ball_distance,
			"has_ball": self.has_ball,
			"request": self.requst
		}
		
	return snapshot
	
	# Hugo then sent me back a snapshot with the same structure which I then re assigned the "others_" variables

```

The next major addition to the state controller was the actual logic behind the determining of states and the state machine.

``` Python

# inside state_controller
def determine_state(self):
	# Check if currently foul 
	# Which has its own system for changing into and our of
	
	if self.state == State.FOUL:
		return
		
	# Waiting for a responce to a request 
	if self.state == State.WAITING:
			# other robot has declined the request
            if self.incoming_request == Request.DECLINE:
                self.request = Request.NONE

                self.state = State.IDLE
                
	        if self.incoming_request == self.request:
		        if self.request == Request.PASS:
			        self.state = State.PASSING
			        return
			    # Repeat for other possible requests
	# If there is an incoming request and we are not waiting
	if self.incoming_request != Request.NONE:
		if self.incoming_request == Request.PASS:
			# Check avaliability to pass 
			if not self.has_ball and self.state not state.SHOOTING:
				self.state = State.RECIEVING
				self.request = Request.RECIEVE # Echo back confirmation
				return
			else:
				# Decline request if it doesn't meet the requirments
				self.request = Request.DECLINE
				
		# Repeat similar logic for other requests
		
		
	# Now the what I call self determined state logic
	if self.has_ball and self.owner_type == "attack":
	# High priority state, set shooting
		self.state = State.SHOOTING
		self.request = Request.NONE
		return
	
	# Next priority state since if you have the ball you will need to get rid of it quick
	if self.has_ball:
		self.request = Requst.PASS
		self.state = State.WAITING
		Return
		
	# Next if no one has ball, determine who gets it
	if not self.has_ball and not self.others_has_ball:
	# If your closer or the other once is moving 
		if self.ball_sistance <= self.other_ball_dist or self.others_state == State.Positioning:
			if self.owner_type == "attack" and self.is_near_hoop:
			# The attacker been closer to the hoop is more important than the defence moving more.
				self.state = State.POSITIONING
				self.request = Request.RETREIVE
				return
			else:
				self.state = State.RETRIEVING
				self.request = Request.NONE
				return
				
		# Lastly if no one has the ball and no one knows where it is we need to find it
			self.state = State.LOCATING
			self.request = Request.NONE
			return
			
	# If none of the above is true become idle
	self.state = State.IDLE
	self.request = Request.NONE
	
```

This completed the majority of the state controller, with the only additions been made after this were renaming of variables, changing their type (tuple vs list ect), and making a few small helper functions for interaction between the systems.

###### Issues with the State controller

While developing the state control system, the following issues were encountered: 

###### Connection With Other Systems and Collaborators

Due to the state controller acting as the connecting system between others systems, it was necessary to include a `get` and `update` helper function for each variable as to allow for their systems to connect with each other. 

#### Foul Detection and Ground Observation

###### Overview of Foul Detection and Ground Observation

The aim for the "Foul Detection and Ground Observation" system, was for it to change the state to foul, after it detects it has been mover to the foul box, using its ground colour to detect. It was then originally intended to include the navigation back to the field, but Gabe did that before I could. The ground observation section, would constantly observe the ground and alert the state controller of any foul, while also saving what colour the ground is to a variable in state controller. This was then intended to be read by Gabe's movement code, allowing him to use it as a secondary navigation check, but i later on the day of submission learnt he hadn't done that despite his earlier assurance of its completion. 

###### Justification for Foul Detection and Ground Observation

Due to the rules, there needed to be a solution to handling when fouls are done. The ground colour, was the natural solution to this because the foul area is a separate colour to any other section of the field, making the difference in colour the obvious tell for if your in foul.

###### Foul Detection and Ground Observation Code Snippets 

The code for this section was generally simple and didn't require any changes beyond name changes or similar small things, such as removing daemon due to its non existence on micropython.

The colour observation function was used as a constantly running thread, which updated the observed colour on the state controller. 

``` Python
# In class Ground_observer
def observe_ground(self):
	# Loop forever
	while True:
		# Set the observed colour
		self.observed_colour = self.colour_sensor.color_name()
		
		# Start the foul detected if in foul and not fouling
		if self.observed_colour == FOUL_COLOUR and not self.currently_foul:
		self.on_foul_detected()
		
		# If fouling update if no longer
		if self.currently_foul:
		# Check state
		if self.state_controller.get_state() != State.FOUL:
		# turn currently foul off
		self.currently_foul = False
		
		# Updated state contellers local ground colour (so Gabe can use that as secondary navigation checker, and foul)
		self.state_controller.set_ground_colour(self.observed_colour)
		
		# Don't want to kill the CPU
		time.sleep(0.75)****

```

With on foul detected, starting a timer thread for the duration of the foul, which would then update state controllers foul elapsed variable.

``` Python

def on_foul_detected(self):
	# Set currently_foul local and state
	self.currently_foul = True
	self.state_controller.set_foul_state()
	
	# Start a timer thread
	timer_thread = Thread(target=self.foul_timer)
	# timer_thread.deamon = True
	timer_thread.start()

# The foul timer, so we don't stay fouled forever
def foul_timer(self):
	# Sleep for the foul time
	time.sleep(FOUL_TIME)
	
	# Tell state controller foul is over but don't change state (Need to return to field)
	self.state_controller.toggle_foul_elapsed()

```

###### Issues with the Foul Detection and Ground Observation

The only main issue with this system was my initial use of thread daemon, which doesn't exist on micropython and caused crashes when used.

###### Connection With Other Systems and Collaborators

As mentioned before this system was meant to connect with the movement and navigation systems, but those connections didn't end up been developed. 

#### Pushing Ball and Aiming
###### Overview of Pushing Ball and Aiming

The pushing ball and aiming system is a defence unique system that runs when the robot intends to pass the ball to the other robot. It calculated the aim angle, which is passed through a `movement.pivot`, to rotate the robot before using `push` to push the ball out of its container and down the ramp to the thrower. This motor is then returned to its original position.
 
###### Justification for Pushing Ball and Aiming

This system was need to allow the passing to work, since otherwise the ball would stay within the container indefinitely. 

###### Pushing Ball and Aiming Code Snippets 

This code was again generally simple, and didn't require any changes beyond fine tuning the amount the push motor turns.

```Python

class PushAndAim:
    def __init__(self, push_motor: Motor):
        # Locally store the inputed motor
        self.push_motor = push_motor

    # Calculate the angle between us and the other robot
    def get_aim_angle(self, our_position: tuple, others_position: tuple):

        # Locally assign x, y, and angle
        our_x, our_y, our_angle = our_position
        others_x, others_y, _ = others_position

        # Difference between theirs and ours
        dx = others_x - our_x
        dy = others_y - our_y

        # The tangen (with both y and x to find its quadrant)
        target_angle = atan2(dy, dx)

        # Angle between
        angle_between = target_angle - our_angle

        # Normilise the angle
        angle_between = (angle_between) % (2 * pi)

        return angle_between

    # Push the ball
    def push(self):
        # Push the ball with the motor
        self.push_motor.run_angle(120, 85)

        # wait a short time
        time.sleep(0.5)

        # Return motor to initial place
        self.push_motor.run_angle(-120, 85)
```

###### Connection With Other Systems and Collaborators

A good unintentional connection my system did, was this idea of aiming at the other robot / getting the angle to the other robot was a common idea and useful for many things, causing my `get_aim_angle` function to be used throughout the entire project. 

## Collaboration

#### How Work Was Divided

As covered before the robots were split into teams of two, and the individual sections of code were split between individuals.

For the individual sections of code, as to not force one person to do more than their fair share of work we set a rough 400 lines of code limit per person, which seemed to split the systems quite evenly among us, but did require some shifting around of responsibilities, as at that point Gabe had already produced his movement code which was at the 400 line section, and he was planned to complete one or two other sections, meaning these had to be re assigned. 

The choice of who was responsible for a section of wasn't the most thought out process, but some systems were just expansions of the testing code so it naturally followed that those who made the test continued their development. Individuals also requested to do certain features, such as the State Controller in my case, and the movement in Gabe's. We also for the most part we tried to keep the code that would only be used by one robot, been made by a person who build that robot. We also tried to assign a major / important system to everyone. 

This meant Hugo, developed the communication system, I did the state controller, Gabe did the movement, and Zen the IR triangulation. With any other systems, been assigned using the rules stated prior.

#### How collaboration was handled

The actual collaboration was handled using GitHub, and its "Projects" feature within a repository. We all used the same git repository, and used GitHub to store in online, to view the repository (although I acknowledge it is an online and updatable source, It should be use full to see the commit history, and branch history) https://github.com/BattleDemon/Robot-Netball-IT-assignment-Term-2-2026. For each feature we worked on, we would create a branch from the main, program all our features within that branch, then request to merge our code with the repositories. This was done using pull request, which to insure we only merged good code, either Hugo or I, would look over the merger's code, with for important features we would both look over, and when we were the merger we would have the other look over it for us. This was due to us been the most knowledgeable at both GitHub, and programming in general, and allowed us to catch problems in the code and missing logic. As part of a pull request, we would comment of individuals code, pointing out the mistakes for them to fix on their own, before either confirm it was able to be merged or declining the request and asking for the issues to be fixed. 

This allowed us to create a visual representation of the timeline for our development, the red line marks the due date.
![[Projects.png]]

Additionally, here is a table of the branches used during development,

![[BranchTable.png|697]]

Peoples contributions were also recorded within this graph here, where you can see a heavy section at the end, rather than a more spread out development.
![[CommitsOverTime.png]]

This can also be viewed individually, with me as the top contributor, although this could be due to my tendencies to over commit for every minor change. Hugo, Gabe, and Zen followed in order.   
![[CommitsIndividual.png]]
#### Hugo's Contributions

Hugo was responsible for the Defending main file, which defines everything and begins the robots, and after neither Gabe nor Zen agreed to do the attacking one, Hugo also made their version. 
Additionally, Hugo developed the actioning of states systems, which followed the plans I had set out with my state machine, and connected that to the other systems to allow for the robot to actual function.
He developed the communication between robots, which after a quick chat we agreed I would give him a dictionary and he would return one, which we ended up doing and didn't change after that.
During the designing of the defence robot, he made the throwing and catching code.
Both Him and I, assisted in explanation of maths for others features.
Designed the defence robot along with me, with him focusing on the throwing and catching system.
Additionally, both of us attempted to keep every one on track, with us setting dead line on occasion which were then ignored by others.
Helped Gabe with his code on the night before submission, though pull requests and comments. 
Only real complaint is he began the last sections of his code too late, although this was more acceptable since he is a proficient enough programmer to finish in such short time. What didn't help that was his last feature relied on other systems which bottle necked his development. 
Another, small complaint was on the due day, in times where we could of been bug fixing, Hugo was scrolling reels, luckily this was short lived and he stepped up soon after. 

#### Gabe's Contributions 

Gabe ended up making the Movement and Navigation systems, with him volunteering to do this system and seeming sense of ability to complete it quickly. He worked off of a template from Hugo's first term work, and expanded it to meet the necessary features, although he would constantly add back redundant sections or duplicate the same sections of code under a new function. This along with, often check in's with him to see how he was doing with implementing the response to the colour detection, with in two occasions after i had made my feature and instructed him on how to connect them by using `self.state_controller.get_ground_colour`, found him either making his own colour detection system within his movement code, or not handling it at all. Additionally while i was developing the foul detection code which originally intended to also do the returning to field, found that despite telling him in a meeting of this, that his movement code was doing that for me. 

Beyond the initial confusion and troubles, the night before the assignment was due Gabe said he need to fix some things, which evolved into both Hugo, Him, and Me spending large parts of that night fixing mistakes in his code. Which was done through pull request, and leaving feed back on his code, which he would follow to fix.

Additionally on the day before submission Gabe kept assuring me he was able to have a meeting, so we could fix code, with this meeting originally intended for morning tea, but with Gabe cancelling due to him forgetting about another commitment, which on its own wouldn't of been a problem. This was followed with the promise of doing the meeting during the middle period, which Gabe proceeded to miss, along with the third agreed upon time of lunch time.

#### Zen's Contributions 

Zen was responsible for the IR controller, and the "Triangulation" of the balls position, although this ended up becoming the distance to the ball, rather than an (x,y). This system was originally going to be me, but Zen offered to do it. This probably wasn't the best choice for me to agree since his mathematical ability made its development a more complex task then it was need. That slight problem compounded by him not starting programming until, at most Tuesday of the week it was due, and not completing it until the night prior. 

Zen also was responsible for the two of the Attacking robot's  individual features, with those been the `Grabbing ball with claw`, and the `Ball throwing`. These from my knowledge were not started until the day of submission, and not completed until lunch time. This i believe is due to the major lack of general plan put into the design of the attacking robot, which prevented the systems he was responsible for to be properly defined long enough before the due date (and time), to allow time for development.

Then when were were getting close to fixing the bugs with both the robots codes and it was looking like they might be able to run, Zen left after lunch instead of staying to attempt to fix any errors. But this is also somewhat acceptable due to his lack of general programming knowledge, preventing him from successfully locating bugs. Along with the complex and confusing even to Hugo and I, of Gabe's code which i don't think Zen would of been able to do anything to remedy. 

#### My Contributions 

In addition to my code contribution which I covered before I have contributed in the following ways.

* The state_controller
* The ground observation and foul detection
* The pushing and aim
* Explained how to use my state controller as the "central" information point, this included attempting to get people to connect their systems properly.
* Explained maths behind finding the distance to ball for the Ir sensor along with Hugo
* Designed and built the defence robot
* Helping others with code
* Explained OOP and helped teach basics on its uses and implementation
* Attempting to keep people on track, by setting dead lines and checking in with others
* Reviewed the pull requests in an attempt to catch problematic code and bugs, with this been what i spent most of the 8 hour meeting doing
* First section of 8 hour meeting, essential coaching Zen through development of the IR controller

#### Attacking Design

I apologies if this section is too harsh or accusatory, but both Zen and Gabe jumped straight into the building of their robot without taking much account into its design, the features it needed, and general capabilities. To attempt to assist with this, both Hugo and I attempted to suggest they plan certain features beforehand, as well as pointed out systems which seemed unlikely to work such as their trebuche, which they decided on following any way.

#### The Night Before Due

The night before the due date, we all agreed to join a discord call at 4:30, with me joining slightly early in case anyone wanted to talk, followed by Hugo at the correct time. During the time it was just us we discussed, writing of documentation and what needed fixing that night. Later, at around 5:30 Zen joined and we spend the next 1-2 hours working on his IR, though a series of him coding, us reviewing and providing feedback, until it was decided it was good enough. This was followed by Zen leaving at around 7:30. Then at 7:45, Gabe joined, then for the next 2 hours we continue working independently, with minor feedback, due to us taking breaks for dinner. But 

#### The Day It's Due

#### Challenges of a Group Project

* Tasks could have been divided better, giving the more mathematically complex tasks to the people necessary, etc.
- People could have started coding earlier (Zen).
- Some people could have been more independent in the decision-making.
- Deadlines could have been followed (Monday, then Tuesday, then Wednesday overshot).
- More team meetings.
- Meetings, when held, could have actually occurred if people had told or organised their other activities better.
- Explanation of systems connection could have been better.
- Attackers could have spent more time designing prior to development.
- Start and finish things earlier (to allow for testing time).
- Could show up to meetings / show up on time.
- Communication between people could have been better.
- When communication / instruction on connecting systems was given, that could have been followed.
- Asked for help from Tim sooner / at all.
- Dividing time between features and designing.
- Didn't test.
- Wasn't time to test.
- Systems not being ready prevented testing.
- Call on the day before the due date intended to fix all mistakes, etc. People: Zen showed up (5:30-5:45, left at 7:20) and Gabe showed up (7:45), Dexter and Hugo showed up on time: 4:30 (agreed-upon time).
- Member required explanation on importing from others' code.
- People need to change placeholders to actual things when needed (my foul system wasn't connected with Gabe's code at all because he used local placeholders instead of connecting with mine).
## Evidence of Working Systems

Here we can see the throwing system working.

![[Documentation/PicsandVids/ThrowingAndCatchingDemo.mp4]]

Also apologies, additional working systems which have videos are not loading for me, instead appearing as sound files still with `.mp4`. I attempted to have Hugo send them to me though other means, but they are too large for any we have tried. So if possible please refer to the video's of working systems on Hugo's documentation.

## Reflection 

#### What do you think of the overall design?
#### How did working in a group effect you and the project?
#### How successful were you as part of a group?
#### What changes would you make?
#### What issues did you experience?
#### What techniques did you use to solve these issues?
#### What changes would you make if repeating this project?
#### What have you learnt from the project? 

## References 

https://mermaid.live/

https://pybricks.com/ev3-micropython/ev3devices.html 

https://github.com/

https://github.com/BattleDemon/Robot-Netball-IT-assignment-Term-2-2026