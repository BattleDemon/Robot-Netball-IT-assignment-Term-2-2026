# Robotic Netball

## Preplanning 

#### Game Play Strategy 

The general game play strategy, in which we based our initial development was a loop where: One Robot gets ball --> Other positions themselves --> The First Passes to Second --> Second shoots --> Repeat. 

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

###### Diagrams of Designs

###### Initial Sensors and their Uses

The initial sensors designed for use on our two robots were as follows:

Attacker
    2 Motors - Used for movement and navigation.
    Colour Sensor - Used to observe the ground and check if the robot is in the foul zone and for additional navigattion checks.
    IR Sensor - Used to locate the ball.
    Unfortionatly i the Attacking robot wasn't as preplanned as the defending robot, causing many of its later sensors to not be planned at this point.

Defender
    2 EV3's - One Used as the main controller, communicator, and navigator, and the other purely deticated to the flywheel system.
    2 Motors - Again used for movement and navigation.
    Another 2 Motors - Used for the ball retrieve and passing, as flywheels.
    A single motor - To release the ball from its container.
    2 Colour Sensors - Used to detect if a ball is within the container, one for each EV3.
    Another Colour sensor - Similar to the Attaker, this colour sensor is used for ground detection.
    A Gyro - Used as a secondary navigation checker.
    Lastly an IR Sensor - Also used to locate the ball.


#### Flowcharts of Gameplay

#### Flowchart of Systems

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

###### Ground Detection and Foul Controller Psuedocode 

###### Overview of Aiming and Pushing

###### Aiming and Pushing Psuedocode 
#### Additional Features Incase of Extra Time

Although due to the scale of this assignment and its limitation some of these might not be practical or cause too much extra work. Some additional features which I considered to made, were that of the team system where the robots would stop communication and each be attempting to win, use separate hoops and attempt to block each other.

## Prototyping

#### Designing the Defence Robot

###### Problems During Production

###### Design Notes and Justification

##### Final Design

#### The State Controller

###### Overview of System

###### Justification for System

###### System Code Snippets 

###### Issues with the System

###### Connection With Other Systems

#### Foul Detection and Ground Observation

###### Overview of System

###### Justification for System

###### System Code Snippets 

###### Issues with the System

###### Connection With Other Systems

#### Pushing Ball and Aiming
###### Overview of System

###### Justification for System

###### System Code Snippets 

###### Issues with the System

###### Connection With Other Systems


 Record multiple development stages
 Include code, photos, or video evidence
 Identify issues and explain fixes
 Justify design decisions

Current idea go through each of my features justify design choices issues ect 
Talk about the collaboration 
How we dicided on the data shaired ect 

## Collaboration

#### How Work Was Divided

As covered before the robots were split into teams of two, and the individual sections of code were split between individuals.

For the individual sections of code, as to not force one person to do more than their fair share of work we set a rough 400 lines of code limit per person, which seemed to split the systems quite evenly among us, but did require some shifting around of responsibilities, as at that point Gabe had already produced his movement code which was at the 400 line section. 

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
