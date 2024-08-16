import gdsfactory as gf
from gdsfactory.cross_section import ComponentAlongPath
import numpy as np


class EmbeddedSnail:
        def __init__(self, cell_height, cell_width, r,
                    junction_width, junction_height, snail_gap_height,
                    finger_pad, finger_gap, finger_width,
                    snail_cap_width, snail_cap_height, snail_cap_lead_width):
            
            self.cell_height = cell_height
            self.cell_width = cell_width
            self.r = r
            self.junction_width = junction_width
            self.junction_height = junction_height
            self.snail_gap_height = snail_gap_height
            self.finger_length = cell_height/2 - snail_gap_height/2 - snail_cap_width/2 - 1.5*finger_pad
            self.finger_width = finger_width
            self.finger_pad = finger_pad
            self.finger_gap = finger_gap
            self.snail_cap_width = snail_cap_width
            self.snail_cap_height = snail_cap_height
            self.snail_cap_lead_width = snail_cap_lead_width
            self.long_finger_length = cell_height/2-snail_gap_height/2
            self.snail_cap_lead_length = cell_height/2-snail_gap_height/2-snail_cap_height/2

        @gf.cell
        def unit_cell(self, alt=0):
            # Draw cell frame
            frame = gf.components.rectangle(size=(self.cell_height/2, self.cell_width/2), layer=(2, 0))
            finger_crosssection = gf.CrossSection(sections=[gf.Section(width=self.finger_width, offset=0, layer=(1, 0), port_names=("in", "out"))])
            long_fingers = gf.components.straight_array(n=3, spacing=self.finger_gap+2*self.finger_pad, length=self.long_finger_length, cross_section=finger_crosssection)
            short_finger = gf.components.straight(length=self.finger_length, cross_section=finger_crosssection)
            fingers = gf.Component()
            fingers.add_ref(long_fingers).dmovex(-self.finger_pad)
            fingers.add_ref(short_finger).dmove((-self.finger_pad,3*(self.finger_width+self.finger_gap+2*self.finger_pad)))

            cap_pad_stem_crosssection = gf.CrossSection(sections=[gf.Section(width=self.snail_cap_lead_width, offset=0, layer=(1, 0), port_names=("in", "out"))])
            cap_pad_stem = gf.components.straight(length=self.snail_cap_lead_length, cross_section=cap_pad_stem_crosssection)
            cap_pad_top = gf.components.triangle(x=self.snail_cap_width/2, xtop=self.snail_cap_lead_width/2, y=self.snail_cap_height/2, ybot=self.finger_width, layer=(1,0))
            cap_pad = gf.Component()
            cap_pad.add_ref(cap_pad_stem).dmove((-self.finger_pad, self.cell_width/2))
            cap_pad.add_ref(cap_pad_top).mirror_y().drotate(-90).dmove((self.cell_height/2-self.snail_gap_height/2-self.finger_gap, self.cell_width/2))

            finger_gaps = gf.kdb.Region(fingers.get_polygons()[1]).sized(self.finger_pad*1e3) #in nm
            cap_pad_gap = gf.kdb.Region(cap_pad.get_polygons()[1]).sized(self.finger_pad*1e3)
            junctions_gap = gf.components.rectangle(size=(self.snail_gap_height, 5*self.junction_width))

            gaps = gf.Component()
            gaps.add_polygon(finger_gaps, (1,0))
            gaps.add_polygon(cap_pad_gap, (1,0))
            gaps.add_ref(junctions_gap).dmove((self.cell_height/2-self.snail_gap_height/2, self.cell_width/2-2.5*self.junction_width))
            subtract_gaps = gf.boolean(A=frame, B=gaps, operation="not", layer1=(2, 0), layer2=(1, 0), layer=(1, 0))

            IDC = gf.Component()
            IDC.add_ref(subtract_gaps)
            # IDC.add_ref(fingers)
            # IDC.add_ref(cap_pad)

            large_junction_spacing = gf.components.rectangle(size=(self.junction_height, self.junction_width))
            small_junction_spacing = gf.components.rectangle(size=(self.r*self.junction_height, 2*self.junction_width))

            junction_spacings = gf.Component()
            if alt:
                junction_spacings.add_ref(large_junction_spacing).dmove((self.snail_gap_height-self.junction_height, -3/2*(self.junction_width)))
                junction_spacings.add_ref(small_junction_spacing).dmove((0, -5/2*(self.junction_width)))
            else:
                junction_spacings.add_ref(large_junction_spacing).dmove((0, -3/2*(self.junction_width)))
                junction_spacings.add_ref(small_junction_spacing).dmove((self.snail_gap_height-self.r*self.junction_height, -5/2*(self.junction_width)))

            cell = gf.Component()
            cell.add_ref(IDC)
            cell.add_ref(IDC).mirror_x().dmovex(self.cell_height)
            cell.add_ref(IDC).mirror_y().dmovey(self.cell_width)
            cell.add_ref(IDC).mirror_y().mirror_x().dmove((self.cell_height, self.cell_width))
            cell.add_ref(junction_spacings).dmove((self.cell_height/2-self.snail_gap_height/2, self.cell_width/2))
            cell.add_ref(junction_spacings).mirror_y().dmove((self.cell_height/2-self.snail_gap_height/2, self.cell_width/2))

            cell.add_port(name="in", center=[self.cell_height/2, self.cell_width], width=self.snail_gap_height, orientation=-90, layer=(1,0))
            cell.add_port(name="out", center=[self.cell_height/2, 0], width=self.snail_gap_height, orientation=90, layer=(1,0))

            return cell

        def draw_cell(self, alt=0):
            self.unit_cell(alt).show()

        # Always alternate cells
        def alt_cells(self):
            alt_cells = gf.Component()
            cell = alt_cells << self.unit_cell()
            reflected_cell = alt_cells << self.unit_cell(1)
            cell.connect("out", reflected_cell.ports["in"])
            alt_cells.add_port(name="in", center=[self.cell_height/2, 2*self.cell_width], width=self.snail_gap_height, orientation=90, layer=(1,0))
            alt_cells.add_port(name="out", center=[self.cell_height/2, 0], width=self.snail_gap_height, orientation=-90, layer=(1,0))
            return alt_cells

        def draw_alternate_cells(self):
            self.alt_cells().show()

        def chain_cells(self, N):
            """Chain cells together in a line. Alternate cells to surpress 3-wave mixing."""
            chain = gf.Component()
            chain.add_ref(gf.components.array(self.alt_cells(), columns = 1, rows = N/2, spacing = (0, 2*self.cell_width,), add_ports=True))
            chain.add_port(name="in", center=[self.cell_height/2, N*self.cell_width], width=self.snail_gap_height, orientation=90, layer=(1,0))
            chain.add_port(name="out", center=[self.cell_height/2, 0], width=self.snail_gap_height, orientation=-90, layer=(1,0))
            return chain

        def draw_chain(self, N):
            self.chain_cells(N).show()

        def bend_cells(self):
            """Chain alternating cells in a 180 degree bend"""
            path = gf.path.straight() + gf.path.arc(40, angle=180) + gf.path.straight()
            cells = ComponentAlongPath(component = self.unit_cell(), spacing = (2.4*self.cell_width))
            alt_cells = ComponentAlongPath(component = self.unit_cell(alt=1), spacing = (2.4*self.cell_width), padding=self.cell_width)
            x = gf.CrossSection(components_along_path=[cells, alt_cells])
            bend = gf.path.extrude(path, cross_section=x)
            return bend

        def draw_bend(self):
            self.bend_cells().show()