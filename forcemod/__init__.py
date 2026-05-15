import aiohttp
import logging
import asyncio
from urllib.parse import quote
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet import __version__ as pyplanet_version

logger = logging.getLogger(__name__)

class ForceModApp(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.mod_url = "http://www.maniapark.com/download/mods/TMT_stadium.zip"
		self.setting_mod_url = Setting(
			'mod_url', 'Mod Url', Setting.CAT_KEYS, type=str,
			description='The mod link to be forced (Skip the map to apply the mod change).',
		)

	async def on_start(self):
		logger.info('ForceMod: on_start begin')
		await self.context.setting.register(self.setting_mod_url)
		logger.info('ForceMod: setting registered, reloading...')
		await self.reload_setting()
		logger.info('ForceMod: on_start complete')

	async def podium_start(self, *args, **kwargs):
		await self.reload_setting()

	async def reload_setting(self, *args, **kwargs):
		try:
			url = await self.setting_mod_url.get_value()
			logger.info('ForceMod: raw setting value: %r', url)

			if not url:
				await self.instance.chat('$f00$iForceMod App : Invalid Mod URL, none given! Forced Mod Unset.')
				await self.instance.gbx.execute("SetForcedMods", False, [])
				return

			# Encode spaces and other unsafe chars, keep URL structure intact
			url = quote(url, safe=':/?=&@#')
			logger.info('ForceMod: encoded URL: %s', url)

			async with aiohttp.ClientSession(
				headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}
			) as session:
				async with session.head(url) as resp:
					logger.info('ForceMod: HEAD %s -> status %s', url, resp.status)
					if resp.status >= 400:
						await self.instance.chat(
							'$f00$iForceMod App : Mod URL returned HTTP {}! Forced Mod Unset.'.format(resp.status)
						)
						await self.instance.gbx.execute("SetForcedMods", False, [])
						return

			self.mod_url = url
			await self.instance.gbx.execute("SetForcedMods", True, [
				{"Env": "Stadium", "Url": self.mod_url}
			])
			logger.info('ForceMod: Mod set to %s', url)

		except Exception as e:
			logger.exception('ForceMod: reload_setting failed')
			await self.instance.chat('$f00$iForceMod App : Invalid Mod URL ! Forced Mod Unset.')
			await self.instance.gbx.execute("SetForcedMods", False, [])
