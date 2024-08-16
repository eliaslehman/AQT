class ReverseKerrTWPAGeometry:
    def __init__(self, chip_height, chip_width, margin, launchpads, 
                 line_gap, line_width, cell_width, delay_length, 
                 num_paths):
        # Substrate parameters
        self.chip_height = chip_height
        self.chip_width = chip_width
        self.margin = margin

        # Launchpads is a list of coordinates
        self.launchpads = launchpads

        self.line_gap = line_gap
        self.line_width = line_width
        self.cell_width = cell_width

        self.turn_radius = line_gap/2
        self.delay_length = delay_length
        self.num_paths = num_paths

        self.total_devices = 0
        # Additional attributes for visualization
        self.fig, self.ax = plt.subplots(figsize=(30,30))

    def plot_geometry(self):
        # Plot chip boundary
        chip_boundary = plt.Rectangle((0, 0), self.chip_height, self.chip_width, linewidth=1, edgecolor='black',
                                     facecolor='none')
        self.ax.add_patch(chip_boundary)

        # Plot device region
        device_region = plt.Rectangle((self.margin, self.margin),
                                      self.chip_width - 2 * self.margin, self.chip_width - 2 * self.margin,
                                      linewidth=0.5, edgecolor='blue', facecolor='none')
        self.ax.add_patch(device_region)

        # Plot launchpads
        self.draw_launchpad(self.launchpads[0])
        self.draw_launchpad(self.launchpads[1], flip=True)

        # Plot waveguide
        self.plot_devices()

        # Customize as needed
        self.ax.set_xlim(-1, self.chip_height)
        self.ax.set_ylim(-1, self.chip_width)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    def draw_launchpad(self, launchpad, flip=False):
        # Customize launchpad shape and size
        if flip:
            launchpad_shape = plt.Polygon([(launchpad[0] - self.margin, launchpad[1]),
                                           (launchpad[0], launchpad[1] + self.margin),
                                           (launchpad[0], launchpad[1] - self.margin)],
                                          edgecolor='green', facecolor='none', linewidth=1)
        else:
            launchpad_shape = plt.Polygon([(launchpad[0], launchpad[1] - self.margin),
                                           (launchpad[0] + self.margin, launchpad[1]),
                                           (launchpad[0], launchpad[1] + self.margin)],
                                          edgecolor='green', facecolor='none', linewidth=1)
        self.ax.add_patch(launchpad_shape)

    def plot_devices(self):
        # Plot the waveguide in a snaking fashion
        waveguide_start = np.array([self.launchpads[0][0] + self.margin, self.launchpads[0][1]])
        waveguide_end = np.array([self.launchpads[1][0] - self.margin, self.launchpads[1][1]])

        N_delay_cells_left = int(self.delay_length / self.cell_width)
        for delay_cell in range(N_delay_cells_left):
            #Left Delay
            x_pos = waveguide_start[0] + self.cell_width * delay_cell
            y_pos = waveguide_start[1]
            self.draw_waveguide_unit_cell(self.cell_width, x_pos, y_pos)

        waveguide_start = x_pos + self.cell_width, y_pos

        # Function to add linear and curved paths with embedded devices
        def add_paths(start, paths):
            for path in paths:
                waveguide_start = self.plot_curved_path(start, path[0], reverse=path[1], qrt=path[2])
                start = self.plot_linear_path(waveguide_start, path[3], path[4])

            N_delay_cells_right = int((waveguide_end[0]-start[0]) / self.cell_width)
            for delay_cell in range(N_delay_cells_right):
                #Right Delay
                x_pos = waveguide_end[0] - self.cell_width * delay_cell
                y_pos = waveguide_end[1]
                self.draw_waveguide_unit_cell(self.cell_width, x_pos, y_pos)

        def generate_paths(N):
            paths = [(np.pi/2, False, True, self.chip_height/2-self.margin-2*self.turn_radius-self.cell_width, np.pi/2)]

            # Add repeated entries
            for _ in range(N):  # Adjust the range based on the number of repeated entries
               paths.append((np.pi, True if _%2 else False, False, self.chip_height-2*self.margin-2*self.turn_radius, np.pi/2 if _%2 else -np.pi/2))

            # Half-length line
            paths.append(
                ((np.pi, True, False, self.chip_height/2-self.margin-2*self.turn_radius, np.pi/2) if N%2 
                else (np.pi, False, False, self.chip_height/2-self.margin-2*self.turn_radius, -np.pi/2))
            )

            #Qrt curve
            paths.append(
                (np.pi/2, True, True, 0, np.pi/2)
            )

            return paths

        paths = generate_paths(self.num_paths)#int((self.chip_width - 2*self.margin - 2*self.delay_length) / (self.line_width+self.line_gap)))
        # Add the paths with embedded devices
        add_paths(waveguide_start, paths)


    def plot_curved_path(self, start, max_angle, reverse=False, qrt=False):
        N_curve_cells = int(self.turn_radius * max_angle / self.cell_width)
        curved_paths = np.linspace(0, max_angle, N_curve_cells)

        for angle in curved_paths:
            x_pos, y_pos = self.calculate_position(start, angle, reverse, qrt)
            self.draw_waveguide_unit_cell(self.cell_width, x_pos, y_pos, reverse, angle)

        return x_pos, y_pos


    def plot_linear_path(self, start, length, angle):
        N_lin_cells = int(length / self.cell_width)

        x_pos = start[0]
        y_pos = start[1]

        for lin_cell in range(N_lin_cells):
            x_pos = start[0]
            y_pos = start[1] + self.cell_width * (2 * angle / np.pi) * lin_cell
            self.total_devices+=1
            self.draw_waveguide_unit_cell(self.cell_width, x_pos, y_pos, angle)

        return x_pos, y_pos
    
    def calculate_position(self, start, angle, reverse, qrt):
        if reverse:
            x_pos = start[0] - (np.cos(angle) - 1) * self.turn_radius
            y_pos = start[1] - np.sin(angle) * self.turn_radius
        elif qrt:
            x_pos = start[0] + np.sin(angle) * self.turn_radius
            y_pos = start[1] - (np.cos(angle) - 1) * self.turn_radius
        else:
            x_pos = start[0] - (np.cos(angle) - 1) * self.turn_radius
            y_pos = start[1] + np.sin(angle) * self.turn_radius

        return x_pos, y_pos

    def draw_waveguide_unit_cell(self, length, x_pos, y_pos, reverse=False, angle=np.pi/2):
        # Draw a unit cell of the waveguide
        unit_cell = plt.Rectangle((x_pos, y_pos), length, self.line_width, angle=np.degrees(angle if reverse else -angle),
                                  linewidth=0.2, edgecolor='white', facecolor='black')
        self.ax.add_patch(unit_cell)
        # self.total_devices += 1