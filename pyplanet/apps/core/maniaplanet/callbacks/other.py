from pyplanet.core.events import Callback, handle_generic

async def handle_bill_updated(source, signal, **kwargs):
	bill_id, state, state_name, transaction_id = source
	return dict(
		bill_id=bill_id, state=state, state_name=state_name, transaction_id=transaction_id
	)

# TODO: Create contrib for bill management.
bill_updated = Callback(
	call='ManiaPlanet.BillUpdated',
	namespace='maniaplanet',
	code='bill_updated',
	target=handle_bill_updated
)

vote_updated = Callback(
	call='ManiaPlanet.VoteUpdated',
	namespace='maniaplanet',
	code='vote_updated',
	target=handle_generic # TODO.
)
