import gdsfactory as gf
from gdsfactory.cross_section import ComponentAlongPath
import numpy as np
from ..qnlfactory.layermap import QFaBLayers
layers = QFaBLayers

class EmbeddedSnail: # Dims in um
        def __init__(self, 
                     cell_height: float = 190, 
                     cell_width: float = 240, 
                     junction_ratio: float = 0.1,
                     dolan_bridge_size: tuple = (2, 0.6), 
                     snail_bridge_spacing: float = 3,
                     bandaid_size: tuple = (4,4),
                     snail_gap_size: tuple = (70, 10),
                     finger_pad: float = 3, 
                     finger_separation: float = 14, 
                     finger_width: float = 6,
                     snail_cap_width: float = 25, 
                     snail_cap_height: float = 5, 
                     snail_cap_lead_width: float = 8.33, 
                     channel_width: float = 55):
            
            self.cell_height = cell_height
            self.cell_width = cell_width
            self.r = junction_ratio
            self.dolan_bridge_width = dolan_bridge_size[0]
            self.dolan_bridge_height = dolan_bridge_size[1]
            self.snail_bridge_spacing = snail_bridge_spacing
            self.bandaid_size = bandaid_size
            self.snail_gap_width = snail_gap_size[0]
            self.snail_gap_height = snail_gap_size[1]
            self.finger_length = cell_height/2 - snail_gap_size[0]/2 - (1+np.sqrt(2))*snail_cap_height/2 - (1+np.sqrt(2))*finger_pad
            self.finger_width = finger_width
            self.finger_pad = finger_pad
            self.finger_separation = finger_separation
            self.snail_cap_width = snail_cap_width
            self.snail_cap_height = snail_cap_height
            self.snail_cap_lead_width = snail_cap_lead_width
            self.long_finger_length = cell_width/2-finger_pad-channel_width
            self.snail_cap_lead_length = cell_width/2-snail_gap_size[0]/2-finger_pad
            self.channel_width = channel_width

        @gf.cell
        def unit_cell(self, alt=0):
            # Draw cell frame
            frame = gf.components.rectangle(size=(self.cell_width/2, self.cell_height/2), layer=layers.SC1_E)
            finger_crosssection = gf.CrossSection(sections=[gf.Section(width=self.finger_width, offset=0, layer=layers.SC1, port_names=("in", "out"), port_types=('electrical','electrical'))])
            outer_fingers = gf.components.straight_array(n=2, spacing=self.finger_separation+self.finger_pad, length=self.long_finger_length, cross_section=finger_crosssection)
            inner_finger = gf.components.straight(length=self.finger_length, cross_section=finger_crosssection)
            fingers = gf.Component()
            fingers.add_ref(outer_fingers).dmove((-self.finger_pad, self.cell_height/2 - self.snail_cap_lead_width/2-3*(self.finger_pad+self.finger_separation+self.finger_pad)-2*self.finger_width))
            fingers.add_ref(inner_finger).dmove((-self.finger_pad, self.cell_height/2 - self.snail_cap_lead_width/2-3*self.finger_pad-self.finger_separation))

            cap_pad_stem_crosssection = gf.CrossSection(sections=[gf.Section(width=self.snail_cap_lead_width, offset=0, layer=layers.SC1, port_names=("in", "out"), port_types=('electrical','electrical'))]) 
            cap_pad_stem = gf.components.straight(length=self.snail_cap_lead_length, cross_section=cap_pad_stem_crosssection)
            cap_pad_top = gf.components.triangle(x=self.snail_cap_width/2, xtop=self.snail_cap_lead_width/2, y=self.snail_cap_width/2, ybot=self.snail_cap_height, layer=layers.SC1)            
            cap_pad = gf.Component()
            cap_pad.add_ref(cap_pad_stem).dmove((-self.finger_pad, self.cell_height/2))
            cap_pad.add_ref(cap_pad_top).mirror_y().drotate(-90).dmove((self.snail_cap_lead_length, self.cell_height/2))

            finger_separations = gf.kdb.Region(fingers.get_polygons()[1]).sized(self.finger_pad*1e3) #in nm
            cap_pad_gap = gf.kdb.Region(cap_pad.get_polygons()[1]).sized(self.finger_pad*1e3)
            junctions_gap = gf.components.rectangle(size=(self.snail_gap_width, self.snail_gap_height))

            gaps = gf.Component()
            gaps.add_polygon(finger_separations, layers.SC1)
            gaps.add_polygon(cap_pad_gap, layers.SC1)
            gaps.add_ref(junctions_gap).dmove(((self.cell_width-self.snail_gap_width)/2, (self.cell_height-self.snail_gap_height)/2))
            subtract_gaps = gf.boolean(A=frame, B=gaps, operation="not", layer1=layers.SC1_E, layer2=layers.SC1, layer=layers.SC1)

            IDC = gf.Component()
            IDC.add_ref(subtract_gaps)
            # IDC.add_ref(fingers)
            # IDC.add_ref(cap_pad)

            large_dolan_bridge = gf.components.rectangle(size=(self.dolan_bridge_width, self.dolan_bridge_height), layer=layers.JJ1_UC)
            large_bridge_inner_spacing = gf.components.rectangle(size=(self.dolan_bridge_width, self.snail_bridge_spacing), layer=layers.JJ1)
            
            large_bridge_outer_spacing = gf.components.rectangle(size=(self.dolan_bridge_width, (self.snail_gap_height-self.snail_bridge_spacing)/2-self.dolan_bridge_height), layer=layers.JJ1)

            small_dolan_bridge = gf.components.rectangle(size=(self.r*self.dolan_bridge_width, self.dolan_bridge_height), layer=layers.JJ1_UC)
            small_bridge_outer_spacing = gf.components.rectangle(size=(self.r*self.dolan_bridge_width, (self.snail_gap_height-self.dolan_bridge_height)/2), layer=layers.JJ1)

            junction_bandaid = gf.components.rectangle(size=self.bandaid_size, layer=layers.JJ1_BD)

            junction_fab = gf.Component()

            if alt:
                junction_fab.add_ref(large_dolan_bridge).dmove((self.snail_gap_width-self.dolan_bridge_width, -(self.snail_bridge_spacing/2+self.dolan_bridge_height)))
                junction_fab.add_ref(large_bridge_inner_spacing).dmove((self.snail_gap_width-self.dolan_bridge_width, -self.snail_bridge_spacing/2))
                junction_fab.add_ref(large_bridge_outer_spacing).dmove((self.snail_gap_width-self.dolan_bridge_width, -self.snail_gap_height/2))
                
                junction_fab.add_ref(small_dolan_bridge).dmove((0, -(self.dolan_bridge_height)/2))
                junction_fab.add_ref(small_bridge_outer_spacing).dmove((0, -self.snail_gap_height/2))

                junction_fab.add_ref(junction_bandaid).dmove((0,-(self.snail_gap_height/2+self.bandaid_size[1])))
                junction_fab.add_ref(junction_bandaid).dmove((self.snail_gap_width-self.bandaid_size[0],-(self.snail_gap_height/2+self.bandaid_size[1])))
                
            else:
                junction_fab.add_ref(large_dolan_bridge).dmove((0, -(self.snail_bridge_spacing/2+self.dolan_bridge_height)))
                junction_fab.add_ref(large_bridge_inner_spacing).dmove((0, -self.snail_bridge_spacing/2))
                junction_fab.add_ref(large_bridge_outer_spacing).dmove((0, -self.snail_gap_height/2))
                
                junction_fab.add_ref(small_dolan_bridge).dmove((self.snail_gap_width-self.r*self.dolan_bridge_width, -(self.dolan_bridge_height)/2))
                junction_fab.add_ref(small_bridge_outer_spacing).dmove((self.snail_gap_width-self.r*self.dolan_bridge_width, -self.snail_gap_height/2))
            
                junction_fab.add_ref(junction_bandaid).dmove((0,-(self.snail_gap_height/2+self.bandaid_size[1])))
                junction_fab.add_ref(junction_bandaid).dmove((self.snail_gap_width-self.bandaid_size[0],-(self.snail_gap_height/2+self.bandaid_size[1])))
                
            cell = gf.Component()
            cell.add_ref(IDC)
            cell.add_ref(IDC).mirror_x().dmovex(self.cell_width)
            cell.add_ref(IDC).mirror_y().dmovey(self.cell_height)
            cell.add_ref(IDC).mirror_y().mirror_x().dmove((self.cell_width, self.cell_height))
            cell.add_ref(junction_fab).dmove((self.cell_width/2-self.snail_gap_width/2, self.cell_height/2))
            cell.add_ref(junction_fab).mirror_y().dmove((self.cell_width/2-self.snail_gap_width/2, self.cell_height/2))

            cell.add_port(name="in", center=[self.cell_width/2, self.cell_height], width=self.snail_gap_width, orientation=-90, layer=layers.SC1, port_type='electrical')
            cell.add_port(name="out", center=[self.cell_width/2, 0], width=self.snail_gap_width, orientation=90, layer=layers.SC1, port_type='electrical')

            return cell

        def draw_cell(self, alt=0):
            self.unit_cell(alt).show()

        # Always alternate cells
        def alt_cells(self):
            alt_cells = gf.Component()
            cell = alt_cells << self.unit_cell()
            reflected_cell = alt_cells << self.unit_cell(1)
            cell.connect("out", reflected_cell.ports["in"])
            alt_cells.add_port(name="in", center=[self.cell_width/2, 2*self.cell_height], width=self.snail_gap_width, orientation=90, layer=layers.SC1, port_type='electrical')
            alt_cells.add_port(name="out", center=[self.cell_width/2, 0], width=self.snail_gap_width, orientation=-90, layer=layers.SC1, port_type='electrical')
            return alt_cells

        def draw_alternate_cells(self):
            self.alt_cells().show()

        def chain_cells(self, N):
            """Chain cells together in a line. Alternate cells to surpress 3-wave mixing."""
            chain = gf.Component()
            chain.add_ref(gf.components.array(self.alt_cells(), columns = 1, rows = N/2, spacing = (0, 2*self.cell_height,), add_ports=True))
            chain.add_port(name="in", center=[self.cell_width/2, N*self.cell_height], width=self.snail_gap_width, orientation=90, layer=layers.SC1, port_type='electrical')
            chain.add_port(name="out", center=[self.cell_width/2, 0], width=self.snail_gap_width, orientation=-90, layer=layers.SC1, port_type='electrical')
            return chain

        def draw_chain(self, N):
            self.chain_cells(N).show()

        def bend_cells(self):
            """Chain alternating cells in a 180 degree bend"""
            path = gf.path.straight() + gf.path.arc(40, angle=180) + gf.path.straight()
            cells = ComponentAlongPath(component = self.unit_cell(), spacing = (2.4*self.cell_height))
            alt_cells = ComponentAlongPath(component = self.unit_cell(alt=1), spacing = (2.4*self.cell_height), padding=self.cell_height)
            x = gf.CrossSection(components_along_path=[cells, alt_cells])
            bend = gf.path.extrude(path, cross_section=x)
            return bend

        def draw_bend(self):
            self.bend_cells().show()