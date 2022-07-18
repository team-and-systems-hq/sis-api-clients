# A collection of Python clients for interfacing with major Australian school management systems

Here you'll find a bunch of classes which will get you started with authentication and basic 
record fetching from major school management systems.

Below is the list of URLs where you can find the API documentation for Aussie school management systems. 

* TASS - https://github.com/TheAlphaSchoolSystemPTYLTD
* Edumate -  https://integrations.edumate.net/apidoc/
* Synergetic - https://developer.synergetic.net.au/api.html
* Sentral - http://development.sentral.com.au/
* Engage - More info coming
* PCSchool - More info coming
* Civica, SchoolPro, SchoolEdge SAS2000, Denbeigh, Compass, Maze - No API or not public

Please note that this code has been extrapolated from the various projects I've been working on 
over the past decade, which is a basic skeleton code to get you started. 

You'll notice that most classes in here to do not catch exceptions when there is some kind of auth 
failure or when the API times out or can't be contacted. 
You'll have to put those in yourself and hook them into your logger. You just basically 
wrap the request calls into try and except and then catch those errors and log them.  
I have purposely taken this code out to keep it simple to use and understand. Also I have  
removed my logging method since everyone uses something different for that.

If you need help with understanding how this works or if you need help with any of the code, 
feel free to email me at mario@enrolhq.com.au.

LICENCE: MIT  - Basically, I don't care how you use this. If you're
using it at your school or making money of it. You can copy it and change it as much as you wish. 
But if you find it useful and see me at the pub you should buy a round.

I'm planning to add more school management systems to this project as I find time. Feel free to 
submit pull requests with changes and additions.

I'm also planning to add a sample Django CRM project here which can be used by schools for different 
purposes and some instructions on how to run it in production. 

