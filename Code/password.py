import string, random 
from random import sample
myrg = random.SystemRandom()
length = 20

l = string.lowercase
u = string.uppercase
d = string.digits
s = string.punctuation
total = l + u + d + s
new = ''

password = myrg.choice(l) + myrg.choice(u) + myrg.choice(d) + myrg.choice(s)

for _ in range(length - len(password)):
	password += myrg.choice(total)

password_list = random.sample(password, 20)
password_shuffle = ''.join(password_list)


def rg():
  	from random import sample
	symbol = string.punctuation
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	numeric = string.digits
	seed = sample(lower, 1) + sample(upper, 1) + sample(numeric, 1) + sample(symbol, 1) +\
	sample(lower + upper + numeric + symbol, 16)
	return ''.join(sample(seed, 20))
