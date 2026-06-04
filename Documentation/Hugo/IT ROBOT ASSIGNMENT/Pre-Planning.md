# Strategy for Game-play and Behaviour plans
The strategy for game play is to have the closest robot grab the ball. if it is the attacking robot and they are too far away from the goal then they will pass it to the defending robot which will then wait for them to be closer to the goal and pass the ball back. The defender when it doesn't have the ball will be staying close to it's starting position and the attacking robot when it doesn't have the ball will be moving to the goal they are attacking.
# Sensor selection

2 x Colour sensor For main ev3Hub
	- 1 for ball detection and 1 for ground detection
1 x Colour sensor for secondary ev3Hub for ball detection
1 x Gyro sensor for main hub to double check navigational accuracy
1 x Infrared sensor for ball detection and location on the main hub.


# General design for defence robot

We will have a base for the driving with the hubs on top and in between the hubs and base there will be a cavity to store the ball. There will be wheels out the front throwing and catching the ball.
There will be some way to hold the ball in the middle section and then release it when we want to pass. the IR sensor will be mounted directly under the hubs so that it is high and has a good vantage point. There will be spinning wheels on the front for the catching and throwing mechanism.
![[Diagram of design.jpg|697]]
![[random thoughts.jpg]]

# PseudoCode

## Main Files
```
import all created files

Main defender or attacker class:

	initialise:
		Initialise all variables and create and start all threads
		Specify all sensors and motors
	
	Main loop:
		Loop to ensure program never closes.

```
## Communication
```
Communicator class:
	init:
		set up mailboxes for the robot server for one of them and client for the other
	send state:
		turn a snapshot dictionary of the states into a json string and send it via the bluetooth mailbox
	
	Receive state:
		receive the state json string, turn it back into a dictionary and then update the variables accordingly.
```
## Catch and Throw
```
function "catch and throw"
	Loop and constantly check if there is a ball in the hold
	if there is (colour sensor detects black):
		run the motor forwards
	else there is no ball there:
		run the motor the other way
```
## Actioning States
```
Actioning states class:
	init:
		initialise variables
	
	define functions of what to do when each state happens.
	
	main loop: 
		if statements for when certain states are triggered to run the code for that state.
```

# Division of tasks
To divide the tasks we created GitHub issues for all the needed tasks. We then defined some of them as major tasks and some as minor tasks. There were 4 major tasks so we gave one to each person and then equally divided up the minor tasks until there were no tasks left.

# Notes

# Additional features if we have time