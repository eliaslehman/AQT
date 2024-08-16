import gdsfactory as gf
from .trace import Trace
import qnlmodels.cpw as CPW
import qnlmodels.klopfenstein_taper as kt

class Launch:
    def __init__(self, cpw : Trace, port = "in_w", pad_width=250, line_spacing=10, pad_height=250, taper_length=250, angle=None, substrate_thickness=675, substrate_permitivity=11.7):
        self.cpw = cpw
        self.port = port
        self.pad_width = pad_width
        self.pad_height = pad_height
        self.line_spacing = line_spacing
        self.taper_length = taper_length
        self.angle = angle
        self.substrate_thickness = substrate_thickness
        self.substrate_permitivity = substrate_permitivity

    # @gf.cell
    def make(self):
        lp = gf.Component()

        section = []
        section.append(gf.Section(width=self.cpw.make().ports[self.port].dwidth, offset=0, layer=(1, 0), name = f'line_w', port_names=(f'in_w', f'out_w')))
        outgoing_cross_section = gf.CrossSection(sections = section)

        launch_pad_cross_section = Trace(spacing=self.line_spacing, width=self.pad_height).get_cross_section()
        transition = lp << gf.components.taper_cross_section(cross_section1=outgoing_cross_section, 
                                                        cross_section2=launch_pad_cross_section,
                                                        length=self.taper_length, 
                                                        linear=False,
                                                        width_type="sine")
        transition.connect("in_w", self.cpw.make().ports[self.port])
        # pad = lp << gf.path.extrude(gf.path.arc(radius=self.pad_width/2+self.line_spacing, angle=180), layer=(2,0), width=self.line_spacing)
        # pad.connect("o1", transition.ports["out_w"])
        # pad.movey(self.pad_width/2)
        
        if self.angle:
            transition.rotate(self.angle)
            # pad.rotate(self.angle)
        return lp

    def draw(self):
        return self.make().show()