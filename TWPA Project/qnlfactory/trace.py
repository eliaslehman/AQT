import numpy as np
import gdsfactory as gf

class Trace():
    """Class for drawing wires along a input path
        Args: 
        line_wdith: 1xN array of widths for path segments
        num_lines: N lines for drawing CPW or other multiline comps
        start: init coordinate
        line_spacing: spacing outside the edge of the trace line
    """
    def __init__(self, width, spacing, start=(0, 0), width_func=None):
        self.path = gf.path.straight(length=0)
        self.line_width = width
        self.line_spacing = spacing
        self.start = start
        self.width_func = width_func
    
    def straight(self, length):
        """Adds a straight portion to this Trace's path.
        
        Args:
            length (float): length of straight path in micron.
        """
        self.path += gf.path.straight(length)
        return self

    def turn(self, radius, angle):
        """Adds a turn to this Trace's path.
        
        Args:
            radius (float): turn radius of turn in micron.
            angle (float): turn angle in degrees.
        """
        self.path += gf.path.arc(radius=radius, angle=angle)
        return self
    
    def half_segment(
            self, 
            length, 
            radius):
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
        num_segments,
        length,
        radius,
        turn=1,
        extra_turns='both',
        length_type='segment',
    ):
        """Draws a meandering section that begins with a straight segment.

        Args:
            num_segments (int): The number of straight segments to include
            length (float): The length of the straight segments or the total
                length, depending on the value of `length_type`.
            radius (float): The radius of the turn.
            turn (int): The direction of the first turn is given by `pi * turn`
            length_type (str): Specifies whether `length` is the segment
                length or the total length of the meander.
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
            section.append(gf.Section(width=0, width_function=self.width_func, offset=0, layer=(1, 0), name = 'line_w', port_names=('in_w', 'out_w')))
        else:
            section.append(gf.Section(width=self.line_width, offset=0, layer=(1, 0), name = 'line_w', port_names=('in_w', 'out_w')))
            # section.append(gf.Section(width=self.line_width+2*self.line_spacing, offset=0, layer=(2, 0), name = f'line_s', port_names=(f'in_s', f'out_s')))
        return gf.CrossSection(sections = section)

    def make(self):
        """Function to extrude Trace sections (wires) onto Trace path."""
        trace = self.get_cross_section()
        return gf.path.extrude(self.path, cross_section = trace)
    
    def append(self, path):
        self.path += path
    
    def draw(self):
        return self.make().show()