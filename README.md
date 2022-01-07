# Instructions

This is a rough Alexa skill to integrate Alexa with YouTube on the 
Chromecast.
An Alexa user can speak a phrase such as:
`open YouTube and (find|search for) cat videos` 
and the system will cast the first matching video on YouTube to the Chromecast.

The interactions are initiated by the Alexa online service, and 
the sequence is as follows:

Alexa Cloud -> (nginx TLS proxy -> (this app)) -> Chromecast

The nginx TLS proxy config can be found in etc and copied to the host.
The TLS key and certificate must be /etc/ssl/alexa/.

## HTTPS configuration

The Alexa Cloud communicates to this program using HTTPS 
and therefore you need a private key and certificate.
Self-signed certificates can be loaded into the Alexa Developer Console.
You also need to port forward 443 if you are behind a NAT. Sadly, 
Amazon Alexa Cloud does not support any other port number. 

The certificate MUST have the Subject Alternate Name field specified.
This essentially is the public domain name of your host.
The simple OpenSSL commands can't do that for you easily but there is a 
nice script [here](https://gist.github.com/erik/119dd32efc269d6dd5d7) that can.

Run this script and follow the instructions.

You need to create a basic skill in the
[Alexa Developer Console](https://developer.amazon.com/alexa/console/ask/).
Give it whatever name you want.
Ensure that the file models/intents.json is also uploaded into the developer console.
Make sure that the REST endpoint and certificate are specified in the developer console.

## Technical details and TODO list

This is a very rough proof-of-concept and is not intended 
as a long term solution:

* This does not yet verify the digital signature of Alexa requests but
it absolutely should.

* This does not use the YouTube API. The latest version of that API 
requires registering for a key, which I'm not keen on signing up to.
Nevertheless, that is what a good solution should use.

* The Chromecast has some kind of REST interface. The custom protocol 
for the interface is called DIAL. Apparently, this is a deprecated interface
and may disappear at any notice.

* This uses the AMAZON.SearchQuery intent to capture the keywords for YouTube.
It's a bit restrictive because it cannot override the in-built video skill functionality
within Alexa. I'm not sure which skill is the best choice for this little
project.

* The default port is 3000. You can change this to another port
by editing the nginx config above and the python script. This should be 
added as a parameter to the script.

* This can be deployed using Amazon's CLI tool if it has the right dotfiles.
The appropriate config files should be investigated.

* This is self-hosted because the Chromecast can only be operated from 
within a LAN. On the other hand, Alexa can only communicate directly with
Alexa-enabled devices, of which the Chromecast certainly is not. Therefore, this
self-hosted "glue" is required and you can't simply use an Amazon Lambda routine.
The hosting could be simplified with a runc or Docker container, however certificates are still 
a manual process (an opportunity to use Let's Encrypt?).
