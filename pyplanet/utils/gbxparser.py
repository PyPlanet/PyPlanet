import asyncio
import io
import struct

import os
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
			value = self.read_string()
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

	async def seek(self, offset, whence=io.SEEK_SET):
		return self.buffer.seek(offset, whence)

	async def tell(self):
		return self.buffer.tell()


class GbxParser:

	def __init__(self, file=None, buffer=None):
		"""
		Initiate a parser with either a file path or buffer.
		:param file: File path.
		:param buffer: Buffer
		:type file: str
		"""
		super().__init__()
		if buffer and not isinstance(buffer, io.BufferedIOBase):
			raise Exception('Buffer given should be a io.BufferedIOBase extended type.')
		if file and not isinstance(file, str):
			raise Exception('File should be a string, pointing to the file you want to load.')
		self.file = file
		self.buffer = _AsyncBufferProxy(buffer)
		self.strings = _LookBackUtils(self.buffer)

		self.result = None

		self.header = None
		self.header_length = 0
		self.header_chunk_count = 0
		self.header_chunks = dict()

	async def parse(self):
		if self.file:
			async with aiofiles.open(self.file, mode='rb') as self.buffer:
				return await self.__parse()
		elif self.buffer:
			return await self.__parse()
		raise Exception('No buffer or file given at init.')

	async def __parse(self):
		# Skip until class reference.
		await self.buffer.seek(9)
		# Read class ID.
		class_id, = struct.unpack('<I', await self.buffer.read(4))
		if class_id != ((0x3 << 24) | (0x43 << 12)):
			raise GbxException('Gbx file has no valid parser, only maps are supported right now.')

		header = await self.__parse_header()
		return None

	async def __parse_header(self):
		self.header_length, = struct.unpack('<I', await self.buffer.read(4))
		self.header_chunk_count, = struct.unpack('<I', await self.buffer.read(4))

		self.header_chunks = dict()
		self.header = []

		# Save header data from binary.
		for nr in range(self.header_chunk_count):
			chunk_id, = struct.unpack('<I', await self.buffer.read(4))
			chunk_size, = struct.unpack('<I', await self.buffer.read(4))
			self.header_chunks[chunk_id] = chunk_size & ~0x80000000

		# Parse all header chunks.
		for chunk_id, chunk_size in self.header_chunks.items():
			self.strings.reset()
			await self.__parse_chunk(chunk_id, chunk_size)

	async def __parse_chunk(self, chunk_id, chunk_size):
		if chunk_id == 0x03043002:
			version, = struct.unpack('<H', await self.buffer.read(2))
			await self.buffer.seek(4)

			time_bronze, time_silver, time_gold, time_author = struct.unpack('<LLLL', await self.buffer.read(16))
			price, is_multilap, map_type = struct.unpack('<LLL', await self.buffer.read(12))
			is_multilap = True if is_multilap == 1 else False

			await self.buffer.seek(4)

			author_score, editor = struct.unpack('<LL', await self.buffer.read(8))
			editor = 'simple' if editor == 1 else 'advanced'

			await self.buffer.seek(4)

			checkpoints, laps = struct.unpack('<LL', await self.buffer.read(8))
			print(checkpoints, laps)

			pass
		return


if __name__ == '__main__':
	filename = os.path.join(
		os.path.dirname(os.path.dirname(os.path.abspath(os.curdir))),
		'tests',
		'_files',
		'maps',
		'canyon-mp4-1.gbx'
	)

	loop = asyncio.get_event_loop()
	parser = GbxParser(file=filename)
	result = loop.run_until_complete(parser.parse())

	# Buffered
	parser = GbxParser(buffer=open(filename, mode='rb'))
	result = loop.run_until_complete(parser.parse())

