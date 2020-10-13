class Object:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.type  = 0


class Video(Object):
    VIDEO_TYPE = 1
    path = "video/"
    def __init__(self,name, filename):
        super().__init__(name,filename)
        self.type = 1

class Image(Object):
    IMAGE_TYPE = 2
    path = "image/"
    def __init__(self,name, filename):
        super().__init__(name,filename)
        self.type = 2
