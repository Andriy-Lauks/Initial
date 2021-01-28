import requests
import misc
import json
import parser
from time import sleep


token = misc.token


URL = 'https://api.telegram.org/bot' + token + '/'
currency = ''
currency_list = {
	'доллар': 'usd/',
	'евро': 'eur/',
	'рубль': 'rub',
	'польский злотый': 'pln/',
	'фунт стерлингов': 'gbp/',
	'швейцарский франк': 'chf/'
}

last_update_id = 0


def get_updates():
	url = URL + 'getupdates'
	params = {'timeout': 100, 'offset': None}
	response = requests.get(url, data=params)
	return response.json()


def get_message():
	data = get_updates()
	with open('updates.json', 'w') as file:
		json.dump(data, file, indent=4, ensure_ascii=False)

	last_object = data['result'][-1]
	current_update_id = last_object['update_id']

	global last_update_id
	if last_update_id != current_update_id:
		last_update_id = current_update_id

		try:
			chat_id = last_object['message']['chat']['id']
			message_text = last_object['message']['text']
			message_sender = last_object['message']['from']['first_name']
		except KeyError:
			chat_id = last_object['edited_message']['chat']['id']
			message_text = last_object['edited_message']['text']
			message_sender = last_object['edited_message']['from']['first_name']

		message = {
			'chat_id': chat_id,
			'text': message_text,
			'user': message_sender
		}
		return message
	return None


def set_commands():
	commands = []
	counter = 0

	for item in parser.parser():
		for key, value in item.items():
			if key == 'bank':
				commands.append({'command': f'command{counter + 1}',
								 'description': f'{value}'})
				counter += 1
	result = json.dumps(commands)
	url = f'{URL}setmycommands?commands={result}'
	response = requests.get(url)

	return commands


def gen_reply(text):
	output = [f'Курс в банке']
	for item in parser.parser(currency):
		if item['bank'] == text:
			for value in item.values():
				output.append(value)
	result = ' '.join(output)
	return result


def send_message(chat_id, text='Подождите, секундочку, пожалуйста... .', *args):
	url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
	requests.get(url)


def currency_keyboard(chat_id):
	text = 'выбери валюту:'
	reply_markup = {"keyboard": [["доллар", "евро", "рубль"],
								 ["польский злотый", "фунт стерлингов", "швейцарский франк"]],
					"one_time_keyboard": True}
	data = {
		'chat_id': chat_id,
		'text': text,
		'reply_markup': json.dumps(reply_markup)
	}
	url = "https://api.telegram.org/bot" + token + "/sendMessage"
	r = requests.get(url, data=data)

	return reply_markup


def yes_no_keyboard(chat_id):
	text = 'Сделай выбор:'
	reply_markup = {"keyboard": [["да"], ["нет"]], "one_time_keyboard": True}
	data = {
		'chat_id': chat_id,
		'text': text,
		'reply_markup': json.dumps(reply_markup)
	}
	url = "https://api.telegram.org/bot" + token + "/sendMessage"
	r = requests.get(url, data=data)

	return reply_markup
	# results = r.json()
	# print(results)

# def test_keyboard(chat_id):
# 	text = "Choose:"
# 	reply_markup = {"keyboard": [["Yes", "No"], ["Maybe"], ["1", "2", "3"]],
# 					"one_time_keyboard": True}
# 	data = {'chat_id': chat_id, 'text': text,
# 			'reply_markup': json.dumps(reply_markup)}
# 	url = "https://api.telegram.org/bot" + token + "/sendMessage"
#
# 	r = requests.get(url, data=data)
# 	results = r.json()
# 	print(results)

def main():
	commands = set_commands()

	while True:
		answer = get_message()

		if answer != None:
			chat_id = answer['chat_id']
			text = answer['text']
			user = answer['user']

			if text == 'тест':
				reply = f'Привет {user}, интересует курс валют?'
				yes_no_keyboard(chat_id)

			elif text == 'да':

				reply = f'Выбери интересующую валюту'

			elif text in currency_list:
				global currency
				currency = currency_list[text]
				reply = 'Нажми для выбора банка из списка'

			else:
				try:
					for item in commands:
						for key, value in item.items():
							if value == text.replace('/', ''):
								reply = gen_reply(item['description'])
								raise Exception()
							else:
								reply = 'Не верная команда, пожалуйста, ' \
										'выберите из списка'
				except:
					reply

			send_message(chat_id, reply)

		else:
			continue

		sleep(2)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		exit()
