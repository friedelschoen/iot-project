from random import choice


def generate_token(chars: str, size: int):
	return ''.join(choice(chars) for _ in range(size))
