import io
import struct
from asyncio import iscoroutinefunction

import aiofiles


class GbxException(BaseException):
	"""
	Exception with parsing the Gbx file.
	"""
	pass


class _LookBackUtils:
	PREDEFINED_STRINGS = {
		11: 'Valley',
		12: 'Canyon',
		13: 'Lagoon',
		17: 'TMCommon',
		202: 'Storm',
		299: 'SMCommon',
		10003: 'Common',
	}

	def __init__(self, buffer):
		self.buffer = buffer
		self.store = list()
		self.version = None

	async def read_string(self):
		length, = struct.unpack('<L', await self.buffer.read(4))
		return struct.unpack('<{}s'.format(length), await self.buffer.read(length))[0].decode()

	async def read_lookback_string(self):
		if self.version is None:
			# We should see the lookback version right now.
			self.version, = struct.unpack('<L', await self.buffer.read(4))
		# Get the index.
		idx, = struct.unpack('<L', await self.buffer.read(4))
		if idx == 0:
			return None

		# Check if this will be the first occurrence.
		if idx & 0xc0000000 != 0 and idx & 0x3fffffff == 0:
			value = await self.read_string()
			self.store.append(value)
			return value

		# Check if idx is telling us that it's empty.
		if idx == 0xffffffff:
			return ''

		# Check if it's a predefined value.
		if idx & 0x3fffffff == idx:
			return self.PREDEFINED_STRINGS[idx]

		# Get from local store.
		idx &= 0x3fffffff
		if idx - 1 >= len(self.store):
			raise GbxException('String not found in lookback list!. Offset: {}'.format(await self.buffer.tell))
		return self.store[idx - 1]

	def reset(self):
		if self.version:
			self.store = list()
			self.version = None


class _AsyncBufferProxy:
	def __init__(self, buffer):
		"""
		:param buffer: Buffer
		:type buffer: io.BufferedIOBase
		"""
		self.buffer = buffer

	async def read(self, size=1):
		return self.buffer.read(size)

	async def seek(self, offset, whence=io.SEEK_CUR):
		return self.buffer.seek(offset, whence)

	async def tell(self):
		return self.buffer.tell()


class GbxParser:
	"""
	Async GBX Map Information Parser.
	
	Author: Toffe.
	"""

	def __init__(self, file=None, buffer=None):
		"""
		Initiate a parser with either a file path or buffer.

		:param file: File path.
		:param buffer: Buffer
		:type file: str
		"""
		super().__init__()
		if file and not isinstance(file, str):
			raise Exception('File should be a string, pointing to the file you want to load.')
		if not file and not buffer:
			raise Exception('File or buffer is required!')
		self.file = file

		if buffer:
			if iscoroutinefunction(buffer.read):
				self.buffer = buffer
			else:
				self.buffer = _AsyncBufferProxy(buffer)
		else:
			self.buffer = _AsyncBufferProxy(buffer)
		self.strings = _LookBackUtils(self.buffer)

		self.result = dict()

		self.header = None
		self.header_xml = None
		self.header_length = 0
		self.header_chunk_count = 0
		self.header_chunks = dict()

		self.parse_thumb = False
		self.parse_header_xml = False

	async def seek(self, offset):
		"""
		We need to override the second param to move from the current position.

		:param offset: offset to move away.
		:type offset: int
		"""
		return await self.buffer.seek(offset, io.SEEK_CUR)

	async def parse(self, thumb=False, header_xml=False):
		self.parse_thumb = thumb
		self.parse_header_xml = header_xml

		if self.file:
			async with aiofiles.open(self.file, mode='rb') as self.buffer:
				self.strings = _LookBackUtils(self.buffer)
				return await self.__parse()
		elif self.buffer:
			return await self.__parse()
		raise Exception('No buffer or file given at init.')

	async def __parse(self):
		# Skip until class reference.
		await self.seek(9)
		# Read class ID.
		class_id, = struct.unpack('<I', await self.buffer.read(4))
		if class_id != ((0x3 << 24) | (0x43 << 12)):
			raise GbxException('Gbx file has no valid parser, only maps are supported right now.')

		self.result.update(await self.__parse_header())

		return self.result

	async def __parse_header(self):
		self.header_length, = struct.unpack('<I', await self.buffer.read(4))
		self.header_chunk_count, = struct.unpack('<I', await self.buffer.read(4))

		self.header_chunks = dict()
		self.header = dict()

		# Save header data from binary.
		for nr in range(self.header_chunk_count):
			chunk_id, = struct.unpack('<I', await self.buffer.read(4))
			chunk_size, = struct.unpack('<I', await self.buffer.read(4))
			self.header_chunks[chunk_id] = chunk_size & ~0x80000000

		# Parse all header chunks.
		for chunk_id, chunk_size in self.header_chunks.items():
			self.strings.reset()
			self.header.update(await self.__parse_chunk(chunk_id, chunk_size))

		return self.header

	async def __parse_chunk(self, chunk_id, chunk_size):
		if chunk_id == 0x03043002:
			version, = struct.unpack('<B', await self.buffer.read(1))
			await self.seek(4)
			time_bronze, time_silver, time_gold, time_author = struct.unpack('<LLLL', await self.buffer.read(16))
			price, is_multilap, map_type = struct.unpack('<LLL', await self.buffer.read(12))
			is_multilap = True if is_multilap == 1 else False
			await self.seek(4)
			author_score, editor = struct.unpack('<LL', await self.buffer.read(8))
			editor = 'simple' if editor == 1 else 'advanced'
			await self.seek(4)
			checkpoints, laps = struct.unpack('<LL', await self.buffer.read(8))
			return dict(
				time_bronze=time_bronze, time_silver=time_silver, time_gold=time_gold, time_author=time_author,
				price=price, is_multilap=is_multilap, map_type=map_type, author_score=author_score, editor=editor,
				checkpoints=checkpoints, laps=laps
			)

		elif chunk_id == 0x03043003:
			version, = struct.unpack('<B', await self.buffer.read(1))
			uid = await self.strings.read_lookback_string()
			environment = await self.strings.read_lookback_string()
			author_login = await self.strings.read_lookback_string()
			name = await self.strings.read_string()
			await self.seek(5)
			await self.strings.read_string() # Unknown, mostly empty.
			mood = await self.strings.read_lookback_string()
			decoration_env_id = await self.strings.read_lookback_string()
			decoration_env_author = await self.strings.read_lookback_string()
			await self.seek(4*4+16)
			map_type = await self.strings.read_string()
			map_style = await self.strings.read_string()
			await self.seek(9)
			title_id = await self.strings.read_lookback_string()
			return dict(
				uid=uid, environment=environment, author_login=author_login, name=name, mood=mood,
				decoration_env_id=decoration_env_id, decoration_env_author=decoration_env_author,
				map_type=map_type, map_style=map_style, title_id=title_id
			)

		elif chunk_id == 0x03043004:
			version, = struct.unpack('<B', await self.buffer.read(1))
			await self.seek(chunk_size - 1)

		elif chunk_id == 0x03043005:
			self.header_xml = await self.strings.read_string()

		elif chunk_id == 0x03043007:
			has_thumb = bool(struct.unpack('<L', await self.buffer.read(4))[0])
			comment = None
			thumb = None
			if has_thumb:
				thumb_size, = struct.unpack('<L', await self.buffer.read(4))
				await self.seek(15) # Skip XML thumb tag.
				if self.parse_thumb:
					thumb = struct.unpack('<{}s'.format(thumb_size), await self.buffer.read(thumb_size))[0].decode()
				else:
					await self.seek(thumb_size)
				await self.seek(16 + 10) # </Thumbnail.jpg></Comments>

				comment_size, = struct.unpack('<L', await self.buffer.read(4))
				if comment_size > 0:
					comment = struct.unpack('<{}s'.format(comment_size), await self.buffer.read(comment_size))[0].decode()
				await self.seek(11) # </Comments>
			else:
				await self.seek(chunk_size - 4)

			return dict(has_thumb=has_thumb, thumb=thumb, comment=comment)

		elif chunk_id == 0x03043008:
			version, = struct.unpack('<L', await self.buffer.read(4))
			author_version, = struct.unpack('<L', await self.buffer.read(4))
			author_login = await self.strings.read_string()
			author_nickname = await self.strings.read_string()
			author_zone = await self.strings.read_string()
			author_extra = await self.strings.read_string()
			return dict(
				author_version=author_version, author_login=author_login, author_nickname=author_nickname,
				author_zone=author_zone, author_extra=author_extra
			)
		return dict()
