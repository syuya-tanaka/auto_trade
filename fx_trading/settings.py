from envyaml import EnvYAML


env = EnvYAML('config.yml')

ACCOUNT_ID = env['oanda.account_id']
API_PASSWORD = env['oanda.api_password']
ACCESS_TOKEN = env['oanda.access_token']

