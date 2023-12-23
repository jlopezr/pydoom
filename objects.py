import pygame

class GameObject:
    def __init__(self, pos, texture):
        self.pos = pos        
        self._texture = texture

    @property
    def texture(self):
        return self._texture


class DynamicObject(GameObject):
    def __init__(self, pos, textures):
        super().__init__(pos, textures[0])
        self._textures = textures
        self._texture_index = 0
        self._next_tick = pygame.time.get_ticks()

    @property
    def texture(self):
        if pygame.time.get_ticks() > self._next_tick:
            self._next_tick = pygame.time.get_ticks() + 100
            self._texture_index= (self._texture_index + 1)%len(self._textures)            
        return self._textures[self._texture_index]