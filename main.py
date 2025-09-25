from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import NumericProperty, StringProperty
import random

class SkyObject:
    def __init__(self, obj_type, color, number):
        self.obj_type = obj_type
        self.color = color
        self.number = number
        self.x = random.uniform(-1, 1)
        self.y = random.uniform(-0.75, 0.75)
        self.altitude = random.uniform(0.5, 1)  # 0-1 scale
        self.speed = random.uniform(0.001, 0.005)
        self.direction = random.choice([-1, 1])
        self.trail = []
        self.behavior = self.assign_behavior()

    def assign_behavior(self):
        behaviors = ['normal'] * 35 + ['hover_zip'] * 25 + ['rare'] * 10 + ['orbit'] * 15 + ['shooting'] * 15
        return random.choice(behaviors)

    def update(self, dt, sim_speed, view_mode, direction):
        if view_mode == 'plan':
            # Top-down movement
            self.x += self.speed * self.direction * dt * sim_speed
            if abs(self.x) > 1:
                self.x = -self.x  # Wrap around
        else:
            # Ground view: perspective
            self.y += self.speed * dt * sim_speed if self.behavior == 'shooting' else 0
            self.altitude -= 0.0001 * dt * sim_speed  # Descend slowly

        # Trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        # Behaviors
        if self.behavior == 'hover_zip':
            if random.random() < 0.01:
                self.speed *= random.uniform(1.5, 3)
        elif self.behavior == 'rare':
            self.direction *= -1 if random.random() < 0.05 else 1
        elif self.behavior == 'shooting':
            self.speed *= 1.2

class NightSky(Widget):
    view_mode = StringProperty('ground')
    direction = StringProperty('east')
    sim_speed = NumericProperty(1.0)
    objects = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generate_objects()
        Clock.schedule_interval(self.update, 1/60)

    def generate_objects(self):
        types = ['plane'] * 30 + ['helicopter'] * 20 + ['satellite'] * 20 + ['meteor'] * 20 + ['rare'] * 10
        colors = {'plane': (1,0,0), 'helicopter': (0,0,1), 'satellite': (1,1,1), 'meteor': (1,1,0.5), 'rare': (0.5,0,1)}
        counts = {t: 0 for t in colors}
        for i in range(7):
            t = random.choice(types)
            if counts[t] < 4:
                counts[t] += 1
                self.objects.append(SkyObject(t, colors[t], i+1))

    def update(self, dt):
        self.canvas.clear()
        with self.canvas:
            # Stars
            Color(1,1,1)
            for _ in range(100):
                Ellipse(pos=(random.uniform(0, self.width), random.uniform(0, self.height)), size=(2,2))
            
            # City lights (bottom)
            Color(0.2,0.2,0.2)
            Line(points=[0,0, self.width,0], width=2)
            
            for obj in self.objects:
                obj.update(dt, self.sim_speed, self.view_mode, self.direction)
                shade = obj.altitude  # Lighter as lower
                Color(*[c * shade for c in obj.color])
                
                # Position scaling
                if self.view_mode == 'plan':
                    px, py = self.width/2 + obj.x * self.width/2, self.height/2 + obj.y * self.height/2
                else:
                    px, py = self.width/2 + obj.x * self.width/2 * obj.altitude, obj.y * self.height + (1 - obj.altitude) * self.height/2
                
                Ellipse(pos=(px-5, py-5), size=(10,10))
                
                # Trail
                if obj.trail:
                    points = [p for pt in obj.trail for p in (self.width/2 + pt[0]*self.width/2, self.height/2 + pt[1]*self.height/2)]
                    Line(points=points, width=1)
                
                # Number
                Color(1,1,1)
                # Simulate label
                # In real, add Label here, but for canvas, use texture if needed

class Controls(BoxLayout):
    def __init__(self, sky, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, 0.2)
        
        view_btn = ToggleButton(text='Plan/Ground', on_press=lambda x: setattr(sky, 'view_mode', 'plan' if sky.view_mode == 'ground' else 'ground'))
        dir_btn = ToggleButton(text='East/West', on_press=lambda x: setattr(sky, 'direction', 'east' if sky.direction == 'west' else 'west'))
        speed_slider = Slider(min=0.1, max=5, value=1, on_value=lambda x,v: setattr(sky, 'sim_speed', v))
        
        self.add_widget(view_btn)
        self.add_widget(dir_btn)
        self.add_widget(speed_slider)

class SkyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        sky = NightSky()
        controls = Controls(sky)
        layout.add_widget(sky)
        layout.add_widget(controls)
        return layout

if __name__ == '__main__':
    SkyApp().run()