from pyplanet.core.events import Callback, handle_generic

# TODO: Create contrib for bill management.
bill_updated = Callback(
	call='ManiaPlanet.BillUpdated',
	namespace='maniaplanet',
	code='bill_updated',
	target=handle_generic
)

vote_updated = Callback(
	call='ManiaPlanet.VoteUpdated',
	namespace='maniaplanet',
	code='vote_updated',
	target=handle_generic # TODO.
)
