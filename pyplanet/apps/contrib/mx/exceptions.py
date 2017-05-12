class ManiaExchangeException(Exception):
	pass


class MXInvalidResponse(ManiaExchangeException):
	pass


class MXMapNotFound(ManiaExchangeException):
	pass
