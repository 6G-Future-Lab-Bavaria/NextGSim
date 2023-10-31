from edge.entities.Entity import Entity


class Actuator(Entity):
    def __init__(self, entity_id=None, model="actuator", location=None, user_id=None):
        super().__init__(entity_id=entity_id, model=model, location=location)
        self.user_id = user_id



