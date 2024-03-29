[//]: # "Image References"

[image1]: https://user-images.githubusercontent.com/10624937/42135619-d90f2f28-7d12-11e8-8823-82b970a54d7e.gif "Trained Agent"

# Project 1: Navigation

### Introduction

For this project, you will train an agent to navigate (and collect bananas!) in a large, square world.  

![Trained Agent][image1]

A reward of +1 is provided for collecting a yellow banana, and a reward of -1 is provided for collecting a blue banana.  Thus, the goal of your agent is to collect as many yellow bananas as possible while avoiding blue bananas.  

The state space has 37 dimensions and contains the agent's velocity, along with ray-based perception of objects around agent's forward direction.  Given this information, the agent has to learn how to best select actions.  Four discrete actions are available, corresponding to:
- **`0`** - move forward.
- **`1`** - move backward.
- **`2`** - turn left.
- **`3`** - turn right.

The task is episodic, and in order to solve the environment, your agent must get an average score of +13 over 100 consecutive episodes.

### Getting Started

1. Download the environment from one of the links below.  You need only select the environment that matches your operating system:
    - Linux: [click here](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Linux.zip)
    - Mac OSX: [click here](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana.app.zip)
    - Windows (32-bit): [click here](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Windows_x86.zip)
    - Windows (64-bit): [click here](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Windows_x86_64.zip)
    
    (_For Windows users_) Check out [this link](https://support.microsoft.com/en-us/help/827218/how-to-determine-whether-a-computer-is-running-a-32-bit-version-or-64) if you need help with determining if your computer is running a 32-bit version or 64-bit version of the Windows operating system.

2.  Place the file in the PROJECT GitHub repository, in the `rainbow_navigation_project/` folder, and unzip (or decompress) the file. 

3.  install environment 

    1. pip install matplotlib
    2. pip install mlagents
    3. pip install numpy
    4. That should be it.

### Instructions

Follow the instructions in `rainbow.ipynb` either train or test the solution!
It is also written as python classes if that suits you better, but I will only go into details with the `rainbow.ipynb`.

### Results
While the results are not optimal, it will solve the problem in around 300 episodes.
I have created a better solution for the project that will solve it in less than 160 episodes, but it is not a rainbow implementation.
The hyper-parameters for this project needs to be tuned further to improve the max average result over 100 episodes.
As the hyper-parameters are set now, it will evens out around an average of 13. 

I will recomment reading the report.pdf for better understanding of the rainbow implementation and look through the comments in the code. It should be fairly well commented.

### Notes.

Through this implementation I have seeked guidance through others implementation of the different techniques used [rainbow is all you need]( https://github.com/Curt-Park/rainbow-is-all-you-need ), and create my own implementation specific to solve the navigation project.
To learn the affect of each implementation I found the [README](https://github.com/KaplanAlex/rl-sonic/blob/master/README.md ) from KaplanAlex where good and I learned a lot from his small summary.

I have commented the code well to show understanding of the subject as well as notes to future me.

