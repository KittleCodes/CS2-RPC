'''
A program that uses Counter-Strike 2's Game State Integration to display data from it on Discord.
'''
import time
import json
from flask import Flask, request, send_file
from pypresence import Presence
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID = '1228722706518900736'
START_TIME = time.time()

RPC = Presence(CLIENT_ID)
RPC.connect()
RPC.update(state = "Starting CS2",
                 large_image = "cslogo",
                 start = START_TIME)

app = Flask(__name__)

@app.route('/image')
def image():
    '''
    Returns generated image file created in handle_request()
    '''
    return send_file('rpc_image.png', mimetype = 'image/png')

@app.route('/', methods = ['POST'])
def handle_request():
    '''
    Recieves POST requests from CS2's Game State Integration and updates the Discord Rich Presence.
    '''
    if request.method == 'POST':
        # Parse the JSON payload
        data = request.data.decode('utf-8')
        parsed_data = json.loads(data)

        activity = parsed_data["player"]["activity"]

        # Check if the player is in the menu
        if activity == "menu":
            RPC.update(
            details = "In Menu",
            large_image = "cs2icon",
            start = START_TIME)
            return '', 200

        # Save wanted data from the JSON payload to variables
        mode = parsed_data["map"]["mode"]
        current_map = parsed_data["map"]["name"]
        player_steamid = parsed_data["provider"]["steamid"]
        data_steamid = parsed_data["player"]["steamid"]
        team = parsed_data["player"]["team"]
        ct_score = parsed_data["map"]["team_ct"]["score"]
        t_score = parsed_data["map"]["team_t"]["score"]
        kills = parsed_data["player"]["match_stats"]["kills"]
        assists = parsed_data["player"]["match_stats"]["assists"]
        deaths = parsed_data["player"]["match_stats"]["deaths"]
        mvps = parsed_data["player"]["match_stats"]["mvps"]
        score = parsed_data["player"]["match_stats"]["score"]

        # Check if the data sent is the data of the player who launched the game
        if data_steamid != player_steamid:
            return '', 200

        # Create an image to be used to show data on Discord Rich Presence
        img = Image.new(mode = "RGB", size = (1000,1000), color =  (20,20,20))
        draw = ImageDraw.Draw(img)
        cs_regular = ImageFont.truetype("cs_regular.ttf", 95)
        georgia = ImageFont.truetype("georgia.ttf", 125)

        # Check what team the player is on and display that data
        if team == "T":
            team_name = "Playing as T"
            wins = t_score
            losses = ct_score

            draw.text((260, 50), "Terrorist", (230,230,230), font = cs_regular)
        else:
            team_name = "Playing as CT"
            wins = ct_score
            losses = t_score

            draw.text((35, 50), "Counter-Terrorist", (230,230,230), font = cs_regular)

        # Add rest of stats to the image and save it to be used in image()
        draw.text((370,150), f"{wins}/{losses}", (230,230,230), font = georgia)
        draw.text((255,330), f"Kills: {kills}", (230,230,230), font = georgia)
        draw.text((255,450), f"Deaths: {deaths}", (230,230,230), font = georgia)
        draw.text((255,570), f"Assists: {assists}", (230,230,230), font = georgia)
        draw.text((255,690), f"MVP's: {mvps}", (230,230,230), font = georgia)
        draw.text((255,810), f"Score: {score}", (230,230,230), font = georgia)
        img.save("rpc_image.png", format = 'PNG')

        # Update the RPC
        RPC.update(
            state = f"{wins}W {losses}L | {kills}K/{deaths}D/{assists}A",
            details = f"{mode.title()} | {current_map}",
            # Use the current time in seconds as a parameter so that the image is not cached
            large_image = "http://kittle.ddns.net:3000/image?"+str(time.time()),
            large_text = team_name,
            start = START_TIME)
        return '', 200
    # If the request method is not POST, return 400
    return '', 400
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)
