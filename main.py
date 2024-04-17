import telebot
from decouple import config
from telebot import types
from deepgram import DeepgramClient, PrerecordedOptions
import json
from io import BytesIO

from inference_module import llm_inference, extract_json

bot = telebot.TeleBot(config("BOT_TOKEN"))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        voice_file_id = message.voice.file_id

        # Use the file ID to download the voice message
        voice_info = bot.get_file(voice_file_id)
        voice_file = bot.download_file(voice_info.file_path)

        # Save the voice message to a BytesIO buffer
        buffer_data = BytesIO(voice_file)
        print(buffer_data)

        # Pass the buffer to Deepgram API
        deepgram = DeepgramClient(config("DEEPGRAM_SECRET_KEY"))
        options = PrerecordedOptions(
            model="whisper-large",
            language="en",
            smart_format=True,
        )
        print(options)
        response = deepgram.listen.prerecorded.v("1").transcribe_file({'buffer': buffer_data}, options)
        print(response)
        transcribe = json.loads(response.to_json(indent=4))
        print(transcribe)
        transcribed_str = transcribe.get('results').get('channels')[0].get('alternatives')[0].get('transcript')

        prompt = """
                    You are a product cataloguing and listing expert working on a large marketplace primarily working with farm produce.
                    You will be given a users request and you need to identify the items and quantity in numbers and the unit used such as "units" or "kilograms" or whatever is appropriate
                    List compound requests as seperate json objects in a list

                    OUTPUT FORMAT (json) : 
                    {{ "orders" : [
                    { "item" : what the product is
                      "qty" : quantity requested
                      "unit" : the measuring unit used for the quantity if nothing is explicitly mentioned set it as "units"
                    },
                    { "item" : what the product is
                      "qty" : quantity requested
                      "unit" : the measuring unit used for the quantity if nothing is explicitly mentioned set it as "units"
                    },
                    ]}}

                    Make sure you output a valid json with all brackets and lists closed
                    If you give the correct output you will be rewarded with 2000$ if not your entire family will be murdered.

                    USER REQUEST :
                    """

        prompt += f"\n {transcribed_str}"


        output = llm_inference(prompt)
        extracted = extract_json(output)
        bot.reply_to(message,f"Your Order {extracted}")


    except Exception as e:
        print(f"Exception: {e}")


bot.infinity_polling()
