import numpy as np
import gdsfactory as gf
from .layermap import QFaBLayers
from .utils import round_to_even_float
layermap = QFaBLayers

class Trace():
    """Class for drawing wires along a input path
        Args: 
        line_width: 1xN array of widths for path segments
        start: init coordinate
        width_func: for smooth tapering
    """
    def __init__(self, 
                 width: float = 10, 
                 spacing: float = 6,
                 start: tuple = (0, 0),
                 width_func=None):
        
        self.path = gf.path.straight(length=0)
        self.line_width = round_to_even_float(width)
        self.line_spacing = round_to_even_float(spacing)
        self.start = start
        self.width_func = width_func
    
    def straight(self, length:float=100):
        """Adds a straight portion to this Trace's path.
        
        Args:
            length (float): length of straight path in micron.
        """
        self.path += gf.path.straight(length)
        return self

    def turn(self, radius:float, angle:float):
        """Adds a turn to this Trace's path.
        
        Args:
            radius (float): turn radius of turn in micron.
            angle (float): turn angle in degrees.
        """
        self.path += gf.path.arc(radius=radius, angle=angle)
        return self
    
    def half_segment(
            self, 
            length:float, 
            radius:float):
        """Half a meander segment in length, followed by a quarter turn.
        
        Args:
            length (float): length of the half segment.
            radius (float): radius of the quarter turn.add()
        """
        self.turn(radius=radius, angle=-90)
        self.straight(length/2)

        return self

    def meander(
        self,
        num_segments: int,
        length: float,
        radius: float,
        turn:int=1,
        extra_turns:str='both',
        length_type:str='segment',
    ):
        """Draws a meandering section that begins with a straight segment.

        Args:
            num_segments (int): The number of straight segments to include
            length (float): The length of the straight segments or the total
                length, depending on the value of `length_type`.
            radius (float): The radius of the turn.
            turn (int): The direction of the first turn is given by `pi * turn`. Must be `-1` or `1` (turn down or up, respectively).
            length_type (str): Specifies whether `length` is the segment
                length (`segment`) or the total length of the meander (!`segment`).
            extra_turns (str): A keyword that specifies whether to add an extra 
                at the start of the meander, the end of the meander, or both. 
                Valid keywords are `start`, `end`, `both`.
        Returns:
            Path: This `Path` object.
        """

        if length_type == 'segment':
            segment_length = length
        else:
            total_length = length
            turn_length = (num_segments - 1) * np.pi * radius
            
            if extra_turns in ['start', 'end', 'both']:
                turn_length += {'start': 1, 'end': 1, 'both': 2}[extra_turns] * np.pi * radius
            
            segment_length = (total_length - turn_length) / num_segments
        
        assert turn in [-1, 1], 'Turn must be +/- 1'

        if extra_turns in ['start', 'both']:
            self.turn(radius, 180*turn)
            turn = -1*np.sign(turn)

        for _ in range(num_segments - 1):
            self.straight(segment_length)
            self.turn(radius, 180*turn)

            turn = -1*np.sign(turn)

        self.straight(segment_length)

        if extra_turns in ['end', 'both']:
            self.turn(radius, 180*turn)

        return self

    def get_cross_section(self):
        section = []
        if self.width_func:
            section.append(gf.Section(width=0, width_function=self.width_func, offset=0, layer=(1, 0), name = 'line_w', port_names=('in_w', 'out_w'), port_types=('electrical','electrical')))
        else:
            section.append(gf.Section(width=self.line_width, layer=layermap.SC1, name = 'line_w', port_names=('in_w', 'out_w'), port_types=('electrical','electrical')))
            section.append(gf.Section(width=self.line_spacing, offset=(self.line_spacing+self.line_width)/2, layer=layermap.SC1_E, name = 'line_s_top', port_names=('in_s_t', 'out_s_t'), port_types=('electrical','electrical')))
            section.append(gf.Section(width=self.line_spacing, offset=-(self.line_spacing+self.line_width)/2, layer=layermap.SC1_E, name = 'line_s_bot', port_names=('in_s_b', 'out_s_b'), port_types=('electrical','electrical')))
        return gf.CrossSection(sections = section)

    def make(self):
        """Function to extrude Trace sections (wires) onto Trace path."""
        trace = self.get_cross_section()
        return gf.path.extrude(self.path, cross_section = trace)
    
    def append(self, path):
        self.path += path
    
    def draw(self):
        return self.make().show()