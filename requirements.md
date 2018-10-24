Functional:

Intent of the project is to track the work efficiency and provide insights to improve\change habits and be a more productive worker.
The above objective can be achieved by building the following modules. 
    a) Track
        a. Standard and Overtime hours - log files & Ux display
        b. Productive\non-productive sub hours - log files (later??)
    b) Analyze
        a. Offline (scripts)
        b. Realtime (Display Ux)
    c) Act
        a. Human part (Hoping the insights will help make the change)

Technical:
    Functional objectives can be realized with the following technical modules adding some fun
    a) Hardware - 
        a. Rpi 
            i. Make it work
        b. LED matrix
            i. Make it work
            ii. Make a stand so it doesn’t fall
    b) Software
        a. Logger
            i. Some Python logger
        b. Controller
            i. TCP commands over local network
                1) Start day - First in morning
                2) Pause day - Lunch break
                3) End day - After OT. Concludes the day
                4) Reset day - Emergency reset option if something is wrong
                5) Configuration
                    a) Standard work hour duration (8hr)
            ii. Modules
                1) CountdownTimer
                2) SimpleTimeTracker(or CountupTimer (unbounded) - for afterwork)
                3) Display module
                4) Program with Apis
                5) Network Service in systemd
                
        c. Display
            i. Countdown timer for tracking standard work hours and showing real-time feedback progress
            ii. Countup timer for tracking overtime work hours and showing real-time feedback and progress
