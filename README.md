# Handy

## Meet Handy
Handy is a set of robotic hands that can converse in sign language. He can perform two primary actions:
* **Act as a translator:** Handy can take speech as input, translate it into sign language, and display the sign language with a set of robotic hands.
* **Have a conversation in sign langage:** Handy can respond in a friendly, human-like way to speech, by displaying a conversational reply in the form of sign language. This can be incredibly useful for those, inclduing the deaf and mute, who want to learn sign language  in a fun interactive way.

**Inspiration**
We always found that the traditional robotic limbs, while they are exceptionally good at what they set out to be, do not mimic human hands naturally.
We felt that robots can gain an enormous amount of human like properties by being able to mimic our hand gestures and the perfect place to start is sign language.
Not only does our project work as a proof of concept for human like robotic limbs it also gives deaf people a lot of versatility, specifically for educational purposes.

**What it does**
We have created two human like hands that are articulated in exactly the same way as normal human hands from the elbow down. This gives our robot incredible versatility allowing it to do anything from communicating in sign language to playing rock-paper-scissor shoot
It is capable of translating English speech into ASL signs using the Google Cloud speech to text API
It is also capable of conversing with the user (chatBOTTT); taking input in speech and answering with ASL (ALMOST THERE BUT NOT YET)

**How we built it**
We arrived on site with pre-printed 3D components and set to work building the hands (20 servos in total).
At the same time our team started to develop an abstraction for a ASL database that provides heuristic features about each sign. We ran our code on the 800 most frequently used words to extract about 10 unique identifiers for each sign. We then converted this virtual 3D movement into a custom designed machine code which would generate the desired motions in real time.
Then a custom protocol was created to allow the python code running on a mac to be transmitted, via serial port, to the Arduino which sends out i2c data to two 16 channel PWMmodules that control the servos.

**Challenges we ran into**
Our initial idea to have a camera recognize sign language and our robot respond to it ended up being impossible for us to achieve in the short time frame. With many signs being very simmilar and the databases very restrictive, it was hoples.
While we were working on the abstraction for the 3D movements coming from the ASL database we realized that the databases available are not nearly as refined as we thought. This meant that we lost detail on some wrist motions and we had to generallize the bigger movments (i.e. major location of the move).
We also faced the difficult challenge of creating our own machine code, that unlike most, used a interdependent polar system, with one servo rotating the next, rotating the next.... Considerable math work had to be done to approximate all possible R^3 positions onto what was essentially the curves of two circles (a sphere that rotates in time).
Finally the hardware ended up being a weak link and with no possibility of buying replacement parts we had to think on the fly to keep the hands in working order.

**Accomplishments that we're proud of**
Sure there are a few bugs here and there but it works and its amazing. The level of difficulty for this project was through the roof and with things coming of to a slow start we were not expecting much. But things went somewhat smoothly and everything worked out in the end.
With 3 members of our team being first time hackers and one member being bogged down over the digital recognition stuff that didn't work out for most of the time; we are extremely proud of our achievement.
All things considered, the fact that we have a working prototype (really!!!) is awesome.

**What we learned**
No task is too big when you have an endless supply of candy and energy drinks
With only one member of our team being used to hardware, it was a big learning experience to play with the Arduino and even creating our own machine code and transmission protocol.
The whole abstraction of an entire database was also new to us and it ended up being an interesting aspect.

**What's next for Handy**
Definitely a V2 of the hardware... Also find a better more detailed database to have more unique detailed signs
Also, (though it is definitely a really tough) a way for the computer to take input from a sign language user and be able to understand the signs through computer vision.
