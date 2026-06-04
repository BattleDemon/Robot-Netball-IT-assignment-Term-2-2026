# Robotic Netball

## Preplanning 

#### Game Play Strategy 

The strategy for game play we set out to follow, used two robots one whose primary function was that of the attacker / shooter, and that of the defender / retriever, who together would work to find the ball, position the attacker near the hoop, pass the ball to the attacker, which would then shoot and hopefully score. With this process hopefully been completed without foul or flaw until the game is called, although methods will be implemented to deal with such situations.

#### General Design and Plan for Robots

###### Initial Meeting

The Initial meeting was surprisingly productive, resulting in our general plan for the two robots and some early design choices.

The Two Robots
* Defending Robot 
	* Locates and Retrieves the ball.
	* Passes the ball to the other robot.
	* Prevent Opposing Shooting, using a wall.
	* Acts as the Main robot, with it sending requests and signals to the other.
* Attacking Robot
	* Receives the ball from the Defending Robot.
	* Shoots the ball into the hoop.
	* Responds to requests from the Defence robot.

Additionally, we also considered the ideas of using another communicating EV3 as a static navigation system, which would remain in the middle of the field and have one of the IR detectors and a some ultrasonic. Its goal is to provide a secondary location for both the ball and using the ultrasonic for the moving robots, although this ideas was later struck down, as too complex, would get in the way, and due to our lack of communicating EV3's. 

This meeting also produced the ideation for the first system, that of the Defence's ball handling. The idea used two counter rotating motors which would make a soft of flywheel / suction effect that would full the ball into a chamber which would then be shut. A colour sensor would be used to detect when the ball entered the chamber and trigger its shutting, along with reversing the rotation of the flywheel. Then once the robot positions its self, the chamber would open releasing the ball which would be pushed out using the flywheels. Additionally we considered another option which instead of physically blocking the chamber we could just make it sit in the chamber until pushed out. (the first option had a ramp, which the lid would block and them be moved allowing the ball to roll to the flywheel, while this second idea would use the pushing motion to give it the intial motion to the fly wheels)

We also brainstormed methods for handleing the movement and aiming.
With aiming been handled as a subsection of moving rather than its own seperate turret. With the robot needing to entirely turn to aim.

The navigation would be proformed by both using the motor turns to calculate a theoretical position aswell as useing a gyro sensor to confirm our correct calculation of the angle. This would then be checked against out theoretical and then be used to estimate the true position.

We also decided that moving slower would be the best option as it would incease accuracy of our reading and prevent any slip or drift.

This meeting also produced some early ideas for the Attacking robot, with it possesing a turret / trebuche design, using a basket the ball would sit in before been flung towards the hoop. 

Additionally we decided for the Defending robot to be able to do everything we needed, we would need to use two EV3 blocks, one would control the movement, shield, and communication, while the other would control the flywheel. 

Another system this meeting produced was the shield, which would be an arm attached to the Defending robot which would stay perpendicular to the ground and could be raised or lowered to prevent an opponents shooting.

It is also clear this early meeting dismissed much of the attacking robot, with us even in this stage not envisioning it been able to move and not calculate its own local ball position. It would stay next to the hoop and wait for the defender to pass to it.

###### Diagrams of Initial Designs

The initial meeting gave the first rough designs of our robot, which included the ball containment chamber, its release gate, the flywheel ball catcher and thrower, along with the recognition it would require two EV3's.

**Early Full Diagram**
![[PXL_20260430_020519027.jpg]]

**Ball Thrower Early Diagram**
![[PXL_20260430_198.jpg]]

**Early EV3 Port Map **
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

To satisfy the division of labour I was tasked with completing the sections of code which i will go into more detail below, of State Controller and System, Ground detection and foul controller, and the Aiming and Pushing of the defensive robot.

###### Overview of the State System and Controller

The State System and Controller is set to be my largest and most important feature in this codebase, it will control what State the robots would be in and decide the logic for transitioning between states. Along with just controlling the individual robots state, it is also going to connect with the other robot in order to decide on collaborative states.

###### State Transitions Flowchart

The transition of states i have envisioned can be summed up by the following flowchart

![[mermaid-diagram-2026-06-02-193220.png]]

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
#### Additional Features Incase of Extra Time

Although due to the scale of this assignment and its limitation some of these might not be practical or cause too much extra work. Some additional features which I considered to made, were that of the team system where the robots would stop communication and each be attempting to win, use separate hoops and attempt to block each other.

## Prototyping

#### Designing the Defence Robot

###### Problems During Production

###### Design Notes and Justification

##### Final Design

#### The State Controller

###### Overview of State controller



###### Justification for State Controller

The addition of this system was nessessary to control, the activities of the robot and ensure it maintained priority when deciding its next function. It also provided the systems for the robots to work collaborativly using requests.

###### State Controller Code Snippets 

###### Issues with the State controller

While developing the state control system, the following issues were encountered: 

###### Connection With Other Systems and Collaborators

#### Foul Detection and Ground Observation

###### Overview of Foul Detection and Ground Observation
###### Justification for Foul Detection and Ground Observation

###### Foul Detection and Ground Observation Code Snippets 

###### Issues with the Foul Detection and Ground Observation

###### Connection With Other Systems and Collaborators

#### Pushing Ball and Aiming
###### Overview of Pushing Ball and Aiming

###### Justification for Pushing Ball and Aiming

###### Pushing Ball and Aiming Code Snippets 

###### Issues with the Pushing Ball and Aiming

###### Connection With Other Systems and Collaborators


 Record multiple development stages
 Include code, photos, or video evidence
 Identify issues and explain fixes
 Justify design decisions

Current idea go through each of my features justify design choices issues ect 
Talk about the collaboration 
How we dicided on the data shaired ect 

## Collaboration

Gone Wrong
	- Task could of been divided better giving the more mathmatically complex task to the poeple nessisary ect
	- People could of started coding earlier (Zen)
	- Some people could of been more independent on the disision making
	- Deadlines could of been followed (monday, then tuesday, then wednesday overshot)
	- More team meetinfs
	- Meets when held could of actualy if people had told or organised their other actives better
	- Explaination of systems connection could of been better]
	- Attackes could of spent more time designe prio to develiopment
	- Start and finish things earlier (to allow for testing time)
	- Could show up to meeting / show up on time
	- Communication between people could of been better
	- When communication / instruction of connecting systems was given that could of been followed
	- Asked for help from Tim sooner / at all
	- Dividing time between features and desiging
	- Didn't test
	- Wasn't time to test
	- Systems not been ready prevented testing
	- Call on day before due date intended to fix all mistakes ect, people (Zen showed up (5:30-45 left at 7:20) and Gabe showed up (7:45) , Dexter Hugo Showed up on time : 4:30 (agreed upon time))
	- Member required explaination on importing from others code

Things that went well 
	- Defence design was completed well before due date and design appears to work
	- Connection between State System, communication and acting on states works well and follows a logical sequence
	- General communication between Hugo and Dexter was good when designing defence / our connected systems
	- First few meets were fine and very informative / productive
	- Most major system were completed early (Exception (zen))
	- Code reviews were informative / benifical, allwowing bugs to be cought and small gaps in logic to be connected. 
	- Hugo and Dexter able to act as leaders / mentors when other on track
	- Github issues / project allowed for planning and assigment of systems
	- File structure is generally good, although with some exceptions
	- Branching / version control allowed for reduction in merge conflicts and symultaneous work 
	- People follow general OOP structure to a good level and produce "Clean Code" although not the maximum of 4 line functions the book calls for
	- People were creative with the problem solving of the robots
	- Complex math was explained to less mathmatically inclined individuals allow for their completion of systems
	- People had choice in the systems they made eg. Gabe volunteered to do movement and was quite infusiastic, Dexter saw the foundational system of the state controller and thus completed it, Hugo applied the testing code well so it could be instantly applied to the final ect
	- Commonly needed variables were easily found and updated for people
	- Programming concepts unknown to some members were explaiend by others 

#### How Work Was Divided

As covered before the robots were split into teams of two, and the individual sections of code were split between individuals.

For the individual sections of code, as to not force one person to do more than their fair share of work we set a rough 400 lines of code limit per person, which seemed to split the systems quite evenly among us, but did require some shifting around of responsibilities, as at that point Gabe had already produced his movement code which was at the 400 line section, and he was planned to complete one or two other sections meaned these had to be re assigned. 

#### Hugo's Contributions

#### Gabe's Contributions 

#### Zen's Contributions 

#### Decision Making Within the Group

#### Production and Design Challenges and their Resolutions 

#### Challenges of a Group Project

 Explain how work was divided
 Describe contributions of each member
 Show how decisions were made
 Explain how challenges were resolved

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
