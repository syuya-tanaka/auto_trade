"""FX trading."""
import os

from envyaml import EnvYAML


env = EnvYAML('config.yml')
print(env['oanda.account_id'])
print(env['oanda.api_password'])
