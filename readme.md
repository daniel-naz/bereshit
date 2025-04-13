## Bereshit Simulation

The project simulates a possible landing of the Israli probe - bereshit that crashed on the moon in 2019.

Source video : [Bereshit landing control room](https://www.youtube.com/watch?v=HMdUcchBYRA&t=1612s).

Source article : [Bereshit crash investigation](https://www.ynet.co.il/articles/0,7340,L-5681547,00.html).

### Part 1 - Crash reasons
___
There was a series of failiures that caused the crash. It started on the night of the launch - the set of cameras that 
were used to track the probes location in space malfunctioned which caused the scientists to improvise and eventually reach the moon after a lot of work.

After a couple of days in space, the probe had an unprompt reboot - the same issue recurred multiple times during the rest of the flight.

While landing - one of the two components responsible for calculating the probes speed stopped working. The probe able to work well until it
rebooted itself after not getting any speed messurements for 0.5 seconds. 

The reboot caused the main engine to stop working and the scientists couldn't fix the error in time.

The main issue in my opinion was keeping all the instuctions on RAM memory while also making the probe reboot itself after each minor error.


### Part 2 - Simulation 
___
1 - I've set the start velocity based on the video above (Horizontal = 1700 mps, Vertical = 47 mps)

2 - I used the physics in the example [project](https://drive.google.com/file/d/1KAnYc7W2aVcX9aZFkI-PQbzQgdgBw4-A/view?usp=sharing) after converting it to python.

#### PID
- Speed : Each tick the probe knows what its expected speed is, the expected horizontal speed is always 0 and the vertical is based on the height. The program calculated the thrust power based on the physics in the simulation by calculating how much thrust is required to slow down and which is the most important axis to do so in.    

- Rotation : Each tick the program checks all the possible integer rotations and finds the one with the most minor error, the error is calculated based on the expected speed and the speed after slowing down at the set rotation. When the horizontal speed is 0 the rotation is set to 0 and each time the max rotation is capped by the horizontal speed to avoid focusing too much on slowing down the horizontal speed.

3 - When running the program the simulator will automatically land with horizontal and vertical speeds of less than 2.5.

### Summary
___
As stated in "Part 1" - the probe crashed mostly because of attempts to reduce its cost. 

In my simulation I wanted to take into account how much speed the probe should have in each stage of the landing and what is the most optimal rotation. Without access to
the programming of bereshit - my simulator is based mostly on my personal logic.

The end fuel value is 15, I've added a slider that allows to tweak the start values. I'm sure someone can find better landing data.

Excel data located in the repository.