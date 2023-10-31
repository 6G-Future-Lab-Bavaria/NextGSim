from edge.entities.Entity import Entity


class Gateway(Entity):
    def __init__(self, entity_id=None, model="gateway", location=None):
        super().__init__(entity_id=entity_id, model=model, location=location)
