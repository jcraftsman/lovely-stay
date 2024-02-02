def update_offers_when_new_offer_published(event: dict, context: dict) -> None:
    offer_published = parse(event)
    offers = OfferRepository.get_instance()
    offers.update(offer_published)


def parse(event: dict) -> 'OfferPublished':
    pass


class OfferPublished:
    pass


class OfferRepository:

    def update(self, offer_published: OfferPublished):
        pass

    @classmethod
    def get_instance(cls) -> 'OfferRepository':
        pass
