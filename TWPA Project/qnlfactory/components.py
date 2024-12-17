import numpy as np
import gdsfactory as gf
from gdsfactory.typings import LayerSpec
from gdsfactory.components import rectangle, triangle
from .trace import Trace
from .layermap import QFaBLayers
from .utils import round_to_even_float
import qnlmodels.cpw as CPW
import qnlmodels.klopfenstein_taper as kt

layermap = QFaBLayers


@gf.cell
def border(
    size: tuple[float, float] = (10_000, 10_000), width: float = 50, corner: float = 250, layer=None
):
    c = gf.Component()

    xsize, ysize = size
    corner = rectangle((corner, corner))

    c1 = c << corner
    c1.dmove((-xsize / 2, -ysize / 2))

    c2 = c << corner
    c2.mirror_x()
    c2.dmove((xsize / 2, -ysize / 2))

    c3 = c << corner
    c3.mirror_y()
    c3.dmove((-xsize / 2, ysize / 2))

    c4 = c << corner
    c4.mirror_x().mirror_y()
    c4.dmove((xsize / 2, ysize / 2))

    border = gf.boolean(
        rectangle((xsize, ysize), centered=True),
        rectangle((xsize - 2 * width, ysize - 2 * width), centered=True),
        "not"
    )

    border_ref = c << border

    return c


@gf.cell
def launch(connected_trace : Trace, 
            port: str = "in_w", 
            pad_width: float = 250, # launch_size[0]
            taper_length: float = 250,  # launch_size[1]
            angle: float = None, 
            substrate_thickness: float = 675, 
            substrate_permitivity: float = 11.7,
            transmission_impedance: float = 50):

    c = gf.Component()

    lp = gf.Component()

    launch_cross_section_mismatch = CPW.CPW(pad_width, pad_width/2, substrate_thickness, substrate_permitivity)
    matched_spacing = round_to_even_float(launch_cross_section_mismatch.solve_for_impedance(transmission_impedance,'s', bounds=(1e-3, 400)))
    launch_cross_section_matched = CPW.CPW(pad_width, matched_spacing, substrate_thickness, substrate_permitivity)
    outgoing_cross_section = connected_trace.get_cross_section()
    launch_pad_cross_section = Trace(width=launch_cross_section_matched.w, spacing=launch_cross_section_matched.s).get_cross_section()
    
    lp_body_ref = lp << gf.components.taper_cross_section(cross_section1=outgoing_cross_section, 
                                                    cross_section2=launch_pad_cross_section,
                                                    length=taper_length, 
                                                    linear=False,
                                                    width_type="sine")        
    lp_backing_ref = lp << rectangle((launch_cross_section_matched.w+2*launch_cross_section_matched.s, launch_cross_section_matched.s), layer=layermap.SC1_E)
    lp_body_ref.connect("in_w", connected_trace.make().ports[port])
    lp_backing_ref.connect("e2", lp_body_ref.ports["out_w"], allow_width_mismatch=True, allow_layer_mismatch=True)
    lp_ref = c << lp

    if angle:
        lp_ref.drotate(angle, connected_trace.make().ports[port])

    c.add_port(name="cpw_side", port=lp_body_ref.ports["in_w"])

    return c


@gf.cell
def solder_bump_array(
    # chip: gf.Component,
    cols: int = 10,
    rows: int = 10,
    spacing: tuple[float, float] = (200, 200),
    center_offset: tuple[float, float] = (0,0),
    centered: bool = False,
    bump_diameter: float=65,
    underbump_metal_width: float=100,
    top_chip: bool=False
):
    # cutouts = chip.extract(layers=[layermap.SC1, layermap.SC1_E, layermap.KEEPOUT])

    c = gf.Component()
    
    array_cell = gf.Component()
    underbump_ref = array_cell << gf.components.rectangle(
        size=(underbump_metal_width,underbump_metal_width), 
        layer=layermap.UBM2 if top_chip else layermap.UBM1,
        centered=True)
    
    liftoff_ref = array_cell << gf.components.circle(
        radius=bump_diameter/2,
        layer=layermap.IND2 if top_chip else layermap.IND1)    

    # liftoff_ref.dmove((-underbump_metal_width/2, -underbump_metal_width/2))
    array_ref = c.add_ref(array_cell, columns=cols, rows=rows, spacing=spacing)
    
    if centered:
        array_ref.dmove((-cols*(spacing[0])/2+underbump_metal_width/2, -rows*(spacing[1])/2+underbump_metal_width/2))
    
    array_ref.dmove((center_offset[0]-underbump_metal_width/2, center_offset[1]-underbump_metal_width/2))
    
    return c


@gf.cell
def solder_bump_array(
    # chip: gf.Component,
    cols: int = 10,
    rows: int = 10,
    spacing: tuple[float, float] = (200, 200),
    center_offset: tuple[float, float] = (0,0),
    centered: bool = False,
    bump_diameter: float=65,
    underbump_metal_width: float=100,
    top_chip: bool=False
):
    c = gf.Component()
    
    array_cell = gf.Component()
    underbump_ref = array_cell << gf.components.rectangle(
        size=(underbump_metal_width,underbump_metal_width), 
        layer=layermap.UBM2 if top_chip else layermap.UBM1,
        centered=True)
    
    liftoff_ref = array_cell << gf.components.circle(
        radius=bump_diameter/2,
        layer=layermap.IND2 if top_chip else layermap.IND1)    

    array_ref = c.add_ref(array_cell, columns=cols, rows=rows, spacing=spacing)
    
    if centered:
        array_ref.dmove((-(cols-1)/2*(spacing[0])+underbump_metal_width/2, -(rows-1)/2*(spacing[1])+underbump_metal_width/2))
        
    array_ref.dmove((center_offset[0]-underbump_metal_width/2, center_offset[1]-underbump_metal_width/2))
    
    return c


@gf.cell
def titanium_array(
    cols: int = 10,
    rows: int = 10,
    spacing: tuple[float, float] = (200, 200),
    center_offset: tuple[float, float] = (0,0),
    centered: bool = False,
    metal_width: float=100,
    top_chip: bool=False
):
    c = gf.Component()

    array_cell = gf.Component()
    underbump_ref = array_cell << gf.components.rectangle(
        size=(metal_width,metal_width), 
        layer=layermap.JJ2 if top_chip else layermap.JJ1,
        centered=True)
    
    array_ref = c.add_ref(array_cell, columns=cols, rows=rows, spacing=spacing)
    
    if centered:
        array_ref.dmove((-(cols-1)/2*(spacing[0])+metal_width/2, -(rows-1)/2*(spacing[1])+metal_width/2))
    
    array_ref.dmove((center_offset[0]-metal_width/2, center_offset[1]-metal_width/2))
    
    return c


@gf.cell
def flip_chip_alignment(
    size: tuple = (150,150),
    center_offset: tuple = (5_000, 5_000),
    shift: float = 0 #ccw shift
):
    c = gf.Component()

    x, y = center_offset
    marker = rectangle(size, layer=layermap.SC1_E)

    c1 = c << marker
    c1.mirror_x().mirror_y()
    c1.dmove((-x / 2 + shift, -y / 2))

    c2 = c << marker
    c2.mirror_y()
    c2.dmove((x / 2, -y / 2 + shift))

    c3 = c << marker
    c3.mirror_x()
    c3.dmove((-x / 2, y / 2 - shift))

    c4 = c << marker
    c4.dmove((x / 2 - shift, y / 2))

    return c


@gf.cell
def triangle_taper(length: float, 
                   large_width: float,
                   small_width: float,
                   layer: LayerSpec):

    c = gf.Component()
    taper_top_half = triangle(y=large_width/2, ybot=small_width/2, x=length, layer=layer)
    c.add_ref(taper_top_half)
    c.add_ref(taper_top_half).mirror_y()

    return c


@gf.cell
def snail_loop(frame_size: float = (30, 14),
               loop_size: tuple = (10,10),
               dolan_bridge_width: float = 0.2,
               large_bridge_height: tuple = 3,
               large_bridge_gap: float = 0.5,
               junction_ratio: float = 0.1,
               large_junction_taper_length: float = 0.5,
               small_junction_taper_length: float = 0.75,
               small_junction_lead_length: float = 2
               ):
    
    frame_height = frame_size[1]
    loop_height = loop_size[1]
    small_junction_height = junction_ratio*large_bridge_height
    branch_thickeness = (frame_height - loop_height)/2
    small_junction_cutout_width = small_junction_taper_length+small_junction_lead_length+dolan_bridge_width

    large_junctions = gf.Component()
    
    center_bridge_gap = rectangle((large_bridge_gap, large_bridge_height), centered=True, layer=layermap.JJ1)
    large_junctions.add_ref(center_bridge_gap)

    large_dolan_bridge = rectangle((dolan_bridge_width, large_bridge_height), layer=layermap.JJ1_UC, centered=True)
    large_junctions.add_ref(large_dolan_bridge).movex(-(large_bridge_gap+dolan_bridge_width)/2)
    large_junctions.add_ref(large_dolan_bridge).movex(-(large_bridge_gap+dolan_bridge_width)/2).mirror_x()
    
    outer_bridge_gap = rectangle((large_bridge_gap, large_bridge_height), centered=True, layer=layermap.JJ1)
    large_junctions.add_ref(outer_bridge_gap).movex(-(large_bridge_gap+dolan_bridge_width))
    large_junctions.add_ref(outer_bridge_gap).movex(-(large_bridge_gap+dolan_bridge_width)).mirror_x()

    large_junction_taper = triangle_taper(large_junction_taper_length, branch_thickeness, large_bridge_height, layer=layermap.JJ1)
    large_junctions.add_ref(large_junction_taper).movex(-(3*large_bridge_gap/2+dolan_bridge_width)-large_junction_taper_length)
    large_junctions.add_ref(large_junction_taper).movex(-(3*large_bridge_gap/2+dolan_bridge_width)-large_junction_taper_length).mirror_x()
    
    small_junction = gf.Component()
    
    small_junction_lead = rectangle((small_junction_lead_length, small_junction_height), centered=True, layer=layermap.JJ1)
    small_junction.add_ref(small_junction_lead).movex(small_junction_taper_length/2-dolan_bridge_width/2)

    small_junction_taper = triangle_taper(small_junction_taper_length, branch_thickeness, small_junction_height, layer=layermap.JJ1)
    small_junction.add_ref(small_junction_taper).movex(-(small_junction_taper_length+small_junction_lead_length+dolan_bridge_width)/2)
    
    c = gf.Component()

    small_junction_cutout = c << rectangle((small_junction_cutout_width, branch_thickeness), centered=True, layer=layermap.KEEPOUT)
    small_junction_cutout.dmovey((loop_height+branch_thickeness)/2)

    large_junctions_ref = c << large_junctions
    large_junctions_ref.dmovey(-(loop_height+branch_thickeness)/2)

    small_junction_ref = c << small_junction
    small_junction_ref.dmovey((loop_height+branch_thickeness)/2)

    frame = rectangle(frame_size, centered=True, layer=layermap.JJ1)
    loop = rectangle(loop_size, centered=True, layer=layermap.JJ1)
    frame_minus_large_junction = gf.boolean(A=frame, B=large_junctions_ref, operation='not', layer1=layermap.JJ1, layer2=layermap.JJ1_UC, layer=layermap.JJ1)
    frame_minus_all_junctions = gf.boolean(A=frame_minus_large_junction, B=small_junction_cutout, operation='not', layer1=layermap.JJ1, layer2=layermap.KEEPOUT, layer=layermap.JJ1)
    frame_loop = gf.boolean(frame_minus_all_junctions, loop, 'not', layer1=layermap.JJ1, layer2=layermap.JJ1, layer=layermap.JJ1)

    c << frame_loop
    c = c.extract(layers=[layermap.JJ1, layermap.JJ1_UC])
    return c


@gf.cell
def ground_idc(output_cpw_width: float,
    pad_size: tuple = (350, 100),
    finger_size: tuple = (40, 50),
    num_fingers: int = 4,
    finger_gap: float = 40,
    taper_length: float = 90,
    layer: LayerSpec=layermap.SC1):

    finger_width, finger_length = finger_size
    pad_width, pad_height = pad_size
    finger_spacing = finger_gap + finger_width

    c = gf.Component()

    pad = rectangle(pad_size,layer=layer, centered=True)
    pad_ref = c << pad

    fingers = gf.Component()
    finger = rectangle(finger_size, layer=layer)
    fingers_ref = fingers.add_ref(finger, columns=num_fingers, rows=2, spacing=(finger_spacing, pad_height+finger_length))
    fingers_ref.dmove((-(num_fingers/2*finger_width+(num_fingers-1)/2*(finger_gap)), -(pad_height/2+finger_length)))
    c << fingers

    taper = triangle_taper(length=taper_length, large_width=pad_height, small_width=output_cpw_width, layer=layer)
    taper_in_ref = c << taper
    taper_in_ref.mirror_x().dmovex(-pad_width/2)

    taper_out_ref = c << taper
    taper_out_ref.dmovex(pad_width/2)

    return c


@gf.cell
def twpa_cell(
    input_cpw_spacing: float,
    pad_size: tuple = (350, 100),
    finger_size: tuple = (40, 50),
    num_fingers: int = 4,
    finger_gap: float = 40,
    finger_padding: float = 4,
    taper_length: float = 100,
    snail_frame_size: tuple = (30, 14),
    loop_size: tuple = (10,10),
    dolan_bridge_width: float = 0.2,
    large_bridge_height: float = 3,
    large_bridge_gap: float = 0.5,
    junction_ratio: float = 0.1,
    large_junction_taper_length: float = 0.5,
    small_junction_taper_length: float = 0.75,
    small_junction_lead_length: float = 2,
    bandage_size: tuple=(20,15)):

    pad_width, pad_height = pad_size

    cell = gf.Component()

    idc = ground_idc(pad_size = pad_size,
                    finger_size = finger_size,
                    num_fingers = num_fingers,
                    finger_gap = finger_gap,
                    taper_length = taper_length,
                    output_cpw_width = snail_frame_size[1])

    idc_ref = cell << idc

    idc_etch_cutout = ground_idc(pad_size = (pad_size[0], pad_size[1]+2*finger_padding),
                                finger_size = (finger_size[0]+2*finger_padding, finger_size[1]),
                                num_fingers = num_fingers,
                                finger_gap = finger_gap-2*finger_padding,
                                taper_length = taper_length,
                                output_cpw_width = snail_frame_size[1]+2*input_cpw_spacing,
                                layer=layermap.SC1_E)

    idc_etch = gf.boolean(idc_etch_cutout, idc, 'not', layer1=layermap.SC1_E, layer2=layermap.SC1, layer=layermap.SC1_E)

    idc_etch_ref = cell << idc_etch

    snail = snail_loop( snail_frame_size,
                        loop_size,
                        dolan_bridge_width,
                        large_bridge_height,
                        large_bridge_gap,
                        junction_ratio,
                        large_junction_taper_length,
                        small_junction_taper_length,
                        small_junction_lead_length)
    
    snail_ref = cell << snail
    snail_ref.dmovex(-(pad_width/2+taper_length+snail_frame_size[0]/2))

    snail_etch = rectangle(size=(snail_frame_size[0], snail_frame_size[1]+2*input_cpw_spacing), centered=True, layer=layermap.SC1_E)
    snail_etch_ref = cell << snail_etch
    snail_etch_ref.dmovex(-(pad_width/2+taper_length+snail_frame_size[0]/2))

    bandage = rectangle(size=bandage_size, layer=layermap.JJ1_BD, centered=True, port_type='electrical')
    left_bandage_ref = cell << bandage
    left_bandage_ref.dmovex(-pad_width/2-taper_length)

    right_bandage_ref = cell << bandage
    right_bandage_ref.dmovex(-pad_width/2-taper_length-snail_frame_size[0])

    c = gf.Component()
    c << cell.extract(layers=[layermap.SC1, layermap.SC1_E, layermap.JJ1, layermap.JJ1_UC, layermap.JJ1_BD])
    
    c.add_port(name="input", center=(pad_size[0]/2+taper_length, 0), width=snail_frame_size[1],  orientation=0, port_type='electrical', layer=layermap.SC1)
    c.add_port(name="output", center=(-pad_size[0]/2-taper_length-snail_frame_size[0], 0), width=snail_frame_size[1], orientation=180, port_type='electrical', layer=layermap.SC1)
    return c