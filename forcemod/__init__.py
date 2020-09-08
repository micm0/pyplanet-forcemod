import aiohttp
import logging
import asyncio
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet import __version__ as pyplanet_version

class ForceModApp(AppConfig):
	"""
	Force Mod plugin
	"""
	game_dependencies = ['trackmania','trackmania_next']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']


	def __init__(self, *args, **kwargs):
		"""
		Initializes the plugin.
		"""
		super().__init__(*args, **kwargs)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.mod_url = "http://www.maniapark.com/download/mods/TMT_stadium.zip"

		self.setting_mod_url = Setting(
			'mod_url', 'Mod Url', Setting.CAT_KEYS, type=str,
			description='The mod link to be forced (Skip the map to apply the mod change).',
		)
		
	async def on_start(self):

		# Register settings.
		await self.context.setting.register(
			self.setting_mod_url,
		)

		# Force reload the setting.
		await self.reload_setting()

		

	async def podium_start(self, *args, **kwargs):
		# Force reload of setting.
		await self.reload_setting()

			
	async def reload_setting(self, *args, **kwargs):
		# Verify force mod setting and get/set mod url.
			url = await self.setting_mod_url.get_value()
			if not url:
				await self.instance.chat('$f00$iForceMod App : Invalid Mod URL, none given! Forced Mod Unset.')
				await self.instance.gbx.execute("SetForcedMods", False, [])
			else:
				with aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}) as session:
					try:
						async with session.get(url) as _:
							self.mod_url = url
							await self.instance.gbx.execute("SetForcedMods", True, [
								{
									"Env": "Stadium",
									"Url": self.mod_url
								}
							])
							logging.info('ForceMod App : Next Mod Url : ' + url)
					except Exception as e:
						await self.instance.chat('$f00$iForceMod App : Invalid Mod URL ! Forced Mod Unset.')
						logging.error('Error with checking Mod URL :')
						logging.error(e)
						await self.instance.gbx.execute("SetForcedMods", False, [])
						
				