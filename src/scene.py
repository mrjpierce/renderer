class Scene:
    """
    Simple scene manager for 3D objects to be rendered.
    Keeps track of models and their transforms.
    """
    def __init__(self):
        # Dictionary: model name -> {'model': Model, 'position': ..., 'rotation': ..., 'scale': ...}
        self.objects = {}

    def add_object(self, name, model, position=None, rotation=None, scale=None):
        self.objects[name] = {
            'model': model,
            'position': position,
            'rotation': rotation,
            'scale': scale
        }

    def remove_object(self, name):
        if name in self.objects:
            del self.objects[name]

    def get_objects(self):
        return self.objects.items()
