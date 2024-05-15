# Weather Buddy
<img src="https://github.com/unkindled-one/Weather-Buddy/assets/87220291/823adeaa-a8a1-44af-bbb3-9c3e4dc3823d" width="200">

Weather Buddy is a Discord Bot that provides weather services to its users!
# Preview
![demo](https://github.com/unkindled-one/Weather-Buddy/assets/87220291/186068f5-082f-46e3-860a-33ed6e32154a)
# Features
- Get current weather
- Get weather forecasts
- Get customized clothing and timing recommendations
- Get daily weather messages at a specified time
- Get weather warnings in your zipcode when they occur
- Get today's rain/snow 
- And much more!
# Installation
1. Copy the source code using
```
git clone https://github.com/unkindled-one/Weather-Buddy.git
```
2. Navigate into the directory
3. Install Dependencies using
```
pip install -r requirements.txt
```
4. Acquire a [Discord API token](https://discord.com/developers/applications) and put the following into a .env file
```
TOKEN=<your token>
```
5. If you don't have a database, run the following command to create one
```
cd src
python database.py
```
6. Add the bot to your server
7. Run the following command to start the bot
```
python bot.py
```
