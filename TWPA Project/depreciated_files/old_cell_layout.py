class UnitCellLayout:
    def __init__(self, cell_height, cell_width,
                 jj_width, jj_height, I0_ratio, 
                 bottom_margin, relative_permitivity, 
                 chip_separation, jj_seperation, J0):
        self.cell_height = cell_height
        self.cell_width = cell_width
        self.jj_width = jj_width
        self.jj_height = jj_height
        self.I0_ratio = I0_ratio
        self.bottom_margin = bottom_margin
        self.relative_permitivity = relative_permitivity
        self.chip_separation = chip_separation #nm
        self.jj_seperation = jj_seperation
        self.J0 = J0

        self.cell_area = 0

    def draw_layout(self, ax, x_offset=0, alt=0):
        # Draw cell frame
        cell_frame_left = plt.Rectangle((x_offset - self.cell_width/2 , -self.cell_height/2), self.cell_width / 2 - 1.5 * self.jj_width - self.bottom_margin, self.cell_height, linewidth=0.5, edgecolor='black', facecolor='grey')
        ax.add_patch(cell_frame_left)

        cell_frame_right = plt.Rectangle((x_offset +  1.5 * self.jj_width+ self.bottom_margin, -self.cell_height/2), self.cell_width / 2 - 1.5 * self.jj_width - self.bottom_margin, self.cell_height, linewidth=0.5, edgecolor='black', facecolor='grey')
        ax.add_patch(cell_frame_right)

        large_junction_frame = plt.Rectangle((x_offset - 1.5 * self.jj_width - self.bottom_margin, (-1)**alt * (self.cell_height / 2 - self.jj_height)), 3 * self.jj_width + 2 * self.bottom_margin, (-1)**alt * self.jj_height, linewidth=0.5, edgecolor='black', facecolor='grey')
        ax.add_patch(large_junction_frame)

        small_junction_frame = plt.Rectangle((x_offset - 1.5 * self.jj_width - self.bottom_margin, (-1)**alt * (- self.cell_height / 2)), 3 * self.jj_width + 2 * self.bottom_margin, (-1)**alt * self.jj_height * self.I0_ratio, linewidth=0.5, edgecolor='black', facecolor='grey')
        ax.add_patch(small_junction_frame)

        # Draw small junction on bottom 
        small_junc = plt.Rectangle((x_offset - self.jj_width / 2, (-1)**alt * - 2*self.cell_height / 2), self.jj_width, (-1)**alt * self.jj_height * self.I0_ratio, linewidth=0.5, edgecolor='black', facecolor='orange')
        ax.add_patch(small_junc)

        # Draw three large junctions on top 
        for i in range(-1, 2):
            large_junc = plt.Rectangle((x_offset - self.jj_width / 2 + (self.jj_width + self.bottom_margin) * i, (-1)**alt * (self.cell_height / 2 - self.jj_height)), self.jj_width, (-1)**alt * self.jj_height, linewidth=0.5, edgecolor='black', facecolor='blue')
            ax.add_patch(large_junc)


        for frame in [cell_frame_left, cell_frame_right, large_junction_frame, small_junction_frame]:
            self.cell_area += abs(frame.get_width()*frame.get_height())

        return ax

    def draw_row(self, N):
        fig, ax = plt.subplots(figsize=(10,5))
        
        for i in range(N):
            x_offset = i * self.cell_width
            self.draw_layout(ax, x_offset, alt=i%2)

        plt.xlim(-self.cell_width/2 * 1.1, self.cell_width * N)
        plt.ylim(-self.cell_height/2 * 1.1, self.cell_height/2 * 1.1)
        # plt.gca().set_aspect('fixed', adjustable='box')
        plt.xlabel('Width (um)')
        plt.ylabel('Height (um)')
        plt.title(f'Device Layout ({N} Cells)')
        plt.grid(True)
        plt.show()

    def calculate_Cg(self):
        print(f"cell area = {self.cell_area}")
        return e0 * self.relative_permitivity * self.cell_area*1e-12 / (self.chip_separation*1e-9)
    
    def calculate_Cj(self):
        return e0 * self.relative_permitivity * (self.jj_height*1e-6) * (self.jj_width*1e-6) / (self.jj_seperation*1e-9)
    
    def calculate_I0(self):
        return self.J0 * self.jj_height * self.jj_width